from __future__ import annotations

import tempfile
import threading
import time
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from autoclicker.automation.cv import run_cv
from autoclicker.automation.points import Point
from autoclicker.automation.service import AutomationError, AutomationService, RunMode
from autoclicker.settings.model import DelaySettings
from tests.factories import make_settings


class FakeMouse:
    def __init__(self):
        self.position = (12, 34)
        self.moves = []
        self.clicks = 0

    def get_position(self):
        return self.position

    def set_position(self, x, y):
        self.moves.append((x, y))

    def click_left(self):
        self.clicks += 1


class AutomationServiceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.mouse = FakeMouse()
        self.actions = mock.Mock()
        self.service = AutomationService(
            make_settings(delays=DelaySettings(0, 0)),
            self.mouse,
            self.actions,
            capture_factory=mock.Mock(),
            default_points_path=Path(self.directory.name) / "points.txt",
        )

    def tearDown(self):
        self.service.shutdown()
        self.directory.cleanup()

    def wait_until_idle(self):
        deadline = time.monotonic() + 2
        while self.service.mode != RunMode.IDLE and time.monotonic() < deadline:
            time.sleep(0.005)
        self.assertEqual(self.service.mode, RunMode.IDLE)

    def test_record_run_once_and_save_use_the_shared_service(self):
        self.service.record_current_point()

        self.assertTrue(self.service.start_points_once())
        self.wait_until_idle()
        path = self.service.save_points()

        self.assertEqual(self.mouse.moves, [(12, 34)])
        self.assertEqual(self.mouse.clicks, 1)
        self.assertTrue(path.is_file())
        self.assertFalse(self.service.dirty)

    def test_start_requires_points(self):
        with self.assertRaises(AutomationError) as context:
            self.service.start_points_once()
        self.assertEqual(context.exception.code, "no_points")

    def test_modes_are_mutually_exclusive_and_stop_is_responsive(self):
        self.service.update_settings(
            replace(self.service.settings, delays=DelaySettings(10_000, 10_000))
        )
        self.service.record_current_point()

        self.assertTrue(self.service.start_points_continuous())
        self.assertFalse(self.service.start_cv())
        self.assertTrue(self.service.stop())
        self.wait_until_idle()
        self.assertEqual(self.mouse.clicks, 0)

    def test_point_edits_do_not_change_active_snapshot(self):
        self.service.record_current_point()
        original = self.service.points()[0]
        self.assertTrue(self.service.start_points_once())
        self.service.update_point(0, Point(99, 99, 0, 0))
        self.wait_until_idle()

        self.assertEqual(self.mouse.moves[0], (original.x, original.y))
        self.assertEqual(self.service.points()[0].x, 99)


class CvRunnerTests(unittest.TestCase):
    def test_exact_detection_dispatches_delayed_second_action_without_new_detection(self):
        stop_event = threading.Event()
        capture = mock.MagicMock()
        capture.__enter__.return_value = capture
        capture.has_exact_color.side_effect = [True, False]

        times = iter((1.0, 2.1))

        def clock():
            value = next(times)
            if value == 2.1:
                stop_event.set()
            return value

        execute = mock.Mock()
        run_cv(
            stop_event,
            make_settings().cv,
            capture_factory=lambda: capture,
            execute_action=execute,
            clock=clock,
        )

        self.assertEqual(
            execute.call_args_list,
            [mock.call("space"), mock.call("space")],
        )
