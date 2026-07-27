from __future__ import annotations

import time
from collections.abc import Callable
from threading import Event

from autoclicker.helpers.time import milliseconds_to_seconds
from autoclicker.settings.model import CvSettings


def run_cv(
    stop_event: Event,
    settings: CvSettings,
    capture_factory: Callable,
    execute_action: Callable[[str], None],
    clock: Callable[[], float] = time.time,
) -> None:
    last_click = 0.0
    awaiting_second_action = False
    second_action_time = 0.0
    frame_delay = milliseconds_to_seconds(settings.delay_between_frames_ms)
    cooldown = milliseconds_to_seconds(settings.click_cooldown_ms)
    second_delay = milliseconds_to_seconds(settings.second_click_delay_ms)

    with capture_factory() as capture:
        while not stop_event.is_set():
            detected = capture.has_exact_color(settings.monitor_region, settings.target_bgr)
            now = clock()

            if detected and now - last_click >= cooldown:
                execute_action(settings.first_action)
                last_click = now
                awaiting_second_action = True
                second_action_time = now + second_delay

            if awaiting_second_action and now >= second_action_time:
                execute_action(settings.second_action)
                awaiting_second_action = False

            stop_event.wait(frame_delay)
