from __future__ import annotations

import unittest
from unittest import mock

from autoclicker.adapters.actions import ActionDispatcher
from autoclicker.adapters.keyboard import (
    HotkeyManager,
    HotkeyRegistrationError,
    KeyboardAdapter,
)
from autoclicker.adapters.mouse import MouseAdapter
from tests.factories import make_hotkeys


class ActionDispatcherTests(unittest.TestCase):
    def setUp(self):
        self.keyboard = mock.Mock()
        self.mouse = mock.Mock()
        self.dispatcher = ActionDispatcher(self.keyboard, self.mouse)

    def test_keyboard_and_mouse_actions_are_dispatched(self):
        self.keyboard.is_valid_combination.return_value = True
        self.dispatcher.execute("ctrl+shift+a")
        self.keyboard.press_and_release.assert_called_once_with("ctrl+shift+a")

        self.keyboard.reset_mock()
        self.keyboard.is_valid_combination.return_value = False
        self.mouse.is_valid_button.return_value = True
        self.dispatcher.execute(" X2_BUTTON ")
        self.mouse.click_button.assert_called_once_with("x2_button")

    def test_invalid_action_is_rejected(self):
        self.keyboard.is_valid_combination.return_value = False
        self.mouse.is_valid_button.return_value = False
        with self.assertRaises(ValueError):
            self.dispatcher.parse("not-an-action")


class MouseAdapterTests(unittest.TestCase):
    def test_supported_buttons_are_forwarded_to_controller(self):
        controller = mock.Mock()
        adapter = MouseAdapter(controller)

        adapter.click_button("RIGHT_BUTTON")

        controller.click.assert_called_once()
        self.assertTrue(adapter.is_valid_button("x1_button"))
        self.assertFalse(adapter.is_valid_button("wheel"))


class KeyboardAdapterTests(unittest.TestCase):
    @mock.patch("autoclicker.adapters.keyboard.keyboard_library.add_hotkey")
    def test_global_hotkeys_are_suppressed_from_focused_gui_controls(self, add_hotkey):
        callback = mock.Mock()

        KeyboardAdapter().add_hotkey("ctrl+alt+space", callback)

        add_hotkey.assert_called_once_with("ctrl+alt+space", callback, suppress=True)


class HotkeyManagerTests(unittest.TestCase):
    def setUp(self):
        self.adapter = mock.Mock()
        self.callbacks = {name: mock.Mock() for name in make_hotkeys().as_dict()}
        self.manager = HotkeyManager(self.adapter, self.callbacks)

    def test_registers_every_configured_hotkey_and_closes_cleanly(self):
        hotkeys = make_hotkeys()

        self.manager.apply(hotkeys)
        self.adapter.remove_all_hotkeys.assert_not_called()
        self.manager.close()

        self.assertEqual(self.adapter.add_hotkey.call_count, len(hotkeys.as_dict()))
        self.adapter.remove_all_hotkeys.assert_called_once_with()

    def test_fixed_preset_hotkeys_are_registered_with_every_active_set(self):
        fixed = {"ctrl+1": mock.Mock(), "ctrl+0": mock.Mock()}
        manager = HotkeyManager(self.adapter, self.callbacks, fixed)

        manager.apply(make_hotkeys())

        registered = [call.args[0] for call in self.adapter.add_hotkey.call_args_list]
        self.assertIn("ctrl+1", registered)
        self.assertIn("ctrl+0", registered)

    def test_closing_before_successful_registration_does_not_clear_uninitialized_listener(self):
        self.manager.close()

        self.adapter.remove_all_hotkeys.assert_not_called()

    def test_failed_replacement_rolls_back_previous_set(self):
        previous = make_hotkeys()
        replacement = make_hotkeys(add_point_hotkey="ctrl+alt+x")
        self.manager.apply(previous)
        self.adapter.add_hotkey.reset_mock()
        self.adapter.add_hotkey.side_effect = [RuntimeError("failure")] + [None] * len(previous.as_dict())

        with self.assertRaises(HotkeyRegistrationError):
            self.manager.apply(replacement)

        self.assertEqual(self.manager.current, previous)
        self.assertEqual(self.adapter.add_hotkey.call_count, len(previous.as_dict()) + 1)
