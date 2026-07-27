from __future__ import annotations

import logging
import shutil
from pathlib import Path

import wx

from autoclicker.adapters import (
    ActionDispatcher,
    HotkeyManager,
    KeyboardAdapter,
    MouseAdapter,
    ScreenCaptureAdapter,
)
from autoclicker.automation import AutomationService
from autoclicker.automation.points import PointFileError
from autoclicker.gui.controller import GuiController
from autoclicker.gui.main_frame import MainFrame
from autoclicker.helpers.paths import (
    application_dir,
    config_path,
    default_settings_path,
    legacy_points_path,
    points_path,
)
from autoclicker.i18n import Translator
from autoclicker.settings import SettingsRepository, validate_settings


def configure_logging(base_directory: Path) -> None:
    try:
        logging.basicConfig(
            filename=base_directory / "autoclicker.log",
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
            encoding="utf-8",
        )
    except OSError:
        logging.basicConfig(level=logging.INFO)


class AutoclickerWxApp(wx.App):
    def __init__(self):
        self.controller: GuiController | None = None
        self._startup_warning: str | None = None
        super().__init__(redirect=False)

    def OnInit(self) -> bool:
        configure_logging(application_dir())
        repository = SettingsRepository(config_path(), default_settings_path())
        try:
            settings = repository.load()
        except Exception as error:
            settings = repository.load_defaults()
            self._startup_warning = (
                "The settings file could not be loaded. Defaults are shown and can be saved from the GUI.\n\n"
                f"{error}"
            )

        keyboard = KeyboardAdapter()
        mouse = MouseAdapter()
        actions = ActionDispatcher(keyboard, mouse)

        try:
            validate_settings(
                settings,
                hotkey_validator=keyboard.is_valid_combination,
                action_validator=actions.is_valid,
            )
        except Exception as error:
            settings = repository.load_defaults()
            warning = f"Some settings are invalid. Defaults are shown and can be saved from the GUI.\n\n{error}"
            self._startup_warning = f"{self._startup_warning}\n\n{warning}" if self._startup_warning else warning

        translator = Translator(settings.ui.language)
        translate = translator

        configured_points_path = repository.resolve_points_path(settings.points.points_path)
        legacy_path = legacy_points_path()
        if configured_points_path == points_path() and not configured_points_path.exists() and legacy_path.is_file():
            try:
                configured_points_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(legacy_path, configured_points_path)
            except OSError as error:
                warning = translate("The legacy points file could not be migrated: {error}").format(error=error)
                self._startup_warning = (
                    f"{self._startup_warning}\n\n{warning}" if self._startup_warning else warning
                )

        service = AutomationService(
            settings=settings,
            mouse=mouse,
            action_dispatcher=actions,
            capture_factory=ScreenCaptureAdapter,
            default_points_path=configured_points_path,
        )
        if configured_points_path.is_file():
            try:
                service.load_points()
            except PointFileError as error:
                warning = translate("The preset points file could not be loaded: {error}").format(error=error)
                self._startup_warning = (
                    f"{self._startup_warning}\n\n{warning}" if self._startup_warning else warning
                )
        try:
            preset_names = repository.preset_names()
        except Exception:
            preset_names = tuple(f"Preset {index}" for index in range(1, 11))
        frame = MainFrame(
            settings,
            repository.load_defaults(repository.active_preset),
            translate,
            preset_names,
            repository.active_preset,
        )
        controller = GuiController(frame, service, repository, keyboard, actions, translate)
        hotkeys = HotkeyManager(
            keyboard,
            controller.hotkey_callbacks(),
            controller.preset_hotkey_callbacks(),
        )
        controller.set_hotkey_manager(hotkeys)
        frame.bind_controller(controller)
        self.controller = controller
        self.SetTopWindow(frame)
        frame.Show()
        service.publish_initial_state()

        try:
            hotkeys.apply(settings.hotkeys)
        except Exception as error:
            warning = translate("Global hotkeys could not be registered: {error}").format(error=error)
            self._startup_warning = f"{self._startup_warning}\n\n{warning}" if self._startup_warning else warning

        if self._startup_warning:
            wx.CallAfter(frame.show_error, self._startup_warning)
        return True

    def OnExit(self) -> int:
        if self.controller is not None:
            self.controller.shutdown()
        return 0


def main() -> int:
    app = AutoclickerWxApp()
    app.MainLoop()
    return 0
