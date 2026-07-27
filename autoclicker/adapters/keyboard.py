from __future__ import annotations

import threading
from collections.abc import Callable, Mapping

import keyboard as keyboard_library

from autoclicker.settings.model import HotkeySettings


class KeyboardAdapter:
    def press_and_release(self, key: str) -> None:
        keyboard_library.press_and_release(key)

    def add_hotkey(self, hotkey: str, callback: Callable[[], None]):
        # Consume registered shortcuts so their final key cannot also activate
        # a focused wx control (for example Space pressing Create mesh).
        return keyboard_library.add_hotkey(hotkey, callback, suppress=True)

    def remove_all_hotkeys(self) -> None:
        keyboard_library.remove_all_hotkeys()

    def is_valid_combination(self, value: str) -> bool:
        if not isinstance(value, str) or not value.strip():
            return False
        try:
            return len(keyboard_library.parse_hotkey(value.strip())) == 1
        except (KeyError, ValueError):
            return False


class HotkeyRegistrationError(RuntimeError):
    pass


class HotkeyManager:
    """Own all global hook registrations and replace them as one logical set."""

    def __init__(
        self,
        adapter: KeyboardAdapter,
        callbacks: Mapping[str, Callable[[], None]],
        fixed_hotkeys: Mapping[str, Callable[[], None]] | None = None,
    ):
        self._adapter = adapter
        self._callbacks = dict(callbacks)
        self._fixed_hotkeys = dict(fixed_hotkeys or {})
        self._current: HotkeySettings | None = None
        self._lock = threading.RLock()

    @property
    def current(self) -> HotkeySettings | None:
        with self._lock:
            return self._current

    def apply(self, hotkeys: HotkeySettings) -> None:
        values = hotkeys.as_dict()
        missing_callbacks = set(values) - set(self._callbacks)
        if missing_callbacks:
            raise HotkeyRegistrationError(
                "Missing callbacks for: " + ", ".join(sorted(missing_callbacks))
            )

        with self._lock:
            previous = self._current
            # keyboard.remove_all_hotkeys() assumes its listener has already
            # been initialized by add_hotkey(). Do not call it before the first
            # registration.
            if previous is not None:
                self._adapter.remove_all_hotkeys()
            try:
                self._register(hotkeys)
            except Exception as error:
                self._adapter.remove_all_hotkeys()
                if previous is not None:
                    try:
                        self._register(previous)
                    except Exception as rollback_error:
                        self._adapter.remove_all_hotkeys()
                        self._current = None
                        raise HotkeyRegistrationError(
                            f"Could not register hotkeys and rollback failed: {rollback_error}"
                        ) from error
                raise HotkeyRegistrationError(f"Could not register hotkeys: {error}") from error

    def close(self) -> None:
        with self._lock:
            if self._current is None:
                return
            try:
                self._adapter.remove_all_hotkeys()
            finally:
                self._current = None

    def _register(self, hotkeys: HotkeySettings) -> None:
        for name, hotkey in hotkeys.as_dict().items():
            self._adapter.add_hotkey(hotkey, self._callbacks[name])
        for hotkey, callback in self._fixed_hotkeys.items():
            self._adapter.add_hotkey(hotkey, callback)
        self._current = hotkeys
