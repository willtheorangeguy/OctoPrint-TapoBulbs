# Troubleshooting

Start with Home Assistant. The plugin cannot control a bulb that Home Assistant
cannot reach.

## Connection test says the token was rejected

Home Assistant returned HTTP 401. Create a new long-lived token from your Home
Assistant profile, paste it into **Access token**, and save the settings.

Make sure the token belongs to an active Home Assistant user. Do not include a
`Bearer` prefix; the plugin adds it to the request header.

## Connection test returns a non-JSON response

The server URL points to a proxy error page or another web application. Use the
Home Assistant base URL without `/api`, a dashboard path, or a trailing route.

```text
http://homeassistant.local:8123
```

## No lights appear after loading

**Load lights from Home Assistant** lists only entity IDs beginning with
`light.`. Confirm that Matter commissioning created a light entity and that the
same Home Assistant user can see it.

If the device exists but has no light entity, fix its Home Assistant Matter
integration before configuring the plugin.

## The state dot stays amber

Amber means the entity is unknown, unavailable, or missing from Home
Assistant's state response.

1. Open the entity in Home Assistant and check its current state.
2. Confirm that the saved entity ID still matches.
3. Turn the bulb off and on at its wall switch.
4. Check IPv6 and Matter connectivity between the bulb and Home Assistant.
5. Review `octoprint.log` for `Home Assistant poll failed`.

## The bulb turns on but brightness or Kelvin does not change

The entity may not support that attribute or the configured Kelvin value may be
outside its advertised range. Open the Home Assistant entity attributes and
check `supported_color_modes`, `min_color_temp_kelvin`, and
`max_color_temp_kelvin`.

Clear the unsupported field in OctoPrint to send a plain `light.turn_on` call.

## The bulb switched off after another print started

The controller cancels a delayed turn-off when OctoPrint emits a later
`PrintStarted` event. If the light still switches off, confirm that the later
job produced that event in `octoprint.log` and check for a separate Home
Assistant or Tapo automation controlling the same bulb.

## TLS verification fails

Use a certificate trusted by the OctoPrint host. For a controlled local setup
with a self-signed certificate, clear **Verify the TLS certificate**. This
weakens server authentication and is not appropriate across an untrusted
network.
