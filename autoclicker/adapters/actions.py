from __future__ import annotations

from autoclicker.adapters.keyboard import KeyboardAdapter
from autoclicker.adapters.mouse import MouseAdapter


class ActionDispatcher:
    def __init__(self, keyboard: KeyboardAdapter, mouse: MouseAdapter):
        self._keyboard = keyboard
        self._mouse = mouse

    def parse(self, action: str) -> tuple[str, str]:
        if not isinstance(action, str) or not action.strip():
            raise ValueError("Action must be a non-empty string.")

        action_name = action.strip()
        if self._keyboard.is_valid_combination(action_name):
            return "keyboard", action_name
        if self._mouse.is_valid_button(action_name):
            return "mouse", action_name.lower()
        raise ValueError(f"Unsupported keyboard combination or mouse action: {action_name}")

    def is_valid(self, action: str) -> bool:
        try:
            self.parse(action)
        except ValueError:
            return False
        return True

    def execute(self, action: str) -> None:
        action_type, action_name = self.parse(action)
        if action_type == "keyboard":
            self._keyboard.press_and_release(action_name)
        else:
            self._mouse.click_button(action_name)
