---
layout: plugin

id: tapo_bulbs
title: Tapo Bulbs
description: Control Matter-connected Tapo bulbs through Home Assistant and automate lighting around OctoPrint jobs.
authors:
- William Vandergraaf
license: AGPLv3

date: 2026-09-06

homepage: https://github.com/willtheorangeguy/OctoPrint-TapoBulbs
source: https://github.com/willtheorangeguy/OctoPrint-TapoBulbs
archive: https://github.com/willtheorangeguy/OctoPrint-TapoBulbs/archive/v0.1.0.zip

tags:
- lighting
- home assistant
- matter
- tapo
- webcam
- automation

compatibility:
  octoprint:
  - 1.5.0

  os:
  - linux
  - windows
  - macos
  - freebsd

  python: ">=3.7,<4"

attributes:
- ai-developed

---

Turn Home Assistant light entities on when a print starts and off when it ends.
The plugin supports multiple bulbs, manual navbar control, optional brightness
and colour temperature, and a post-print delay. A newer print cancels an older
pending turn-off.

Home Assistant commissions the Tapo bulb over Matter. The plugin calls Home
Assistant's local REST API, so it stores no Tapo cloud credential or Matter
fabric key.

### Requirements

A reachable Home Assistant instance, a long-lived access token, and a
Matter-compatible Tapo bulb exposed as a `light.*` entity.

### Note on AI assistance

This plugin was written with AI assistance and is marked `ai-developed`
accordingly. It is maintained by a human who reads and understands the code.
