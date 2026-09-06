# Configuration

All configuration comes from **Settings -> Tapo Bulbs** and is stored through
OctoPrint's settings system. There are no environment-variable or command-line
overrides.

## Connection settings

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| Server URL | string | empty | Home Assistant base URL, for example `http://homeassistant.local:8123` |
| Access token | secret string | empty | Long-lived Home Assistant token, for example the value created in your profile |
| Verify TLS certificate | boolean | `true` | Validate HTTPS certificates |
| Request timeout | integer | `5` | Seconds before a REST request fails; currently stored as an advanced setting |
| Poll interval | integer | `30` | Seconds between state refreshes; values below `5` run as `5` |
| Turn-off delay | number | `0` | Seconds to wait after an enabled terminal event |

The access token is a restricted admin setting. OctoPrint does not expose it to
non-administrator settings requests.

## Bulb settings

Each bulb row has these options:

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| Entity ID | string | empty | Home Assistant light entity, for example `light.printer_camera` |
| Label | string | entity ID | Text shown in the navbar |
| Navbar | boolean | `true` | Include the bulb in manual controls |
| Start | boolean | `true` | Turn on for `PrintStarted` |
| Done | boolean | `true` | Turn off for `PrintDone` |
| Failed | boolean | `true` | Turn off for `PrintFailed` |
| Cancelled | boolean | `true` | Turn off for `PrintCancelled` |
| Brightness | integer or blank | blank | Brightness percentage from `1` through `100` |
| Kelvin | integer or blank | blank | Colour temperature accepted by the light entity |

Rows without a valid `light.*` entity ID are discarded on save. Brightness is
clamped to `1` through `100`. A non-numeric optional profile value is treated as
blank.

## Example

This OctoPrint settings fragment lights one camera at 90% and 5000 K, then
waits 20 seconds before switching it off:

```yaml title="config.yaml"
plugins:
  tapo_bulbs:
    base_url: http://homeassistant.local:8123
    poll_interval: 30
    off_delay: 20
    bulbs:
      - entity_id: light.printer_camera
        label: Printer light
        show_in_navbar: true
        on_print_start: true
        off_print_done: true
        off_print_failed: true
        off_print_cancelled: true
        brightness_pct: 90
        color_temp_kelvin: 5000
```

Do not paste the access token into an example or commit it to source control.
