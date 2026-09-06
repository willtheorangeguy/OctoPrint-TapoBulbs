# OctoPrint-TapoBulbs

OctoPrint-TapoBulbs controls TP-Link Tapo Matter bulbs through Home Assistant.
It lights the printer for a video feed while a job runs and switches the light
off when the job ends.

## Key features

- Turns bulbs on when OctoPrint emits `PrintStarted`.
- Turns bulbs off on completed, failed, and cancelled jobs.
- Applies optional brightness and colour-temperature values on turn-on.
- Cancels a delayed turn-off if another print starts.
- Controls any number of Home Assistant `light.*` entities from the navbar.
- Keeps Matter commissioning and credentials in Home Assistant.

## Quick start

Install the release archive in OctoPrint's Plugin Manager:

```text
https://github.com/willtheorangeguy/OctoPrint-TapoBulbs/archive/v0.1.0.zip
```

Pair the bulb in Home Assistant, create a long-lived access token, and open
**Settings -> Tapo Bulbs** in OctoPrint. The [getting started guide](getting-started.md)
covers the complete path.

## Where to next

- [Matter setup](matter-setup.md) commissions the bulb in Home Assistant.
- [Configuration](configuration.md) lists every plugin setting.
- [Usage](usage.md) explains manual controls and print automation.
- [Troubleshooting](troubleshooting.md) maps visible symptoms to checks.

## Support

Open a [GitHub issue](https://github.com/willtheorangeguy/OctoPrint-TapoBulbs/issues)
with the OctoPrint version, plugin version, Home Assistant version, bulb entity
ID, and relevant `octoprint.log` lines. Remove access tokens before posting.
