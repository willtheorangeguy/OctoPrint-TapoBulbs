# Known issues

- State updates are polled rather than subscribed through Home Assistant's
  WebSocket API.
- Automated actions are fire-and-report background work. OctoPrint does not
  block print-state transitions while Home Assistant responds.
- Brightness and colour-temperature capability bounds are shown by discovery
  but not copied into each settings row.
