# API

The plugin exposes OctoPrint's protected Simple API at
`/api/plugin/tapo_bulbs`. GET returns cached status. POST commands use a JSON
`command` field. Use an OctoPrint API key; this is separate from the Home
Assistant token stored in plugin settings.

## Request setup

The examples run in one Python session:

```python
from getpass import getpass
import requests

octoprint_url = input("OctoPrint base URL: ").strip().rstrip("/")
octoprint_key = getpass("OctoPrint API key: ")
endpoint = octoprint_url + "/api/plugin/tapo_bulbs"
headers = {"X-Api-Key": octoprint_key}

def command(name, **parameters):
    response = requests.post(
        endpoint,
        headers=headers,
        json={"command": name, **parameters},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()
```

## Response conventions

| Condition | Status and body |
| --- | --- |
| Successful command | HTTP 200 with `{"ok": true}` or a command-specific object |
| Home Assistant failure | HTTP 200 with `{"ok": false, "error": "..."}` |
| Missing permission | HTTP 403 |
| Unknown command | HTTP 400 |
| Missing required command field | Rejected by OctoPrint's Simple API validation |

## Get status

`GET /api/plugin/tapo_bulbs` requires OctoPrint `STATUS`. It does not force a
poll.

```python
response = requests.get(endpoint, headers=headers, timeout=15)
response.raise_for_status()
print(response.json())
```

```json
{
  "bulbs": [
    {
      "entity_id": "light.printer_camera",
      "label": "Printer light",
      "show_in_navbar": true,
      "on_print_start": true,
      "off_print_done": true,
      "off_print_failed": true,
      "off_print_cancelled": true,
      "brightness_pct": 90,
      "color_temp_kelvin": 5000
    }
  ],
  "states": {
    "light.printer_camera": {
      "state": "on",
      "available": true,
      "brightness": 230,
      "color_temp_kelvin": 5000
    }
  },
  "error": null
}
```

## Turn on

POST fields: `command: turn_on` and required string `entity_id`. This requires
`PLUGIN_TAPO_BULBS_CONTROL`. The entity must be in saved bulb settings.

```python
print(command("turn_on", entity_id="light.printer_camera"))
```

```json
{"ok": true}
```

The plugin applies the saved brightness and Kelvin fields when present.

## Turn off

POST fields: `command: turn_off` and required string `entity_id`. This requires
`PLUGIN_TAPO_BULBS_CONTROL`.

```python
print(command("turn_off", entity_id="light.printer_camera"))
```

```json
{"ok": true}
```

## Refresh

POST body: `{"command": "refresh"}`. This requires
`PLUGIN_TAPO_BULBS_CONTROL` and synchronously polls Home Assistant.

```python
snapshot = command("refresh")
print(snapshot["error"])
```

```text
None
```

The complete response matches [Get status](#get-status) and has no `ok` field.

## Test connection

This command requires OctoPrint `SETTINGS`. The fields `base_url`,
`access_token`, and `verify_certificate` are required by the Simple API command
schema. Empty connection strings fall back to saved settings.

```python
print(command(
    "test_connection",
    base_url="",
    access_token="",
    verify_certificate=True,
))
```

```json
{"ok": true, "message": "API running."}
```

## List lights

POST body: `{"command": "list_lights"}` with optional unsaved connection
fields. This requires OctoPrint `SETTINGS`.

```python
print(command("list_lights"))
```

```json
{
  "ok": true,
  "lights": [
    {
      "entity_id": "light.printer_camera",
      "name": "Printer Camera",
      "supported_color_modes": ["color_temp", "hs"],
      "min_color_temp_kelvin": 2500,
      "max_color_temp_kelvin": 6500
    }
  ]
}
```

Only `light.*` states are returned. Capability attributes may be missing or
null when Home Assistant does not publish them.

## Plugin messages

The browser receives messages under plugin ID `tapo_bulbs`.

| Type | Contents |
| --- | --- |
| `states` | The GET snapshot plus `type: states` |
| `automation` | `action` (`on` or `off`), `state`, and a `failures` array |

An invalidated delayed action uses automation state `cancelled`. A finished
action uses `done` or `failed`.

## Home Assistant API consumed

The client sends JSON with `Authorization: Bearer ...`.

| Method and path | Use | Request example | Response |
| --- | --- | --- | --- |
| `GET /api/` | Connection test | No body | `{"message": "API running."}` |
| `GET /api/states` | Discovery and polling | No body | Array of Home Assistant state objects |
| `POST /api/services/light/turn_on` | Manual and print-start on | `{"entity_id": "light.printer_camera", "brightness_pct": 90}` | Array of changed states |
| `POST /api/services/light/turn_off` | Manual and print-end off | `{"entity_id": "light.printer_camera"}` | Array of changed states |

Read the [Home Assistant REST API reference](https://developers.home-assistant.io/docs/api/rest/)
for the upstream contract.
