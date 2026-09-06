# coding=utf-8
"""Background print-lifecycle automation for configured bulbs."""

from __future__ import absolute_import, unicode_literals

import logging
import threading


class PrintLightController(object):
    """Turn configured bulbs on and off without blocking OctoPrint's event bus."""

    def __init__(self, turn_on, turn_off, notify, logger=None):
        self._turn_on = turn_on
        self._turn_off = turn_off
        self._notify = notify
        self._logger = logger or logging.getLogger(__name__)
        self._lock = threading.Lock()
        self._generation = 0
        self._shutdown = threading.Event()

    def print_started(self, bulbs):
        """Cancel stale delayed shutdowns and turn on selected bulbs."""
        with self._lock:
            self._generation += 1
            generation = self._generation
        selected = [bulb for bulb in bulbs if bulb.get("on_print_start", True)]
        return self._spawn("on", selected, generation, 0)

    def print_ended(self, bulbs, outcome, delay=0):
        """Turn off bulbs selected for this terminal print outcome."""
        setting = {
            "done": "off_print_done",
            "failed": "off_print_failed",
            "cancelled": "off_print_cancelled",
        }.get(outcome)
        if setting is None:
            return False
        with self._lock:
            generation = self._generation
        selected = [bulb for bulb in bulbs if bulb.get(setting, True)]
        return self._spawn("off", selected, generation, max(float(delay or 0), 0))

    def shutdown(self):
        """Prevent pending delayed actions from executing during shutdown."""
        self._shutdown.set()
        with self._lock:
            self._generation += 1

    def _spawn(self, action, bulbs, generation, delay):
        if not bulbs:
            return False
        worker = threading.Thread(
            target=self._run,
            args=(action, bulbs, generation, delay),
            name="tapo_bulbs_{}".format(action),
        )
        worker.daemon = True
        worker.start()
        return True

    def _run(self, action, bulbs, generation, delay):
        if delay and self._shutdown.wait(delay):
            return
        with self._lock:
            if generation != self._generation:
                self._notify(
                    {
                        "type": "automation",
                        "action": action,
                        "state": "cancelled",
                        "detail": "A newer print superseded this light action.",
                    }
                )
                return

        failures = []
        for bulb in bulbs:
            entity_id = bulb["entity_id"]
            try:
                if action == "on":
                    self._turn_on(
                        entity_id,
                        bulb.get("brightness_pct"),
                        bulb.get("color_temp_kelvin"),
                    )
                else:
                    self._turn_off(entity_id)
            except Exception as exc:
                self._logger.exception("Could not turn %s %s", action, entity_id)
                failures.append({"entity_id": entity_id, "error": str(exc)})

        self._notify(
            {
                "type": "automation",
                "action": action,
                "state": "failed" if failures else "done",
                "failures": failures,
            }
        )
