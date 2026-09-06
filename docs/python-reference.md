# Python reference

These interfaces support the plugin implementation. Running OctoPrint clients
should use the [HTTP API](api.md). Mkdocstrings generates the definitions below
from source.

## Home Assistant transport

This example validates a bulb entity without making a network request:

```python
from octoprint_tapo_bulbs.ha_client import validate_light_entity

print(validate_light_entity("light.printer_camera"))
```

```text
light.printer_camera
```

::: octoprint_tapo_bulbs.ha_client
    options:
      members:
        - validate_light_entity
        - HomeAssistantError
        - HomeAssistantClient

## Print automation

OctoPrint constructs this controller with Home Assistant and plugin-message
callbacks. The [architecture guide](architecture.md) explains its concurrency
boundary.

::: octoprint_tapo_bulbs.automation
    options:
      members:
        - PrintLightController
