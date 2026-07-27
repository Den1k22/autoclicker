from __future__ import annotations

import configparser
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from autoclicker.helpers.paths import default_settings_path
from autoclicker.settings import (
    DelaySettings,
    MeshSettings,
    SettingsRepository,
    SettingsValidationError,
    UiSettings,
    validate_settings,
)
from tests.factories import make_hotkeys, make_settings


class SettingsRepositoryTests(unittest.TestCase):
    def test_missing_settings_file_is_created_from_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config" / "settings.ini"
            repository = SettingsRepository(path, default_settings_path())

            settings = repository.load()

            self.assertTrue(path.is_file())
            self.assertEqual(settings.ui.language, "en")
            self.assertEqual(settings.hotkeys.exit_hotkey, "ctrl+alt+q")

    def test_existing_file_is_migrated_without_losing_unknown_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.ini"
            path.write_text(
                "[MAIN]\nMODE = prod\n"
                "[HOTKEYS]\nadd_point_hotkey = ctrl+alt+x\n"
                "save_points_hotkey = ctrl+alt+s\n"
                "load_points_hotkey = ctrl+alt+l\n"
                "create_mesh_hotkey = ctrl+alt+m\n"
                "[DELAYS]\ndelay_before = 75\n"
                "[MESH]\namount_width = 4\n"
                "[CV]\nmonitor_region_top = 1\n"
                "[CUSTOM]\nkeep_me = yes\n",
                encoding="utf-8",
            )
            repository = SettingsRepository(path, default_settings_path())

            settings = repository.load()
            parser = configparser.ConfigParser()
            parser.read(path, encoding="utf-8")

            self.assertEqual(settings.hotkeys.add_point_hotkey, "ctrl+alt+x")
            self.assertEqual(settings.delays.delay_before_ms, 75)
            self.assertEqual(parser.get("CUSTOM", "keep_me"), "yes")
            self.assertTrue(parser.has_option("HOTKEYS", "exit_hotkey"))
            self.assertFalse(parser.has_option("HOTKEYS", "save_points_hotkey"))
            self.assertFalse(parser.has_option("HOTKEYS", "load_points_hotkey"))
            self.assertFalse(parser.has_option("HOTKEYS", "create_mesh_hotkey"))
            self.assertEqual(parser.get("MAIN", "language"), "en")

    def test_round_trip_save_updates_all_typed_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.ini"
            repository = SettingsRepository(path, default_settings_path())
            initial = repository.load_defaults()
            changed = replace(
                initial,
                delays=DelaySettings(123, 456),
                mesh=MeshSettings(7, 8),
                ui=UiSettings("ru"),
            )

            repository.save(changed)

            self.assertEqual(repository.load(), changed)


class SettingsValidationTests(unittest.TestCase):
    def test_valid_settings_are_accepted(self):
        validate_settings(
            make_settings(),
            hotkey_validator=lambda value: bool(value),
            action_validator=lambda value: value == "space",
        )

    def test_numeric_boundaries_and_language_are_validated(self):
        invalid = make_settings(
            delays=DelaySettings(-1, 0),
            mesh=MeshSettings(1, 2),
            ui=UiSettings("de"),
        )

        with self.assertRaises(SettingsValidationError) as context:
            validate_settings(invalid)

        self.assertIn("delay_before", context.exception.errors)
        self.assertIn("amount_width", context.exception.errors)
        self.assertIn("language", context.exception.errors)

    def test_duplicate_and_invalid_hotkeys_are_rejected(self):
        invalid = make_settings(
            hotkeys=make_hotkeys(
                add_point_hotkey="not-valid",
                remove_last_point_hotkey="CTRL+ALT+C",
                remove_all_points_hotkey="ctrl+alt+c",
            )
        )

        with self.assertRaises(SettingsValidationError) as context:
            validate_settings(invalid, hotkey_validator=lambda value: value != "not-valid")

        self.assertIn("add_point_hotkey", context.exception.errors)
        self.assertIn("remove_all_points_hotkey", context.exception.errors)
