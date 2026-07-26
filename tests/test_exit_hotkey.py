import os
import sys
import unittest
from unittest import mock


CODE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "code"))
if CODE_PATH not in sys.path:
    sys.path.insert(0, CODE_PATH)

import autoclicker  # noqa: E402
import hotkeys_storage  # noqa: E402


class ExitHotkeyTests(unittest.TestCase):

    def test_exit_callback_stops_work_and_signals_main(self):
        thread_controller = mock.Mock()
        exit_event = mock.Mock()

        autoclicker.on_exit(thread_controller, exit_event)

        thread_controller.change_state.assert_called_once_with(False)
        exit_event.set.assert_called_once_with()

    def test_exit_hotkey_does_not_block_later_registrations(self):
        thread_controller = mock.Mock()
        exit_event = mock.Mock()
        hotkeys = {
            hotkeys_storage.ADD_POINT_HOTKEY: "ctrl+alt+space",
            hotkeys_storage.EXIT_HOTKEY: "ctrl+alt+q",
            hotkeys_storage.START_STOP_CV_HOTKEY: "ctrl+alt+v"
        }

        with mock.patch.object(autoclicker.hotkeys_storage, "get_all_available_hotkeys", return_value=hotkeys), \
                mock.patch.object(autoclicker.keyboard_controller, "add_hotkey") as add_hotkey:
            autoclicker.set_hotkeys(thread_controller, exit_event)

        self.assertEqual(add_hotkey.call_count, 3)
        add_hotkey.assert_any_call(
            "ctrl+alt+q",
            autoclicker.on_exit,
            args=(thread_controller, exit_event)
        )
        add_hotkey.assert_any_call(
            "ctrl+alt+v",
            autoclicker.on_start_stop_cv,
            args=(thread_controller,)
        )

    def test_main_waits_and_cleans_up_keyboard_hooks(self):
        exit_event = mock.Mock()

        with mock.patch.object(autoclicker.threading, "Event", return_value=exit_event), \
                mock.patch.object(autoclicker, "is_settings_valid", return_value=True), \
                mock.patch.object(autoclicker, "load_hotkeys_from_settings", return_value=True), \
                mock.patch.object(autoclicker, "set_hotkeys") as set_hotkeys, \
                mock.patch.object(autoclicker.keyboard_controller, "remove_all_hotkeys") as remove_all_hotkeys:
            autoclicker.main()

        set_hotkeys.assert_called_once_with(mock.ANY, exit_event)
        exit_event.wait.assert_called_once_with()
        remove_all_hotkeys.assert_called_once_with()

    def test_main_cleans_up_when_waiting_fails(self):
        exit_event = mock.Mock()
        exit_event.wait.side_effect = KeyboardInterrupt

        with mock.patch.object(autoclicker.threading, "Event", return_value=exit_event), \
                mock.patch.object(autoclicker, "is_settings_valid", return_value=True), \
                mock.patch.object(autoclicker, "load_hotkeys_from_settings", return_value=True), \
                mock.patch.object(autoclicker, "set_hotkeys"), \
                mock.patch.object(autoclicker.keyboard_controller, "remove_all_hotkeys") as remove_all_hotkeys:
            with self.assertRaises(KeyboardInterrupt):
                autoclicker.main()

        remove_all_hotkeys.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
