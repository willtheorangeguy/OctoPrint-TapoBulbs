# coding=utf-8
"""Control Tapo Matter bulbs through Home Assistant from OctoPrint."""

from __future__ import absolute_import, unicode_literals

import contextlib
import threading

import flask
import octoprint.plugin
from octoprint.access import ADMIN_GROUP, USER_GROUP
from octoprint.access.permissions import Permissions
from octoprint.events import Events
from octoprint.util import RepeatedTimer

from .automation import PrintLightController
from .ha_client import HomeAssistantClient, HomeAssistantError, validate_light_entity

__plugin_name__ = "Tapo Bulbs"
__plugin_pythoncompat__ = ">=3.7,<4"

_MIN_POLL_INTERVAL = 5


def _optional_int(value, minimum=None, maximum=None):
    if value in (None, "", 0, "0"):
        return None
    try:
        value = int(value)
    except (TypeError, ValueError):
        return None
    if minimum is not None:
        value = max(value, minimum)
    if maximum is not None:
        value = min(value, maximum)
    return value


class TapoBulbsPlugin(
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.ShutdownPlugin,
):
    """OctoPrint plugin implementation."""

    def __init__(self):
        super(TapoBulbsPlugin, self).__init__()
        self._client = None
        self._client_lock = threading.Lock()
        self._timer = None
        self._states = {}
        self._last_error = None
        self._automation = None

    # ------------------------------------------------------------ SettingsPlugin

    def get_settings_defaults(self):
        return {
            "base_url": "",
            "access_token": "",
            "verify_certificate": True,
            "request_timeout": 5,
            "poll_interval": 30,
            "off_delay": 0,
            "bulbs": [],
        }

    def get_settings_restricted_paths(self):
        return {"admin": [["access_token"]]}

    def get_settings_version(self):
        return 1

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        with self._client_lock:
            if self._client is not None:
                self._client.close()
            self._client = None
        self._restart_timer()

    # --------------------------------------------------------------- UI plugins

    def get_assets(self):
        return {"js": ["js/tapo_bulbs.js"], "css": ["css/tapo_bulbs.css"]}

    def is_template_autoescaped(self):
        return True

    def get_template_configs(self):
        return [
            {"type": "navbar", "custom_bindings": True, "classes": ["dropdown"]},
            {"type": "settings", "name": "Tapo Bulbs", "custom_bindings": True},
        ]

    # ----------------------------------------------------------- lifecycle/client

    def on_after_startup(self):
        self._automation = PrintLightController(
            self._turn_on_bulb, self._turn_off_bulb, self._push, self._logger
        )
        self._restart_timer()

    def on_shutdown(self):
        self._stop_timer()
        if self._automation is not None:
            self._automation.shutdown()
        with self._client_lock:
            if self._client is not None:
                self._client.close()
                self._client = None

    @property
    def client(self):
        """Return a client that matches the currently saved settings."""
        base_url = self._settings.get(["base_url"])
        token = self._settings.get(["access_token"])
        verify = self._settings.get_boolean(["verify_certificate"])
        timeout = self._settings.get_int(["request_timeout"]) or 5
        with self._client_lock:
            if self._client is None or not self._client.matches(
                base_url, token, verify, timeout
            ):
                if self._client is not None:
                    self._client.close()
                self._client = HomeAssistantClient(
                    base_url,
                    token,
                    verify_certificate=verify,
                    timeout=timeout,
                    logger=self._logger,
                )
            return self._client

    # ------------------------------------------------------------------- polling

    def _restart_timer(self):
        self._stop_timer()
        interval = max(
            self._settings.get_int(["poll_interval"]) or 30, _MIN_POLL_INTERVAL
        )
        self._timer = RepeatedTimer(interval, self._poll, run_first=True)
        self._timer.start()

    def _stop_timer(self):
        if self._timer is not None:
            try:
                self._timer.cancel()
            except Exception:
                pass
            self._timer = None

    def _poll(self):
        if not self.client.configured:
            return
        try:
            all_states = self.client.get_all_states()
            states = self._build_states(all_states)
        except HomeAssistantError as exc:
            if self._last_error != exc.message:
                self._logger.warning("Home Assistant poll failed: %s", exc.message)
            self._last_error = exc.message
            self._states = {}
            self._push_snapshot()
            return
        except Exception:
            self._logger.exception("Unexpected error polling Home Assistant")
            return

        self._last_error = None
        if states != self._states:
            self._states = states
            self._push_snapshot()

    def _build_states(self, all_states):
        result = {}
        for bulb in self._bulbs():
            state = all_states.get(bulb["entity_id"])
            attributes = (state or {}).get("attributes") or {}
            result[bulb["entity_id"]] = {
                "state": (state or {}).get("state", "unknown"),
                "available": state is not None
                and (state or {}).get("state") != "unavailable",
                "brightness": attributes.get("brightness"),
                "color_temp_kelvin": attributes.get("color_temp_kelvin"),
            }
        return result

    def _push_snapshot(self):
        payload = self._payload()
        payload["type"] = "states"
        self._push(payload)

    def _push(self, payload):
        try:
            self._plugin_manager.send_plugin_message(self._identifier, payload)
        except Exception:
            self._logger.exception("Could not push a plugin message")

    def _refresh_soon(self):
        timer = threading.Timer(1.5, self._poll)
        timer.daemon = True
        timer.start()

    # --------------------------------------------------------------------- bulbs

    def _bulbs(self):
        result = []
        for raw in self._settings.get(["bulbs"], merged=True) or []:
            if not isinstance(raw, dict):
                continue
            entity_id = (raw.get("entity_id") or "").strip()
            if not entity_id.startswith("light."):
                continue
            result.append(
                {
                    "entity_id": entity_id,
                    "label": (raw.get("label") or "").strip() or entity_id,
                    "show_in_navbar": bool(raw.get("show_in_navbar", True)),
                    "on_print_start": bool(raw.get("on_print_start", True)),
                    "off_print_done": bool(raw.get("off_print_done", True)),
                    "off_print_failed": bool(raw.get("off_print_failed", True)),
                    "off_print_cancelled": bool(raw.get("off_print_cancelled", True)),
                    "brightness_pct": _optional_int(
                        raw.get("brightness_pct"), minimum=1, maximum=100
                    ),
                    "color_temp_kelvin": _optional_int(
                        raw.get("color_temp_kelvin"), minimum=1
                    ),
                }
            )
        return result

    def _bulb(self, entity_id):
        for bulb in self._bulbs():
            if bulb["entity_id"] == entity_id:
                return bulb
        return None

    def _turn_on_bulb(self, entity_id, brightness_pct=None, color_temp_kelvin=None):
        self.client.turn_on(entity_id, brightness_pct, color_temp_kelvin)
        self._refresh_soon()

    def _turn_off_bulb(self, entity_id):
        self.client.turn_off(entity_id)
        self._refresh_soon()

    # ----------------------------------------------------------------------- API

    def is_api_protected(self):
        return True

    def get_api_commands(self):
        return {
            "turn_on": ["entity_id"],
            "turn_off": ["entity_id"],
            "refresh": [],
            "list_lights": [],
            "test_connection": ["base_url", "access_token", "verify_certificate"],
        }

    def on_api_get(self, request):
        if not Permissions.STATUS.can():
            return flask.abort(403)
        return flask.jsonify(self._payload())

    def on_api_command(self, command, data):
        if command in ("list_lights", "test_connection"):
            if not Permissions.SETTINGS.can():
                return flask.abort(403)
        elif not Permissions.PLUGIN_TAPO_BULBS_CONTROL.can():
            return flask.abort(403)

        handler = getattr(self, "_command_{}".format(command), None)
        if handler is None:
            return flask.abort(400, description="Unknown command")
        try:
            return handler(data)
        except HomeAssistantError as exc:
            self._logger.warning("Command %s failed: %s", command, exc.message)
            return flask.jsonify(ok=False, error=exc.message)
        except Exception:
            self._logger.exception("Command %s raised", command)
            return flask.jsonify(ok=False, error="Unexpected plugin error; see octoprint.log.")

    def _command_refresh(self, data):
        self._poll()
        return flask.jsonify(self._payload())

    def _command_turn_on(self, data):
        bulb = self._guard_known(data["entity_id"])
        self._turn_on_bulb(
            bulb["entity_id"], bulb["brightness_pct"], bulb["color_temp_kelvin"]
        )
        return flask.jsonify(ok=True)

    def _command_turn_off(self, data):
        bulb = self._guard_known(data["entity_id"])
        self._turn_off_bulb(bulb["entity_id"])
        return flask.jsonify(ok=True)

    def _guard_known(self, entity_id):
        validate_light_entity(entity_id)
        bulb = self._bulb(entity_id)
        if bulb is None:
            raise HomeAssistantError(
                "{} is not one of the configured bulbs.".format(entity_id)
            )
        return bulb

    @contextlib.contextmanager
    def _settings_client(self, data):
        base_url = (data.get("base_url") or "").strip()
        if not base_url:
            yield self.client
            return
        client = HomeAssistantClient(
            base_url,
            data.get("access_token") or self._settings.get(["access_token"]),
            verify_certificate=data.get("verify_certificate", True),
            timeout=self._settings.get_int(["request_timeout"]) or 5,
            logger=self._logger,
        )
        try:
            yield client
        finally:
            client.close()

    def _command_test_connection(self, data):
        with self._settings_client(data) as client:
            message = client.test_connection()
        return flask.jsonify(ok=True, message=message)

    def _command_list_lights(self, data):
        with self._settings_client(data) as client:
            states = client.get_all_states()
        lights = []
        for entity_id, state in sorted(states.items()):
            if not entity_id.startswith("light."):
                continue
            attributes = state.get("attributes") or {}
            lights.append(
                {
                    "entity_id": entity_id,
                    "name": attributes.get("friendly_name", entity_id),
                    "supported_color_modes": attributes.get(
                        "supported_color_modes", []
                    ),
                    "min_color_temp_kelvin": attributes.get("min_color_temp_kelvin"),
                    "max_color_temp_kelvin": attributes.get("max_color_temp_kelvin"),
                }
            )
        return flask.jsonify(ok=True, lights=lights)

    def _payload(self):
        return {
            "bulbs": self._bulbs(),
            "states": self._states,
            "error": self._last_error,
        }

    # ------------------------------------------------------- EventHandlerPlugin

    def on_event(self, event, payload):
        if self._automation is None:
            return
        if event == Events.PRINT_STARTED:
            self._automation.print_started(self._bulbs())
        elif event in (Events.PRINT_DONE, Events.PRINT_FAILED, Events.PRINT_CANCELLED):
            outcome = {
                Events.PRINT_DONE: "done",
                Events.PRINT_FAILED: "failed",
                Events.PRINT_CANCELLED: "cancelled",
            }[event]
            self._automation.print_ended(
                self._bulbs(),
                outcome,
                self._settings.get_float(["off_delay"]) or 0,
            )

    # --------------------------------------------------------------------- hooks

    def get_additional_permissions(self, *args, **kwargs):
        return [
            {
                "key": "CONTROL",
                "name": "Control Tapo bulbs",
                "description": "Allows switching configured Home Assistant "
                "light entities on and off from OctoPrint.",
                "roles": ["control"],
                "dangerous": False,
                "default_groups": [ADMIN_GROUP, USER_GROUP],
            }
        ]

    def get_update_information(self):
        return {
            "tapo_bulbs": {
                "displayName": "Tapo Bulbs",
                "displayVersion": self._plugin_version,
                "type": "github_release",
                "user": "willtheorangeguy",
                "repo": "OctoPrint-TapoBulbs",
                "current": self._plugin_version,
                "pip": "https://github.com/willtheorangeguy/OctoPrint-TapoBulbs/archive/{target_version}.zip",
            }
        }


__plugin_implementation__ = TapoBulbsPlugin()
__plugin_hooks__ = {
    "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
    "octoprint.access.permissions": __plugin_implementation__.get_additional_permissions,
}
