"""Adapters for operating-system and third-party input APIs."""

from autoclicker.adapters.actions import ActionDispatcher
from autoclicker.adapters.keyboard import HotkeyManager, KeyboardAdapter
from autoclicker.adapters.mouse import MouseAdapter
from autoclicker.adapters.screen_capture import ScreenCaptureAdapter

__all__ = [
    "ActionDispatcher",
    "HotkeyManager",
    "KeyboardAdapter",
    "MouseAdapter",
    "ScreenCaptureAdapter",
]
