from __future__ import annotations

from pynput import mouse


SUPPORTED_BUTTONS = {
    "left_button": mouse.Button.left,
    "right_button": mouse.Button.right,
    "middle_button": mouse.Button.middle,
    "x1_button": mouse.Button.x1,
    "x2_button": mouse.Button.x2,
}


class MouseAdapter:
    def __init__(self, controller=None):
        self._controller = controller or mouse.Controller()

    def get_position(self) -> tuple[int, int]:
        x, y = self._controller.position
        return int(x), int(y)

    def set_position(self, x: int, y: int) -> None:
        self._controller.position = (x, y)

    @staticmethod
    def is_valid_button(button: str) -> bool:
        return isinstance(button, str) and button.strip().lower() in SUPPORTED_BUTTONS

    def click_button(self, button: str, times: int = 1) -> None:
        if not self.is_valid_button(button):
            raise ValueError(f"Unsupported mouse button: {button}")
        self._controller.click(SUPPORTED_BUTTONS[button.strip().lower()], times)

    def click_left(self, times: int = 1) -> None:
        self.click_button("left_button", times)
