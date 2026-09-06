# Matter setup

[Home Assistant's Matter integration](https://www.home-assistant.io/integrations/matter/)
commissions and controls the bulb. The OctoPrint plugin communicates with Home
Assistant rather than opening a Matter session to the bulb.

## Commission the bulb

1. Power the bulb and reset it according to its hardware instructions. The
   [Tapo L535E product page](https://www.tp-link.com/ca/home-networking/smart-bulb/tapo-l535e/)
   confirms Matter support for that model.
2. In the Home Assistant mobile app, open **Settings -> Devices & services**.
3. Press **Add integration**, choose **Add Matter device**, and scan the Matter
   QR code supplied with the bulb.
4. Complete the pairing flow and assign the device to the printer room.
5. Open the device in Home Assistant and record its `light.*` entity ID, such
   as `light.printer_camera`.

The phone running the Home Assistant app needs Bluetooth during commissioning.
Home Assistant and the bulb need IPv6-capable local connectivity for Matter.

## Verify Home Assistant control

Turn the entity on and off from the Home Assistant dashboard before configuring
OctoPrint. The plugin cannot repair Matter commissioning, discovery, or network
routing problems.

## Create the API credential

Open your Home Assistant profile, scroll to **Long-lived access tokens**, press
**Create token**, and copy the value. Home Assistant shows it once.

!!! warning
    Treat the token as a password. Do not put it in screenshots, issue reports,
    source control, or documentation builds.

## Existing Tapo app setup

Matter supports multiple administrators. A bulb already managed by another
Matter ecosystem can be shared to Home Assistant using that ecosystem's Matter
sharing flow. The exact menu belongs to the commissioning platform, not this
plugin.
