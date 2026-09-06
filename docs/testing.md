# Testing

<!-- markdownlint-disable MD046 -->
<!-- Material content tabs require indentation around fenced code blocks. -->

The test suite covers Home Assistant request construction, safe error mapping,
per-outcome automation, failure isolation, shutdown, and delayed-action
cancellation.

## Run tests

Install development dependencies first:

=== "Windows"

    ```powershell
    .venv\Scripts\python -m pip install -e ".[develop]"
    .venv\Scripts\python -m pytest
    ```

=== "macOS / Linux"

    ```bash
    .venv/bin/python -m pip install -e ".[develop]"
    .venv/bin/python -m pytest
    ```

A successful run ends with output like:

```text
21 passed
```

The exact count changes as coverage grows.

## Test organization

| File | Scope |
| --- | --- |
| `tests/test_ha_client.py` | Entity validation, REST paths, payloads, authentication, states, and errors |
| `tests/test_automation.py` | Start/end selection, profiles, delays, cancellation, shutdown, and partial failure |

`requests-mock` intercepts Home Assistant calls. The suite does not require a
Home Assistant server, Matter controller, bulb, or OctoPrint process.

## Manual test

Use OctoPrint's Virtual Printer to verify UI and event wiring:

1. Configure a real Home Assistant test light.
2. Start OctoPrint from the development checkout.
3. Enable and connect the Virtual Printer.
4. Start a short G-code file and confirm the selected light turns on.
5. Complete, cancel, and fail separate jobs to exercise each terminal choice.
6. Start another job during the turn-off delay and confirm the older off action
   is cancelled.
