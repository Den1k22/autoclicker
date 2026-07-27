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
    PointsSettings,
    PRESET_COUNT,
    UiSettings,
)


OBSOLETE_HOTKEY_OPTIONS = (
    "save_points_hotkey",
    "load_points_hotkey",
    "create_mesh_hotkey",
)
PRESET_SCOPED_SECTIONS = ("HOTKEYS", "DELAYS", "MESH", "CV", "POINTS")


def preset_section(index: int, section: str | None = None) -> str:
    if not 0 <= index < PRESET_COUNT:
        raise IndexError(index)
    base = f"PRESET_{index + 1}"
    return base if section is None else f"{base}.{section}"


class SettingsRepository:
    def __init__(self, path: Path, default_path: Path):
        self.path = Path(path)
        self.default_path = Path(default_path)
        self._active_preset = 0

    @property
    def active_preset(self) -> int:
        return self._active_preset

    def load(self) -> AppSettings:
        parser, changed = self._load_parser()
        self._active_preset = self._read_active_preset(parser)
        settings = self._to_model(parser, self._active_preset)
        if changed:
            self._write_parser(parser)
        return settings

    def load_preset(self, index: int) -> AppSettings:
        parser, changed = self._load_parser()
        settings = self._to_model(parser, index)
        if changed:
            self._write_parser(parser)
        return settings

    def load_defaults(self, index: int | None = None) -> AppSettings:
        target = self._active_preset if index is None else index
        return self._to_model(self._read_defaults_parser(), target)

    def preset_names(self) -> tuple[str, ...]:
        parser, changed = self._load_parser()
        names = tuple(parser.get(preset_section(index), "name") for index in range(PRESET_COUNT))
        if changed:
            self._write_parser(parser)
        return names

    def save(self, settings: AppSettings, preset_index: int | None = None) -> None:
        index = self._active_preset if preset_index is None else preset_index
        parser, _ = self._load_parser()

        parser.set("MAIN", "mode", "prod")
        parser.set("MAIN", "language", settings.ui.language)
        parser.set(preset_section(index), "name", settings.preset_name.strip())

        hotkey_section = preset_section(index, "HOTKEYS")
        for option in OBSOLETE_HOTKEY_OPTIONS:
            parser.remove_option(hotkey_section, option)
        for key, value in settings.hotkeys.as_dict().items():
            parser.set(hotkey_section, key, value)

        parser.set(preset_section(index, "DELAYS"), "delay_before", str(settings.delays.delay_before_ms))
        parser.set(preset_section(index, "DELAYS"), "delay_after", str(settings.delays.delay_after_ms))
        parser.set(preset_section(index, "MESH"), "amount_width", str(settings.mesh.amount_width))
        parser.set(preset_section(index, "MESH"), "amount_height", str(settings.mesh.amount_height))
        parser.set(preset_section(index, "POINTS"), "points_path", settings.points.points_path.strip())

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
        cv_section = preset_section(index, "CV")
        for key, value in cv_values.items():
            parser.set(cv_section, key, str(value))

        self._write_parser(parser)

    def set_active_preset(self, index: int) -> None:
        preset_section(index)
        parser, _ = self._load_parser()
        parser.set("MAIN", "active_preset", str(index + 1))
        self._write_parser(parser)
        self._active_preset = index

    def resolve_points_path(self, value: str) -> Path:
        path = Path(value.strip())
        if path.is_absolute():
            return path
        return self.path.parent / path

    def serialize_points_path(self, path: Path) -> str:
        resolved = Path(path).resolve()
        try:
            return str(resolved.relative_to(self.path.parent.resolve()))
        except ValueError:
            return str(resolved)

    def _load_parser(self) -> tuple[configparser.ConfigParser, bool]:
        defaults = self._read_defaults_parser()
        changed = False

        if self.path.exists():
            parser = self._read_parser(self.path)
            if not parser.has_section(preset_section(0)):
                self._migrate_legacy_sections(parser)
                changed = True
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

        for index in range(PRESET_COUNT):
            hotkey_section = preset_section(index, "HOTKEYS")
            for option in OBSOLETE_HOTKEY_OPTIONS:
                if parser.remove_option(hotkey_section, option):
                    changed = True

        return parser, changed

    def _read_defaults_parser(self) -> configparser.ConfigParser:
        parser = self._read_parser(self.default_path)
        for index in range(1, PRESET_COUNT):
            for section in PRESET_SCOPED_SECTIONS:
                source = preset_section(0, section)
                target = preset_section(index, section)
                if not parser.has_section(target):
                    parser.add_section(target)
                for key, value in parser.items(source):
                    if not parser.has_option(target, key):
                        parser.set(target, key, value)
        return parser

    @staticmethod
    def _migrate_legacy_sections(parser: configparser.ConfigParser) -> None:
        for section in PRESET_SCOPED_SECTIONS:
            if not parser.has_section(section):
                continue
            target = preset_section(0, section)
            if not parser.has_section(target):
                parser.add_section(target)
            for key, value in parser.items(section):
                parser.set(target, key, value)
            parser.remove_section(section)

    @staticmethod
    def _read_active_preset(parser: configparser.ConfigParser) -> int:
        try:
            value = parser.getint("MAIN", "active_preset", fallback=1)
        except ValueError as error:
            raise ValueError(f"Invalid settings file: {error}") from error
        if not 1 <= value <= PRESET_COUNT:
            raise ValueError(f"Invalid settings file: active_preset must be between 1 and {PRESET_COUNT}")
        return value - 1

    @staticmethod
    def _read_parser(path: Path) -> configparser.ConfigParser:
        parser = configparser.ConfigParser()
        if not path.is_file():
            raise FileNotFoundError(path)
        with path.open("r", encoding="utf-8") as file:
            parser.read_file(file)
        return parser

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
    def _to_model(parser: configparser.ConfigParser, index: int) -> AppSettings:
        try:
            hotkey_values = dict(parser.items(preset_section(index, "HOTKEYS")))
            hotkeys = HotkeySettings(
                **{field.name: hotkey_values[field.name] for field in fields(HotkeySettings)}
            )
            delays = DelaySettings(
                delay_before_ms=parser.getint(preset_section(index, "DELAYS"), "delay_before"),
                delay_after_ms=parser.getint(preset_section(index, "DELAYS"), "delay_after"),
            )
            mesh = MeshSettings(
                amount_width=parser.getint(preset_section(index, "MESH"), "amount_width"),
                amount_height=parser.getint(preset_section(index, "MESH"), "amount_height"),
            )
            cv_section = preset_section(index, "CV")
            cv = CvSettings(
                monitor_region_top=parser.getint(cv_section, "monitor_region_top"),
                monitor_region_left=parser.getint(cv_section, "monitor_region_left"),
                monitor_region_width=parser.getint(cv_section, "monitor_region_width"),
                monitor_region_height=parser.getint(cv_section, "monitor_region_height"),
                target_rgb_r=parser.getint(cv_section, "target_rgb_r"),
                target_rgb_g=parser.getint(cv_section, "target_rgb_g"),
                target_rgb_b=parser.getint(cv_section, "target_rgb_b"),
                delay_between_frames_ms=parser.getint(cv_section, "delay_between_frames"),
                click_cooldown_ms=parser.getint(cv_section, "click_cooldown"),
                second_click_delay_ms=parser.getint(cv_section, "second_click_delay"),
                first_action=parser.get(cv_section, "first_action"),
                second_action=parser.get(cv_section, "second_action"),
            )
            ui = UiSettings(language=parser.get("MAIN", "language", fallback="en").lower())
            points = PointsSettings(
                points_path=parser.get(preset_section(index, "POINTS"), "points_path")
            )
            name = parser.get(preset_section(index), "name")
        except (configparser.Error, KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid settings file: {error}") from error

        return AppSettings(
            hotkeys=hotkeys,
            delays=delays,
            mesh=mesh,
            cv=cv,
            ui=ui,
            preset_name=name,
            points=points,
        )
