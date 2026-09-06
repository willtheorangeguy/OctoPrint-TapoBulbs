# coding=utf-8
import pytest

from octoprint_tapo_bulbs.ha_client import (
    HomeAssistantClient,
    HomeAssistantError,
    validate_light_entity,
)

BASE = "https://ha.example"
TOKEN = "secret-token"


@pytest.fixture
def client():
    return HomeAssistantClient(BASE, TOKEN, timeout=1)


@pytest.mark.parametrize("entity_id", ["light.printer", "light.enclosure_2"])
def test_validates_light_entities(entity_id):
    assert validate_light_entity(entity_id) == entity_id


@pytest.mark.parametrize("entity_id", ["", None, "light", "switch.printer", "light."])
def test_rejects_non_light_entities(entity_id):
    with pytest.raises(HomeAssistantError):
        validate_light_entity(entity_id)


def test_turn_on_sends_camera_profile(client, requests_mock):
    mock = requests_mock.post(BASE + "/api/services/light/turn_on", json=[])
    client.turn_on("light.printer", brightness_pct=85, color_temp_kelvin=5000)
    assert mock.last_request.json() == {
        "entity_id": "light.printer",
        "brightness_pct": 85,
        "color_temp_kelvin": 5000,
    }


def test_turn_on_omits_blank_profile(client, requests_mock):
    mock = requests_mock.post(BASE + "/api/services/light/turn_on", json=[])
    client.turn_on("light.printer")
    assert mock.last_request.json() == {"entity_id": "light.printer"}


def test_turn_off_uses_light_service(client, requests_mock):
    mock = requests_mock.post(BASE + "/api/services/light/turn_off", json=[])
    client.turn_off("light.printer")
    assert mock.called


def test_sends_bearer_token(client, requests_mock):
    mock = requests_mock.post(BASE + "/api/services/light/turn_off", json=[])
    client.turn_off("light.printer")
    assert mock.last_request.headers["Authorization"] == "Bearer " + TOKEN


@pytest.mark.parametrize("brightness", [0, 101])
def test_rejects_invalid_brightness(client, brightness):
    with pytest.raises(HomeAssistantError):
        client.turn_on("light.printer", brightness_pct=brightness)


def test_get_all_states_indexes_entities(client, requests_mock):
    requests_mock.get(
        BASE + "/api/states",
        json=[
            {"entity_id": "light.printer", "state": "on"},
            {"entity_id": "sensor.room", "state": "20"},
            {"not_an_entity": True},
        ],
    )
    states = client.get_all_states()
    assert set(states) == {"light.printer", "sensor.room"}


def test_test_connection_accepts_home_assistant(client, requests_mock):
    requests_mock.get(BASE + "/api/", json={"message": "API running."})
    assert "API running" in client.test_connection()


def test_401_explains_token_without_disclosing_it(client, requests_mock):
    requests_mock.get(BASE + "/api/states", status_code=401)
    with pytest.raises(HomeAssistantError) as excinfo:
        client.get_all_states()
    assert "token" in excinfo.value.message.lower()
    assert TOKEN not in excinfo.value.message


def test_timeout_has_friendly_message(client, requests_mock):
    import requests

    requests_mock.get(BASE + "/api/", exc=requests.exceptions.ConnectTimeout)
    with pytest.raises(HomeAssistantError) as excinfo:
        client.test_connection()
    assert "did not respond" in excinfo.value.message


def test_unconfigured_client_refuses_request():
    with pytest.raises(HomeAssistantError):
        HomeAssistantClient("", "").get_all_states()


def test_matches_and_strips_trailing_slash(client):
    assert client.matches(BASE + "/", TOKEN, True, 1)
    assert not client.matches(BASE, "different", True, 1)
    assert HomeAssistantClient(BASE + "/", TOKEN).base_url == BASE
