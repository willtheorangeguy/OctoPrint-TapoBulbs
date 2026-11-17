# OctoPrint-TapoBulbs

Turn TP-Link Tapo bulbs on when an OctoPrint job starts and off when it ends.
The bulb connects to Home Assistant through Matter; the plugin controls its
Home Assistant `light.*` entity over the REST API.

## Features

- **Print lifecycle lighting.** Turn each configured bulb on at print start and
  off after completed, failed, or cancelled prints.
- **Camera-lighting profile.** Apply an optional brightness percentage and
  colour temperature when the bulb turns on.
- **Delayed turn-off.** Keep the light on after a print for a configurable
  number of seconds. A new print cancels the pending shutoff.
- **Multi-bulb control.** Configure multiple Home Assistant light entities and
  choose the events that affect each one.
- **Navbar controls.** See current state and brightness, then switch a bulb on
  or off without leaving OctoPrint.
- **Matter through Home Assistant.** Home Assistant owns device commissioning
  and Matter credentials. The plugin needs only the entity ID and a long-lived
  Home Assistant access token.

## Requirements

- OctoPrint 1.5.0 or newer, including 2.0.0 (Python 3.9+ for OctoPrint 2)
- A reachable Home Assistant instance with the Matter integration
- A Matter-compatible Tapo bulb commissioned in Home Assistant as a `light.*`
  entity
- A Home Assistant long-lived access token

The [Tapo L535E](https://www.tp-link.com/ca/home-networking/smart-bulb/tapo-l535e/)
is one compatible example. Other Tapo Matter bulbs exposed by Home Assistant as
light entities use the same interface.

## Installation

Install through OctoPrint's Plugin Manager using:

```text
https://github.com/willtheorangeguy/OctoPrint-TapoBulbs/archive/v0.1.0.zip
```

## Setup

1. Commission the bulb with **Settings -> Devices & services -> Matter** in
   Home Assistant.
2. Create a long-lived access token in your Home Assistant profile.
3. Open **Settings -> Tapo Bulbs** in OctoPrint and enter the Home Assistant URL
   and token.
4. Press **Test connection**, then **Load lights from Home Assistant**.
5. Add the bulb's `light.*` entity and select the print events that control it.
6. Set brightness or colour temperature when you want a fixed camera-lighting
   profile. Leave either field blank to preserve that attribute.

## How it communicates

```text
OctoPrint print event
        |
        v
OctoPrint-TapoBulbs
        | Home Assistant REST API
        v
Home Assistant light entity
        | Matter on the local network
        v
Tapo bulb
```

The plugin does not commission Matter devices and never receives their setup
codes or fabric credentials.

## Development

Compatibility checks against OctoPrint 2.0.0 cover plugin discovery, settings,
API permissions, and print event automation. See [testing](docs/testing.md) for
the remaining checks with a real Home Assistant light.

```bash
python -m venv .venv
.venv/bin/pip install OctoPrint
.venv/bin/pip install -e ".[develop]"
.venv/bin/pytest
```

See the [documentation site](https://williamvdg.me/OctoPrint-TapoBulbs/) for
Matter setup, configuration, API details, testing, and troubleshooting.

## License

[AGPLv3](LICENSE)
