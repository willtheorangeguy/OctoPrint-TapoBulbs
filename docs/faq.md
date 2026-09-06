# FAQ

???+ question "Does the plugin connect directly to the bulb?"

    No. Home Assistant commissions the bulb and communicates with it over
    Matter. The plugin calls Home Assistant's REST API with a long-lived access
    token.

??? question "Does it work only with the Tapo L535E?"

    No. The plugin accepts any Home Assistant entity whose ID starts with
    `light.`. The L535E is the reference use case because it supports Matter,
    brightness, and tunable white.

??? question "Can it control more than one bulb?"

    Yes. Add multiple rows and select print events independently for each row.
    A service failure for one bulb does not stop actions for the others.

??? question "What happens when a print is cancelled or fails?"

    The bulb turns off when the corresponding **Cancelled** or **Failed** option
    is selected. Both are selected by default.

??? question "Can it leave a bulb's existing brightness unchanged?"

    Yes. Leave **Brightness** blank. Leave **Kelvin** blank to preserve the
    existing colour-temperature behaviour too.

??? question "Can another print interrupt the turn-off delay?"

    Yes. A later `PrintStarted` event invalidates the older delayed action, so
    the active print keeps its lights on.

??? question "Why use Home Assistant instead of the Tapo cloud API?"

    Home Assistant provides the Matter controller, local device entity, and a
    stable light service. The plugin does not need Tapo account credentials or
    a vendor-cloud session.
