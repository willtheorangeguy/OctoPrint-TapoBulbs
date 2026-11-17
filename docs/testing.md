# Testing

<!-- markdownlint-disable MD046 -->
<!-- Material content tabs require indentation around fenced code blocks. -->

The test suite covers Home Assistant request construction, safe error mapping,
per-outcome automation, failure isolation, shutdown, and delayed-action
cancellation. It also uses installed OctoPrint APIs to check plugin discovery,
settings, permission enforcement, and print event wiring.

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
38 passed
```

The exact count changes as coverage grows.

## Test organization

| File | Scope |
| --- | --- |
| `tests/test_ha_client.py` | Entity validation, REST paths, payloads, authentication, states, and errors |
| `tests/test_automation.py` | Start/end selection, profiles, delays, cancellation, shutdown, and partial failure |
| `tests/test_plugin.py` | OctoPrint entry point discovery, settings, API permissions, and print events reaching the Home Assistant client |

`requests-mock` intercepts Home Assistant calls. The suite does not require a
Home Assistant server, Matter controller, bulb, or OctoPrint process.

## OctoPrint 2.0.0 compatibility

The 38 automated tests pass against OctoPrint 2.0.0 on Python 3.12. The plugin
does not use the removed APIs listed in the
[OctoPrint 2.0.0 migration guide](https://docs.octoprint.org/en/main/plugins/migration_2_0_0.html).
Its print automation uses lifecycle events without depending on the printer
connector implementation or event payload fields.

Builds use the setuptools backend declared in `pyproject.toml`. They do not
import OctoPrint during packaging. Both an editable install and a wheel build
work with pip's default build isolation:

```bash
python -m pip install -e ".[develop]"
python -m pip wheel . --no-deps --wheel-dir dist
python -m pytest
```

These checks mock Home Assistant traffic. Verify browser controls and actual
bulb behavior with the manual test below before deploying to a printer.

## Manual test

Use OctoPrint's Virtual Printer to verify UI and event wiring:

1. Configure a real Home Assistant test light.
2. Start OctoPrint from the development checkout.
3. Enable and connect the Virtual Printer.
4. Start a short G-code file and confirm the selected light turns on.
5. Complete, cancel, and fail separate jobs to exercise each terminal choice.
6. Start another job during the turn-off delay and confirm the older off action
   is cancelled.
