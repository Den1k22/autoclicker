from __future__ import annotations

from dataclasses import replace

from autoclicker.settings.model import (
    AppSettings,
    CvSettings,
    DelaySettings,
    HotkeySettings,
    MeshSettings,
    PointsSettings,
    UiSettings,
)


def make_hotkeys(**overrides) -> HotkeySettings:
    values = {
        "add_point_hotkey": "ctrl+alt+space",
        "remove_last_point_hotkey": "ctrl+alt+z",
        "remove_all_points_hotkey": "ctrl+alt+c",
        "start_autoclicker_hotkey": "ctrl+alt+[",
        "stop_autoclicker_hotkey": "ctrl+alt+]",
        "one_autoclick_run_hotkey": "ctrl+alt+\\",
        "start_stop_cv_hotkey": "ctrl+alt+v",
        "exit_hotkey": "ctrl+alt+q",
    }
    values.update(overrides)
    return HotkeySettings(**values)


def make_settings(**overrides) -> AppSettings:
    settings = AppSettings(
        hotkeys=make_hotkeys(),
        delays=DelaySettings(50, 50),
        mesh=MeshSettings(3, 3),
        cv=CvSettings(
            monitor_region_top=10,
            monitor_region_left=20,
            monitor_region_width=100,
            monitor_region_height=50,
            target_rgb_r=188,
            target_rgb_g=255,
            target_rgb_b=71,
            delay_between_frames_ms=0,
            click_cooldown_ms=500,
            second_click_delay_ms=1000,
            first_action="space",
            second_action="space",
        ),
        ui=UiSettings("en"),
        preset_name="Preset 1",
        points=PointsSettings("points.txt"),
    )
    return replace(settings, **overrides)
