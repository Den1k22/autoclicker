from __future__ import annotations

import configparser
import os
import tempfile
from dataclasses import fields
from pathlib import Path

from autoclicker.settings.model import (
    AppSettings,
    CvSettings,
    DelaySettings,
    HotkeySettings,
    MeshSettings,
    UiSettings,
)


OBSOLETE_HOTKEY_OPTIONS = (
    "save_points_hotkey",
    "load_points_hotkey",
    "create_mesh_hotkey",
)


class SettingsRepository:
    def __init__(self, path: Path, default_path: Path):
        self.path = Path(path)
        self.default_path = Path(default_path)

    def load(self) -> AppSettings:
        defaults = self._read_parser(self.default_path)
        changed = False

        if self.path.exists():
            parser = self._read_parser(self.path)
        else:
            parser = configparser.ConfigParser()
            changed = True

        for section in defaults.sections():
            if not parser.has_section(section):
                parser.add_section(section)
                changed = True
            for key, value in defaults.items(section):
                if not parser.has_option(section, key):
                    parser.set(section, key, value)
                    changed = True

        for option in OBSOLETE_HOTKEY_OPTIONS:
            if parser.remove_option("HOTKEYS", option):
                changed = True

        settings = self._to_model(parser)
        if changed:
            self._write_parser(parser)
        return settings

    def load_defaults(self) -> AppSettings:
        return self._to_model(self._read_parser(self.default_path))

    def save(self, settings: AppSettings) -> None:
        parser = self._read_parser(self.path) if self.path.exists() else configparser.ConfigParser()
        self._ensure_sections(parser)

        parser.set("MAIN", "MODE", "prod")
        parser.set("MAIN", "language", settings.ui.language)

        for option in OBSOLETE_HOTKEY_OPTIONS:
            parser.remove_option("HOTKEYS", option)
        for key, value in settings.hotkeys.as_dict().items():
            parser.set("HOTKEYS", key, value)

        parser.set("DELAYS", "delay_before", str(settings.delays.delay_before_ms))
        parser.set("DELAYS", "delay_after", str(settings.delays.delay_after_ms))
        parser.set("MESH", "amount_width", str(settings.mesh.amount_width))
        parser.set("MESH", "amount_height", str(settings.mesh.amount_height))

        cv_values = {
            "monitor_region_top": settings.cv.monitor_region_top,
            "monitor_region_left": settings.cv.monitor_region_left,
            "monitor_region_width": settings.cv.monitor_region_width,
            "monitor_region_height": settings.cv.monitor_region_height,
            "target_rgb_r": settings.cv.target_rgb_r,
            "target_rgb_g": settings.cv.target_rgb_g,
            "target_rgb_b": settings.cv.target_rgb_b,
            "delay_between_frames": settings.cv.delay_between_frames_ms,
            "click_cooldown": settings.cv.click_cooldown_ms,
            "second_click_delay": settings.cv.second_click_delay_ms,
            "first_action": settings.cv.first_action,
            "second_action": settings.cv.second_action,
        }
        for key, value in cv_values.items():
            parser.set("CV", key, str(value))

        self._write_parser(parser)

    @staticmethod
    def _read_parser(path: Path) -> configparser.ConfigParser:
        parser = configparser.ConfigParser()
        if not path.is_file():
            raise FileNotFoundError(path)
        with path.open("r", encoding="utf-8") as file:
            parser.read_file(file)
        return parser

    @staticmethod
    def _ensure_sections(parser: configparser.ConfigParser) -> None:
        for section in ("MAIN", "HOTKEYS", "DELAYS", "MESH", "CV"):
            if not parser.has_section(section):
                parser.add_section(section)

    def _write_parser(self, parser: configparser.ConfigParser) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                newline="",
                delete=False,
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
            ) as temporary:
                parser.write(temporary)
                temporary.flush()
                os.fsync(temporary.fileno())
                temporary_path = Path(temporary.name)
            os.replace(temporary_path, self.path)
        except OSError:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise

    @staticmethod
    def _to_model(parser: configparser.ConfigParser) -> AppSettings:
        try:
            hotkey_values = dict(parser.items("HOTKEYS"))
            hotkeys = HotkeySettings(
                **{field.name: hotkey_values[field.name] for field in fields(HotkeySettings)}
            )
            delays = DelaySettings(
                delay_before_ms=parser.getint("DELAYS", "delay_before"),
                delay_after_ms=parser.getint("DELAYS", "delay_after"),
            )
            mesh = MeshSettings(
                amount_width=parser.getint("MESH", "amount_width"),
                amount_height=parser.getint("MESH", "amount_height"),
            )
            cv = CvSettings(
                monitor_region_top=parser.getint("CV", "monitor_region_top"),
                monitor_region_left=parser.getint("CV", "monitor_region_left"),
                monitor_region_width=parser.getint("CV", "monitor_region_width"),
                monitor_region_height=parser.getint("CV", "monitor_region_height"),
                target_rgb_r=parser.getint("CV", "target_rgb_r"),
                target_rgb_g=parser.getint("CV", "target_rgb_g"),
                target_rgb_b=parser.getint("CV", "target_rgb_b"),
                delay_between_frames_ms=parser.getint("CV", "delay_between_frames"),
                click_cooldown_ms=parser.getint("CV", "click_cooldown"),
                second_click_delay_ms=parser.getint("CV", "second_click_delay"),
                first_action=parser.get("CV", "first_action"),
                second_action=parser.get("CV", "second_action"),
            )
            ui = UiSettings(language=parser.get("MAIN", "language", fallback="en").lower())
        except (configparser.Error, KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid settings file: {error}") from error

        return AppSettings(hotkeys=hotkeys, delays=delays, mesh=mesh, cv=cv, ui=ui)
