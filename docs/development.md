# Development

<!-- markdownlint-disable MD046 -->
<!-- Material content tabs require indentation around fenced code blocks. -->

Develop against the same Python environment constraints as OctoPrint.

## Set up

=== "Windows"

    ```powershell
    py -m venv .venv
    .venv\Scripts\python -m pip install OctoPrint
    .venv\Scripts\python -m pip install -e ".[develop]"
    ```

=== "macOS / Linux"

    ```bash
    python3 -m venv .venv
    .venv/bin/python -m pip install OctoPrint
    .venv/bin/python -m pip install -e ".[develop]"
    ```

## Run OctoPrint

Start a development instance with a separate basedir:

=== "Windows"

    ```powershell
    .venv\Scripts\octoprint serve --basedir .octoprint-dev
    ```

=== "macOS / Linux"

    ```bash
    .venv/bin/octoprint serve --basedir .octoprint-dev
    ```

Enable OctoPrint's bundled Virtual Printer plugin to produce lifecycle events
without printer hardware.

## Preview documentation

The docs scripts fetch the shared site design used by
OctoPrint-HomeAssistantPower.

=== "Windows"

    ```powershell
    .\scripts\docs-serve.ps1
    ```

=== "macOS / Linux"

    ```bash
    ./scripts/docs-serve.sh
    ```

Use the `-Build` or `--build` variant for the same strict build used in CI.

## Deploy to a test host

The PowerShell helper syncs the checkout, installs it in editable mode, and
restarts the OctoPrint service:

```powershell
.\scripts\deploy.ps1 -Target pi@octoprint.local
```

Read the script parameters before using a non-default virtual environment,
remote path, service name, or service user.
