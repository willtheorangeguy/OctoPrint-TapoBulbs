# Roadmap

The first release focuses on reliable on/off lifecycle lighting through Home
Assistant.

## Current release

- Multiple `light.*` entities
- Print start and three terminal event types
- Optional brightness and colour temperature
- Delayed turn-off with newer-print cancellation
- Navbar state and manual control
- Home Assistant REST discovery and polling

## Candidates

- Home Assistant WebSocket state subscriptions instead of polling
- Configurable turn-on and turn-off transitions
- Scene or script targets for complex camera-lighting setups
- State restoration for bulbs that were already on before a print
- Integration tests against a live OctoPrint development instance

Candidate items are not implemented contracts. Track accepted work in
[GitHub issues](https://github.com/willtheorangeguy/OctoPrint-TapoBulbs/issues).
