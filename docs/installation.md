# Installation

<!-- markdownlint-disable MD046 -->
<!-- Material content tabs require indentation around fenced code blocks. -->

Install OctoPrint-TapoBulbs through Plugin Manager or from a local checkout.

## Requirements

The plugin supports Python 3.7 through 3.x and OctoPrint 1.5.0 or newer. It adds
no runtime dependency because OctoPrint already provides `requests`.

=== "Plugin Manager URL"

    Open **Settings -> Plugin Manager -> Get More** and paste:

    ```text
    https://github.com/willtheorangeguy/OctoPrint-TapoBulbs/archive/v0.1.0.zip
    ```

=== "Local checkout"

    Install the checkout into the same virtual environment as OctoPrint:

    ```bash
    pip install -e .
    ```

## Verify the installation

Restart OctoPrint. **Tapo Bulbs** appears in the settings list and a lightbulb
icon appears in the navbar.

For a command-line check, run this inside OctoPrint's virtual environment:

```bash
pip show OctoPrint-TapoBulbs
```

The output contains:

```text
Name: OctoPrint-TapoBulbs
Version: 0.1.0
```

## Upgrading

Use **Settings -> Software Update** after a GitHub release becomes available.
The plugin's update hook tracks releases from the `OctoPrint-TapoBulbs`
repository.

## Uninstalling

Open **Settings -> Plugin Manager**, find **OctoPrint-TapoBulbs**, and press the
trash icon. Uninstalling the plugin does not remove the bulb from Home
Assistant's Matter fabric.
