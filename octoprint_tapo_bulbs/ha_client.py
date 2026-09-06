# coding=utf-8
"""Small, thread-safe Home Assistant REST API client for light entities."""

from __future__ import absolute_import, unicode_literals

import logging
import threading

import requests

_DEFAULT_TIMEOUT = 5


class HomeAssistantError(Exception):
    """Raised when a Home Assistant request or light configuration fails."""

    def __init__(self, message, status_code=None):
        super(HomeAssistantError, self).__init__(message)
        self.message = message
        self.status_code = status_code


def validate_light_entity(entity_id):
    """Return a normalized ``light.*`` entity ID or raise a friendly error."""
    entity_id = (entity_id or "").strip()
    if not entity_id.startswith("light.") or len(entity_id) <= len("light."):
        raise HomeAssistantError(
            "{!r} is not a Home Assistant light entity ID (expected "
            "light.my_bulb).".format(entity_id)
        )
    return entity_id


class HomeAssistantClient(object):
    """Wrap the Home Assistant endpoints used by the plugin."""

    def __init__(
        self,
        base_url,
        access_token,
        verify_certificate=True,
        timeout=_DEFAULT_TIMEOUT,
        logger=None,
    ):
        self._base_url = (base_url or "").strip().rstrip("/")
        self._access_token = (access_token or "").strip()
        self._verify = bool(verify_certificate)
        self._timeout = timeout or _DEFAULT_TIMEOUT
        self._logger = logger or logging.getLogger(__name__)
        self._lock = threading.Lock()
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": "Bearer {}".format(self._access_token),
                "Content-Type": "application/json",
            }
        )

        if not self._verify:
            try:
                import urllib3

                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            except Exception:  # pragma: no cover
                pass

    @property
    def base_url(self):
        """Configured Home Assistant base URL without a trailing slash."""
        return self._base_url

    @property
    def configured(self):
        """Whether both connection fields have values."""
        return bool(self._base_url and self._access_token)

    def matches(self, base_url, access_token, verify_certificate, timeout):
        """Return whether this client was built from the supplied settings."""
        return (
            self._base_url == (base_url or "").strip().rstrip("/")
            and self._access_token == (access_token or "").strip()
            and self._verify == bool(verify_certificate)
            and self._timeout == (timeout or _DEFAULT_TIMEOUT)
        )

    def close(self):
        """Close the underlying HTTP session."""
        try:
            self._session.close()
        except Exception:
            pass

    def _request(self, method, path, payload=None):
        if not self.configured:
            raise HomeAssistantError(
                "Home Assistant is not configured yet - set the server URL and "
                "access token in the plugin settings."
            )

        try:
            with self._lock:
                response = self._session.request(
                    method,
                    "{}/api{}".format(self._base_url, path),
                    json=payload,
                    timeout=self._timeout,
                    verify=self._verify,
                )
        except requests.exceptions.SSLError:
            raise HomeAssistantError(
                "TLS verification failed. Disable certificate verification only "
                "if Home Assistant uses a trusted self-signed certificate."
            )
        except requests.exceptions.Timeout:
            raise HomeAssistantError(
                "Home Assistant did not respond within {}s.".format(self._timeout)
            )
        except requests.exceptions.ConnectionError:
            raise HomeAssistantError(
                "Could not reach Home Assistant at {}.".format(self._base_url)
            )
        except requests.exceptions.RequestException as exc:
            raise HomeAssistantError(
                "Request to Home Assistant failed ({}).".format(type(exc).__name__)
            )

        if response.status_code == 401:
            raise HomeAssistantError(
                "Home Assistant rejected the access token (401). Create a new "
                "long-lived access token and update the plugin settings.",
                status_code=401,
            )
        if response.status_code == 403:
            raise HomeAssistantError(
                "The access token is not allowed to perform this action (403).",
                status_code=403,
            )
        if response.status_code == 404:
            raise HomeAssistantError(
                "Home Assistant returned 404 for {}. Check the server URL and "
                "entity ID.".format(path),
                status_code=404,
            )
        if response.status_code >= 400:
            raise HomeAssistantError(
                "Home Assistant returned HTTP {}.".format(response.status_code),
                status_code=response.status_code,
            )
        if not response.content:
            return None
        try:
            return response.json()
        except ValueError:
            raise HomeAssistantError(
                "Home Assistant returned a non-JSON response. Check the server URL."
            )

    def test_connection(self):
        """Return Home Assistant's REST API greeting."""
        result = self._request("GET", "/")
        message = (result or {}).get("message", "")
        if "API running" not in message:
            raise HomeAssistantError(
                "Connected, but {} is not a Home Assistant API endpoint.".format(
                    self._base_url
                )
            )
        return message

    def get_all_states(self):
        """Return all Home Assistant states indexed by entity ID."""
        states = self._request("GET", "/states") or []
        return {
            state["entity_id"]: state
            for state in states
            if isinstance(state, dict) and state.get("entity_id")
        }

    def call_light_service(self, entity_id, service, **attributes):
        """Call a Home Assistant light service with validated attributes."""
        entity_id = validate_light_entity(entity_id)
        payload = {"entity_id": entity_id}
        payload.update({key: value for key, value in attributes.items() if value is not None})
        return self._request(
            "POST", "/services/light/{}".format(service), payload=payload
        )

    def turn_on(self, entity_id, brightness_pct=None, color_temp_kelvin=None):
        """Turn on a bulb and optionally apply a camera-lighting profile."""
        attributes = {}
        if brightness_pct is not None:
            brightness = int(brightness_pct)
            if brightness < 1 or brightness > 100:
                raise HomeAssistantError("Brightness must be between 1 and 100%.")
            attributes["brightness_pct"] = brightness
        if color_temp_kelvin is not None:
            kelvin = int(color_temp_kelvin)
            if kelvin <= 0:
                raise HomeAssistantError("Color temperature must be greater than 0 K.")
            attributes["color_temp_kelvin"] = kelvin
        return self.call_light_service(entity_id, "turn_on", **attributes)

    def turn_off(self, entity_id):
        """Turn off a bulb."""
        return self.call_light_service(entity_id, "turn_off")
