"""Exercise the plugin against installed OctoPrint APIs, without hardware."""

import logging
import threading

import flask
import pytest
from octoprint.access.permissions import Permissions, PluginOctoPrintPermission
from octoprint.events import Events
from octoprint.plugin import OctoPrintPlugin, plugin_settings
from octoprint.plugin.core import PluginManager
from octoprint.settings import Settings
from octoprint.vendor.flask_principal import Identity, RoleNeed
from werkzeug.exceptions import Forbidden

import octoprint_tapo_bulbs


BASE = "https://ha.example"
ENTITY = "light.printer"


@pytest.fixture
def plugin(tmp_path, monkeypatch):
    instance = octoprint_tapo_bulbs.TapoBulbsPlugin()
    instance._identifier = "tapo_bulbs"
    instance._logger = logging.getLogger("test.tapo_bulbs")
    instance._settings = plugin_settings(
        "tapo_bulbs",
        defaults=instance.get_settings_defaults(),
        settings=Settings(basedir=str(tmp_path)),
    )
    instance._settings.set(["base_url"], BASE)
    instance._settings.set(["access_token"], "test-token")
    instance._settings.set(["bulbs"], [{"entity_id": ENTITY}])
    # Avoid delayed network activity after a test has finished.
    monkeypatch.setattr(instance, "_refresh_soon", lambda: None)
    monkeypatch.setattr(instance, "_push", lambda payload: None)
    definition = instance.get_additional_permissions()[0]
    permission = PluginOctoPrintPermission(
        definition["name"], definition["description"], *definition["roles"],
        plugin="tapo_bulbs", default_groups=definition["default_groups"]
    )
    permission.key = "PLUGIN_TAPO_BULBS_CONTROL"
    monkeypatch.setitem(Permissions.permissions, permission.key, permission)
    try:
        yield instance
    finally:
        instance.on_shutdown()


def identity(*roles):
    result = Identity("test-user")
    result.provides.update(RoleNeed(role) for role in roles)
    return result


def test_installed_entry_point_loads_in_octoprint():
    manager = PluginManager([], [OctoPrintPlugin], ["octoprint.plugin"])
    manager.reload_plugins(startup=True, initialize_implementations=False)
    info = manager.enabled_plugins["tapo_bulbs"]
    assert not info.incompatible
    # The plugin manager reloads the module, creating a fresh class object.
    assert isinstance(info.implementation, OctoPrintPlugin)
    assert info.implementation.is_api_protected()
    assert "octoprint.access.permissions" in info.hooks
    assert "octoprint.plugin.softwareupdate.check_config" in info.hooks


def test_settings_save_uses_octoprint_settings(plugin, monkeypatch):
    monkeypatch.setattr(plugin, "_restart_timer", lambda: None)
    plugin.on_settings_save({"off_delay": 12, "access_token": "replacement"})
    assert plugin._settings.get_float(["off_delay"]) == 12
    assert plugin._settings.get(["access_token"]) == "replacement"
    assert plugin.get_settings_restricted_paths() == {"admin": [["access_token"]]}
    assert plugin._bulbs()[0]["entity_id"] == ENTITY


@pytest.mark.parametrize(
    "event,service",
    [
        (Events.PRINT_STARTED, "turn_on"),
        (Events.PRINT_DONE, "turn_off"),
        (Events.PRINT_FAILED, "turn_off"),
        (Events.PRINT_CANCELLED, "turn_off"),
    ],
)
def test_print_events_reach_home_assistant(plugin, requests_mock, event, service):
    completed = threading.Event()

    def respond(request, context):
        assert request.json()["entity_id"] == ENTITY
        completed.set()
        return []

    requests_mock.get(BASE + "/api/states", json=[])
    requests_mock.post(BASE + "/api/services/light/" + service, json=respond)
    plugin.on_after_startup()
    # OctoPrint 2 includes connector information; the plugin accepts the payload.
    plugin.on_event(event, {"connector": "serial"})
    assert completed.wait(2), "Print event did not trigger the light service"


@pytest.mark.parametrize("allowed", [True, False])
def test_status_api_requires_status_permission(plugin, allowed):
    with flask.Flask(__name__).test_request_context():
        flask.g.identity = identity("status") if allowed else identity()
        assert plugin.is_api_protected()
        if allowed:
            payload = plugin.on_api_get(flask.request).get_json()
            assert payload["bulbs"][0]["entity_id"] == ENTITY
            assert "test-token" not in str(payload)
        else:
            with pytest.raises(Forbidden):
                plugin.on_api_get(flask.request)


@pytest.mark.parametrize("allowed", [True, False])
def test_control_api_uses_registered_permission(plugin, requests_mock, allowed):
    light = requests_mock.post(BASE + "/api/services/light/turn_on", json=[])
    with flask.Flask(__name__).test_request_context():
        flask.g.identity = identity("control") if allowed else identity("status")
        if allowed:
            response = plugin.on_api_command("turn_on", {"entity_id": ENTITY})
            assert response.get_json() == {"ok": True}
            assert light.last_request.json() == {"entity_id": ENTITY}
        else:
            with pytest.raises(Forbidden):
                plugin.on_api_command("turn_on", {"entity_id": ENTITY})
            assert not light.called


@pytest.mark.parametrize("allowed", [True, False])
def test_connection_api_requires_settings_permission(plugin, requests_mock, allowed):
    connection = requests_mock.get(BASE + "/api/", json={"message": "API running."})
    data = {"base_url": BASE, "access_token": "test-token", "verify_certificate": True}
    with flask.Flask(__name__).test_request_context():
        flask.g.identity = identity("settings") if allowed else identity("control")
        if allowed:
            assert plugin.on_api_command("test_connection", data).get_json()["ok"]
            assert connection.called
        else:
            with pytest.raises(Forbidden):
                plugin.on_api_command("test_connection", data)
            assert not connection.called
