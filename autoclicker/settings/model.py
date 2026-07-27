from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Callable, Mapping


SUPPORTED_LANGUAGES = ("en", "ru")
PRESET_COUNT = 10
PRESET_SWITCH_HOTKEYS = (
    "ctrl+1",
    "ctrl+2",
    "ctrl+3",
    "ctrl+4",
    "ctrl+5",
    "ctrl+6",
    "ctrl+7",
    "ctrl+8",
    "ctrl+9",
    "ctrl+0",
)


def N_(message: str) -> str:
    """Mark a deferred string for catalog extraction."""
    return message


def normalize_hotkey(value: str) -> str:
    aliases = {"control": "ctrl"}
    tokens = (
        aliases.get(token.strip().casefold(), token.strip().casefold())
        for token in value.split("+")
    )
    return "+".join(sorted(tokens))


HOTKEY_LABELS = {
    "add_point_hotkey": N_("Add point"),
    "remove_last_point_hotkey": N_("Remove last point"),
    "remove_all_points_hotkey": N_("Remove all points"),
    "start_autoclicker_hotkey": N_("Start continuous clicking"),
    "stop_autoclicker_hotkey": N_("Stop automation"),
    "one_autoclick_run_hotkey": N_("Run points once"),
    "start_stop_cv_hotkey": N_("Start or stop computer vision"),
    "exit_hotkey": N_("Exit application"),
}


@dataclass(frozen=True, slots=True)
class HotkeySettings:
    add_point_hotkey: str
    remove_last_point_hotkey: str
    remove_all_points_hotkey: str
    start_autoclicker_hotkey: str
    stop_autoclicker_hotkey: str
    one_autoclick_run_hotkey: str
    start_stop_cv_hotkey: str
    exit_hotkey: str

    def as_dict(self) -> dict[str, str]:
        return {field.name: getattr(self, field.name) for field in fields(self)}


@dataclass(frozen=True, slots=True)
class DelaySettings:
    delay_before_ms: int
    delay_after_ms: int


@dataclass(frozen=True, slots=True)
class MeshSettings:
    amount_width: int
    amount_height: int


@dataclass(frozen=True, slots=True)
class CvSettings:
    monitor_region_top: int
    monitor_region_left: int
    monitor_region_width: int
    monitor_region_height: int
    target_rgb_r: int
    target_rgb_g: int
    target_rgb_b: int
    delay_between_frames_ms: int
    click_cooldown_ms: int
    second_click_delay_ms: int
    first_action: str
    second_action: str

    @property
    def monitor_region(self) -> dict[str, int]:
        return {
            "top": self.monitor_region_top,
            "left": self.monitor_region_left,
            "width": self.monitor_region_width,
            "height": self.monitor_region_height,
        }

    @property
    def target_bgr(self) -> tuple[int, int, int]:
        return self.target_rgb_b, self.target_rgb_g, self.target_rgb_r


@dataclass(frozen=True, slots=True)
class UiSettings:
    language: str = "en"


@dataclass(frozen=True, slots=True)
class PointsSettings:
    points_path: str


@dataclass(frozen=True, slots=True)
class AppSettings:
    hotkeys: HotkeySettings
    delays: DelaySettings
    mesh: MeshSettings
    cv: CvSettings
    ui: UiSettings
    preset_name: str
    points: PointsSettings


class SettingsValidationError(ValueError):
    def __init__(self, errors: Mapping[str, str]):
        self.errors = dict(errors)
        super().__init__("; ".join(self.errors.values()))


def validate_settings(
    settings: AppSettings,
    hotkey_validator: Callable[[str], bool] | None = None,
    action_validator: Callable[[str], bool] | None = None,
) -> None:
    errors: dict[str, str] = {}

    if not settings.preset_name.strip():
        errors["preset_name"] = "Preset name cannot be empty."
    if not settings.points.points_path.strip():
        errors["points_path"] = "Points path cannot be empty."

    if settings.ui.language not in SUPPORTED_LANGUAGES:
        errors["language"] = "Language must be English or Russian."

    if settings.delays.delay_before_ms < 0:
        errors["delay_before"] = "Delay before a click cannot be negative."
    if settings.delays.delay_after_ms < 0:
        errors["delay_after"] = "Delay after a click cannot be negative."

    if settings.mesh.amount_width <= 1:
        errors["amount_width"] = "Mesh width must be greater than 1."
    if settings.mesh.amount_height <= 1:
        errors["amount_height"] = "Mesh height must be greater than 1."

    if settings.cv.monitor_region_width <= 0:
        errors["monitor_region_width"] = "CV region width must be greater than 0."
    if settings.cv.monitor_region_height <= 0:
        errors["monitor_region_height"] = "CV region height must be greater than 0."

    for name, value in (
        ("target_rgb_r", settings.cv.target_rgb_r),
        ("target_rgb_g", settings.cv.target_rgb_g),
        ("target_rgb_b", settings.cv.target_rgb_b),
    ):
        if not 0 <= value <= 255:
            errors[name] = "RGB values must be between 0 and 255."

    for name, value in (
        ("delay_between_frames", settings.cv.delay_between_frames_ms),
        ("click_cooldown", settings.cv.click_cooldown_ms),
        ("second_click_delay", settings.cv.second_click_delay_ms),
    ):
        if value < 0:
            errors[name] = "CV timing values cannot be negative."

    normalized_hotkeys: dict[str, str] = {}
    reserved_hotkeys = {normalize_hotkey(hotkey) for hotkey in PRESET_SWITCH_HOTKEYS}
    for name, hotkey in settings.hotkeys.as_dict().items():
        normalized = normalize_hotkey(hotkey.strip())
        if not normalized:
            errors[name] = "Hotkeys cannot be empty."
        elif hotkey_validator is not None and not hotkey_validator(hotkey):
            errors[name] = "Unsupported hotkey."
        elif normalized in reserved_hotkeys:
            errors[name] = "Hotkey is reserved for preset selection."
        elif normalized in normalized_hotkeys:
            errors[name] = "Hotkey duplicates another action."
        else:
            normalized_hotkeys[normalized] = name

    for name, action in (
        ("first_action", settings.cv.first_action),
        ("second_action", settings.cv.second_action),
    ):
        if not action.strip():
            errors[name] = "CV actions cannot be empty."
        elif action_validator is not None and not action_validator(action):
            errors[name] = "Unsupported CV action."

    if errors:
        raise SettingsValidationError(errors)
