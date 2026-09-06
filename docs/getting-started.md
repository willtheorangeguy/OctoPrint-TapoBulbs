# Getting started

This guide takes a Matter-compatible Tapo bulb from pairing to automatic print
lighting.

## Prerequisites

- OctoPrint 1.5.0 or newer
- Home Assistant with its Matter integration running
- A Matter-compatible Tapo bulb, such as the Tapo L535E
- Network reachability from the OctoPrint host to Home Assistant

Check the OctoPrint version under **Settings -> Software Update**. Check Home
Assistant under **Settings -> System -> Repairs -> System information**.

## Install

Open **Settings -> Plugin Manager -> Get More**, paste this URL into **... from
URL**, and press **Install**:

```text
https://github.com/willtheorangeguy/OctoPrint-TapoBulbs/archive/v0.1.0.zip
```

Restart OctoPrint when the Plugin Manager requests it.

## First run

1. Pair the bulb through Home Assistant's Matter integration. Follow
   [Matter setup](matter-setup.md) if it is not already listed as a light.
2. Open your Home Assistant profile and create a long-lived access token.
3. Open **Settings -> Tapo Bulbs** in OctoPrint.
4. Enter a server URL such as `http://homeassistant.local:8123` and paste the
   token.
5. Press **Test connection**. The result reads `Connected to Home Assistant.`
6. Press **Load lights from Home Assistant**.
7. Press **Add bulb**, choose the `light.*` entity, and enter a navbar label.
8. Leave **Start**, **Done**, **Failed**, and **Cancelled** selected to light all
   prints and switch the bulb off for every terminal outcome.
9. Press **Save**.
10. Use **On** and **Off** in the OctoPrint navbar to verify control before
    starting a print.

## What just happened

OctoPrint sent a Home Assistant REST service call for the selected light.
Home Assistant then controlled the physical bulb over its commissioned Matter
fabric. The plugin stored neither the Matter setup code nor Matter keys.

## Next steps

- Set a repeatable video-lighting profile under [Configuration](configuration.md).
- Add a turn-off delay under [Usage](usage.md#delayed-turn-off).
- Use [Troubleshooting](troubleshooting.md) if the state dot stays amber.
