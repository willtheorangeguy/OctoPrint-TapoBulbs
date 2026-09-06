# Usage

The plugin offers manual navbar controls and event-driven print lighting.

## Manual control

Open the lightbulb menu in OctoPrint's navbar. Each configured bulb shows a
state dot, its Home Assistant brightness when available, and **On** and **Off**
buttons.

The state colours are:

| Colour | Meaning |
| --- | --- |
| Green | Home Assistant reports `on` |
| Grey | Home Assistant reports `off` |
| Amber | State is unknown or unavailable |

Manual **On** applies the configured brightness and colour temperature. Manual
**Off** sends no transition or profile attributes.

## Print automation

At `PrintStarted`, every row with **Start** selected receives `light.turn_on`.
The end-event choices map as follows:

| OctoPrint event | Row option | Home Assistant service |
| --- | --- | --- |
| `PrintDone` | **Done** | `light.turn_off` |
| `PrintFailed` | **Failed** | `light.turn_off` |
| `PrintCancelled` | **Cancelled** | `light.turn_off` |

Each bulb is handled independently. A failure on one row is reported in the UI
and does not stop the remaining bulbs.

## Delayed turn-off

Set **Turn-off delay** to keep the scene lit for a final webcam frame or
timelapse processing. For example, `30` waits 30 seconds after the terminal
event before switching selected bulbs off.

A new `PrintStarted` event cancels a waiting turn-off. This prevents an older
job from darkening a newer print.

## Camera-lighting profile

Set **Brightness** to a value from `1` through `100`. Set **Kelvin** to a value
supported by the Home Assistant entity. The Tapo L535E advertises white light
from 2500 K through 6500 K, but Home Assistant reports the authoritative range
for each device.

Leave a profile field blank to omit it from `light.turn_on`. Home Assistant then
uses the entity's existing behaviour for that attribute.
