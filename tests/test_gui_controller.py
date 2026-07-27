from __future__ import annotations

import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from autoclicker.gui.controller import GuiController
from autoclicker.settings.model import DelaySettings, PointsSettings, UiSettings
from tests.factories import make_hotkeys, make_settings


def immediate(function, *args, **kwargs):
    return function(*args, **kwargs)


class GuiControllerTests(unittest.TestCase):
    def setUp(self):
        self.settings = make_settings()
        self.frame = mock.MagicMock()
        self.service = mock.MagicMock()
        self.service.settings = self.settings
        self.repository = mock.MagicMock()
        self.repository.active_preset = 0
        self.repository.resolve_points_path.return_value = Path("points.txt")
        self.repository.preset_names.return_value = tuple(f"Preset {index}" for index in range(1, 11))
        self.repository.load_defaults.return_value = self.settings
        self.keyboard = mock.MagicMock()
        self.keyboard.is_valid_combination.return_value = True
        self.actions = mock.MagicMock()
        self.actions.is_valid.return_value = True
        self.controller = GuiController(
            self.frame,
            self.service,
            self.repository,
            self.keyboard,
            self.actions,
            lambda message: message,
            call_after=immediate,
        )
        self.hotkeys = mock.MagicMock()
        self.controller.set_hotkey_manager(self.hotkeys)

    def test_valid_settings_are_registered_saved_and_applied(self):
        candidate = replace(self.settings, delays=DelaySettings(10, 20))
        self.frame.candidate_settings.return_value = candidate

        self.controller.on_apply_settings()

        self.hotkeys.apply.assert_called_once_with(candidate.hotkeys)
        self.repository.save.assert_called_once_with(candidate, 0)
        self.service.update_settings.assert_called_once_with(candidate)
        self.frame.show_info.assert_called_once_with("Settings applied successfully.")

    def test_save_failure_restores_previous_hotkeys(self):
        candidate = replace(self.settings, delays=DelaySettings(10, 20))
        self.frame.candidate_settings.return_value = candidate
        self.repository.save.side_effect = OSError("read only")

        self.controller.on_apply_settings()

        self.assertEqual(
            self.hotkeys.apply.call_args_list,
            [mock.call(candidate.hotkeys), mock.call(self.settings.hotkeys)],
        )
        self.service.update_settings.assert_not_called()
        self.frame.show_error.assert_called_once()

    def test_language_change_is_saved_without_restart_prompt(self):
        candidate = replace(self.settings, ui=UiSettings("ru"))
        self.frame.candidate_settings.return_value = candidate

        self.controller.on_apply_settings()

        self.repository.save.assert_called_once_with(candidate, 0)
        self.service.update_settings.assert_called_once_with(candidate)
        self.frame.Close.assert_not_called()
        self.frame.show_info.assert_called_once_with("Settings applied successfully.")

    def test_add_point_hotkey_does_not_invoke_mesh_creation(self):
        self.controller.hotkey_callbacks()["add_point_hotkey"]()

        self.service.record_current_point.assert_called_once_with()
        self.service.create_mesh.assert_not_called()

    def test_preset_hotkeys_map_one_through_nine_and_zero_to_ten(self):
        callbacks = self.controller.preset_hotkey_callbacks()

        with mock.patch.object(self.controller, "on_select_preset") as select:
            callbacks["ctrl+2"]()
            callbacks["ctrl+0"]()

        self.assertEqual(select.call_args_list, [mock.call(1), mock.call(9)])

    def test_switch_stops_automation_saves_dirty_points_and_loads_target(self):
        target = replace(
            self.settings,
            preset_name="Preset 2",
            points=PointsSettings("points_2.txt"),
        )
        self.service.stop_and_wait.return_value = True
        self.service.dirty = True
        self.repository.load_preset.return_value = target
        self.repository.resolve_points_path.return_value = Path("missing_points_2.txt")

        self.controller.on_select_preset(1)

        self.service.stop_and_wait.assert_called_once_with()
        self.service.save_points.assert_called_once_with()
        self.hotkeys.apply.assert_called_once_with(target.hotkeys)
        self.repository.set_active_preset.assert_called_once_with(1)
        self.service.update_settings.assert_called_once_with(target)
        self.service.replace_points_document.assert_called_once_with((), Path("missing_points_2.txt"))
        self.frame.set_preset.assert_called_once()

    def test_empty_dirty_point_list_does_not_prompt_on_close(self):
        self.service.dirty = True
        self.service.points.return_value = ()
        event = mock.Mock()

        self.controller.on_close(event)

        self.frame.confirm_discard_changes.assert_not_called()
        event.Skip.assert_called_once_with()

    def test_empty_dirty_point_list_does_not_prompt_before_load(self):
        self.service.dirty = True
        self.service.points.return_value = ()

        self.assertTrue(self.controller._confirm_replace_dirty_points())
        self.frame.confirm_discard_changes.assert_not_called()

    def test_invalid_duplicate_hotkeys_are_not_registered_or_saved(self):
        candidate = replace(
            self.settings,
            hotkeys=make_hotkeys(
                add_point_hotkey="ctrl+alt+x",
                remove_last_point_hotkey="ctrl+alt+x",
            ),
        )
        self.frame.candidate_settings.return_value = candidate

        self.controller.on_apply_settings()

        self.hotkeys.apply.assert_not_called()
        self.repository.save.assert_not_called()
        self.frame.settings_panel.hotkeys.set_errors.assert_called_once()

    def test_shutdown_is_idempotent(self):
        self.controller.shutdown()
        self.controller.shutdown()

        self.service.shutdown.assert_called_once_with()
        self.hotkeys.close.assert_called_once_with()
