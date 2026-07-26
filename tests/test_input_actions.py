import os
import sys
import unittest
from unittest import mock


CODE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "code"))
if CODE_PATH not in sys.path:
    sys.path.insert(0, CODE_PATH)

import action_controller  # noqa: E402
import cv_controller  # noqa: E402
import keyboard_controller  # noqa: E402
import mouse_controller  # noqa: E402
import settings  # noqa: E402


class KeyboardControllerTests(unittest.TestCase):

    def test_accepts_single_keys_and_combinations(self):
        self.assertTrue(keyboard_controller.is_valid_key("space"))
        self.assertTrue(keyboard_controller.is_valid_key("f5"))
        self.assertTrue(keyboard_controller.is_valid_key("ctrl+shift+a"))

    def test_rejects_invalid_keys_and_sequences(self):
        self.assertFalse(keyboard_controller.is_valid_key(""))
        self.assertFalse(keyboard_controller.is_valid_key("not-a-real-key"))
        self.assertFalse(keyboard_controller.is_valid_key("a,b"))

    def test_hotkey_registration_is_delegated(self):
        callback = mock.Mock()
        with mock.patch.object(keyboard_controller.keyboard, "add_hotkey", return_value="hook") as add_hotkey:
            result = keyboard_controller.add_hotkey("ctrl+alt+v", callback, args=("argument",))

        self.assertEqual(result, "hook")
        add_hotkey.assert_called_once_with("ctrl+alt+v", callback, args=("argument",))

    def test_hotkey_cleanup_is_delegated(self):
        with mock.patch.object(keyboard_controller.keyboard, "remove_all_hotkeys") as remove_all_hotkeys:
            keyboard_controller.remove_all_hotkeys()

        remove_all_hotkeys.assert_called_once_with()


class MouseControllerTests(unittest.TestCase):

    def test_supports_all_configurable_buttons(self):
        for button in ("left_button", "right_button", "middle_button", "x1_button", "x2_button"):
            with self.subTest(button=button):
                self.assertTrue(mouse_controller.is_valid_button(button))

    def test_click_button_uses_pynput_controller(self):
        with mock.patch.object(mouse_controller.mouse_controller, "click") as click:
            mouse_controller.click_button("RIGHT_BUTTON")

        click.assert_called_once_with(mouse_controller.mouse.Button.right, 1)

    def test_click_button_rejects_invalid_values(self):
        for button in (None, "", "wheel"):
            with self.subTest(button=button):
                with self.assertRaises(ValueError):
                    mouse_controller.click_button(button)

    def test_left_click_compatibility_wrapper(self):
        with mock.patch.object(mouse_controller, "click_button") as click_button:
            mouse_controller.click_left_button(2)

        click_button.assert_called_once_with("left_button", 2)


class ActionControllerTests(unittest.TestCase):

    def test_defaults_preserve_space_actions(self):
        self.assertEqual(settings.DEFAULTS["CV"]["first_action"], "space")
        self.assertEqual(settings.DEFAULTS["CV"]["second_action"], "space")

    def test_keyboard_action_dispatch(self):
        with mock.patch.object(keyboard_controller, "press_and_release") as press:
            action_controller.execute_action(" ctrl+shift+a ")

        press.assert_called_once_with("ctrl+shift+a")

    def test_mouse_action_dispatch(self):
        with mock.patch.object(mouse_controller, "click_button") as click:
            action_controller.execute_action(" X2_BUTTON ")

        click.assert_called_once_with("x2_button")

    def test_rejects_invalid_actions(self):
        invalid_actions = (
            "",
            "keyboard:space",
            "mouse:left",
            "wheel_button",
            "not-a-real-key",
            "a,b"
        )

        for action in invalid_actions:
            with self.subTest(action=action):
                with self.assertRaises(ValueError):
                    action_controller.parse_action(action)


class CvActionTests(unittest.TestCase):

    def test_cv_runner_dispatches_first_and_second_actions(self):
        screen_capture = mock.MagicMock()
        screen_capture.__enter__.return_value = screen_capture
        thread_controller = mock.MagicMock()
        thread_controller.is_working.side_effect = (True, True, False)

        with mock.patch.object(cv_controller.mss, "mss", return_value=screen_capture), \
                mock.patch.object(cv_controller.np, "array", return_value=object()), \
                mock.patch.object(cv_controller.cv2, "cvtColor", return_value=object()), \
                mock.patch.object(cv_controller.cv2, "inRange", return_value=object()), \
                mock.patch.object(cv_controller.cv2, "findContours",
                                  side_effect=((["contour"], None), ([], None))), \
                mock.patch.object(cv_controller.time, "time", side_effect=(1.0, 2.1)), \
                mock.patch.object(cv_controller.time, "sleep"), \
                mock.patch.object(cv_controller.action_controller, "execute_action") as execute:
            cv_controller.cv_runner(thread_controller)

        self.assertEqual(
            execute.call_args_list,
            [mock.call(cv_controller.first_action), mock.call(cv_controller.second_action)]
        )


if __name__ == "__main__":
    unittest.main()
