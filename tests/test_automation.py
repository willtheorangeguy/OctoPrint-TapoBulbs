# coding=utf-8
import threading
import time

from octoprint_tapo_bulbs.automation import PrintLightController


class Recorder:
    def __init__(self):
        self.on = []
        self.off = []
        self.messages = []
        self.lock = threading.Lock()

    def turn_on(self, entity_id, brightness, kelvin):
        with self.lock:
            self.on.append((entity_id, brightness, kelvin))

    def turn_off(self, entity_id):
        with self.lock:
            self.off.append(entity_id)

    def notify(self, payload):
        with self.lock:
            self.messages.append(payload)


def wait_for(predicate, timeout=2):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(0.01)
    return False


def bulb(**overrides):
    result = {
        "entity_id": "light.printer",
        "on_print_start": True,
        "off_print_done": True,
        "off_print_failed": True,
        "off_print_cancelled": True,
        "brightness_pct": 90,
        "color_temp_kelvin": 5000,
    }
    result.update(overrides)
    return result


def build(recorder):
    return PrintLightController(
        recorder.turn_on, recorder.turn_off, recorder.notify
    )


def test_print_start_turns_on_selected_bulb_with_profile():
    recorder = Recorder()
    controller = build(recorder)
    assert controller.print_started([bulb()])
    assert wait_for(lambda: len(recorder.on) == 1)
    assert recorder.on == [("light.printer", 90, 5000)]


def test_print_start_skips_disabled_bulb():
    recorder = Recorder()
    controller = build(recorder)
    assert not controller.print_started([bulb(on_print_start=False)])
    assert recorder.on == []


def test_each_terminal_outcome_uses_its_setting():
    for outcome in ("done", "failed", "cancelled"):
        recorder = Recorder()
        controller = build(recorder)
        controller.print_started([])
        assert controller.print_ended([bulb()], outcome)
        assert wait_for(lambda: recorder.off == ["light.printer"])


def test_outcome_can_be_disabled():
    recorder = Recorder()
    controller = build(recorder)
    controller.print_started([])
    assert not controller.print_ended([bulb(off_print_failed=False)], "failed")
    assert recorder.off == []


def test_new_print_cancels_delayed_turn_off():
    recorder = Recorder()
    controller = build(recorder)
    controller.print_started([])
    controller.print_ended([bulb()], "done", delay=0.15)
    controller.print_started([])
    assert wait_for(
        lambda: any(message.get("state") == "cancelled" for message in recorder.messages)
    )
    assert recorder.off == []


def test_failure_is_reported_without_stopping_other_bulbs():
    recorder = Recorder()

    def fail_first(entity_id, brightness, kelvin):
        if entity_id == "light.bad":
            raise RuntimeError("unavailable")
        recorder.turn_on(entity_id, brightness, kelvin)

    controller = PrintLightController(fail_first, recorder.turn_off, recorder.notify)
    controller.print_started(
        [bulb(entity_id="light.bad"), bulb(entity_id="light.good")]
    )
    assert wait_for(lambda: len(recorder.messages) == 1)
    assert recorder.on == [("light.good", 90, 5000)]
    assert recorder.messages[0]["state"] == "failed"
    assert recorder.messages[0]["failures"][0]["entity_id"] == "light.bad"


def test_shutdown_cancels_delayed_action():
    recorder = Recorder()
    controller = build(recorder)
    controller.print_started([])
    controller.print_ended([bulb()], "done", delay=0.15)
    controller.shutdown()
    time.sleep(0.2)
    assert recorder.off == []
