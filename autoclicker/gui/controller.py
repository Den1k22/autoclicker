from __future__ import annotations

import threading
from pathlib import Path

import wx

from autoclicker.adapters.keyboard import HotkeyManager
from autoclicker.automation.points import Point, PointFileError
from autoclicker.automation.service import AutomationError, AutomationService, RunMode
from autoclicker.settings.model import AppSettings, SettingsValidationError, validate_settings
from autoclicker.settings.repository import SettingsRepository


class GuiController:
    def __init__(
        self,
        frame,
        service: AutomationService,
        repository: SettingsRepository,
        keyboard,
        action_dispatcher,
        translate,
        call_after=wx.CallAfter,
    ):
        self.frame = frame
        self.service = service
        self.repository = repository
        self.keyboard = keyboard
        self.action_dispatcher = action_dispatcher
        self._ = translate
        self._call_after = call_after
        self._hotkeys: HotkeyManager | None = None
        self._settings = service.settings
        self._closing = False
        self._shutdown_lock = threading.Lock()
        self._shutdown_complete = False

        service.add_points_listener(self._points_changed)
        service.add_mode_listener(self._mode_changed)
        service.add_error_listener(self._worker_failed)

    def set_hotkey_manager(self, manager: HotkeyManager) -> None:
        self._hotkeys = manager

    def hotkey_callbacks(self):
        return {
            "add_point_hotkey": self.on_record_point,
            "remove_last_point_hotkey": self.on_remove_last_point,
            "remove_all_points_hotkey": self.on_clear_points,
            "start_autoclicker_hotkey": self.on_start_points,
            "stop_autoclicker_hotkey": self.on_stop,
            "one_autoclick_run_hotkey": self.on_run_once,
            "start_stop_cv_hotkey": self.on_toggle_cv,
            "exit_hotkey": lambda: self._call_after(self.frame.Close),
        }

    def on_record_point(self, event=None) -> None:
        try:
            self.service.record_current_point()
        except Exception as error:
            self._show_error(str(error))

    def on_edit_point(self, index: int, point: Point) -> None:
        try:
            values = [
                int(self.frame.points_panel.table.GetValue(index, column))
                for column in range(1, 5)
            ]
            self.service.update_point(index, Point(*values))
        except (IndexError, TypeError, ValueError):
            self._show_error(self._("Coordinates must be integers and delays cannot be negative."))
            self._points_changed(self.service.points(), self.service.dirty, self.service.document_path)

    def on_remove_point(self, index: int) -> None:
        try:
            self.service.remove_point(index)
        except IndexError:
            self._show_error(self._("The selected point no longer exists."))

    def on_remove_last_point(self, event=None) -> None:
        self.service.remove_last_point()

    def on_clear_points(self, event=None) -> None:
        self.service.clear_points()

    def on_move_point(self, index: int, offset: int) -> None:
        selected = self.service.move_point(index, offset)
        self._call_after(self.frame.points_panel.select_row, selected)

    def on_create_mesh(self, event=None) -> None:
        try:
            self.service.create_mesh()
        except ValueError as error:
            if str(error) == "mesh_requires_three_points":
                self._show_error(self._("Mesh generation requires exactly three points."))
            else:
                self._show_error(self._("Mesh width and height must both be greater than 1."))

    def on_run_once(self, event=None) -> None:
        self._start(self.service.start_points_once)

    def on_start_points(self, event=None) -> None:
        self._start(self.service.start_points_continuous)

    def on_start_cv(self, event=None) -> None:
        self._start(self.service.start_cv)

    def on_toggle_cv(self, event=None) -> None:
        if self.service.mode == RunMode.CV:
            self.service.stop()
        else:
            self._start(self.service.start_cv)

    def on_stop(self, event=None) -> None:
        self.service.stop()

    def on_load_points(self, event=None) -> None:
        if not self._confirm_replace_dirty_points():
            return
        path = self.frame.choose_points_to_open(self.service.document_path)
        if path is not None:
            self._load(path)

    def on_save_points(self, event=None) -> bool:
        return self._save(self.service.document_path)

    def on_save_points_as(self, event=None) -> bool:
        path = self.frame.choose_points_to_save(self.service.document_path)
        return False if path is None else self._save(path)

    def on_apply_settings(self, event=None) -> None:
        try:
            candidate = self.frame.candidate_settings()
            validate_settings(
                candidate,
                hotkey_validator=self.keyboard.is_valid_combination,
                action_validator=self.action_dispatcher.is_valid,
            )
        except SettingsValidationError as error:
            self.frame.settings_panel.hotkeys.set_errors(error.errors)
            self._show_error("\n".join(self._(message) for message in error.errors.values()))
            return
        except (TypeError, ValueError) as error:
            self._show_error(str(error))
            return

        if self._hotkeys is None:
            self._show_error(self._("Global hotkeys are not initialized."))
            return

        previous = self._settings
        try:
            self._hotkeys.apply(candidate.hotkeys)
            self.repository.save(candidate)
        except Exception as error:
            try:
                self._hotkeys.apply(previous.hotkeys)
            except Exception:
                pass
            self._show_error(self._("Could not apply settings: {error}").format(error=error))
            return

        self._settings = candidate
        self.service.update_settings(candidate)
        self.frame.settings_panel.hotkeys.clear_errors()
        self.frame.show_info(self._("Settings applied successfully."))

    def on_exit(self, event=None) -> None:
        self.frame.Close()

    def on_close(self, event: wx.CloseEvent) -> None:
        if self._closing:
            event.Skip()
            return
        if self._has_savable_point_changes():
            answer = self.frame.confirm_discard_changes()
            if answer == wx.ID_CANCEL:
                event.Veto()
                return
            if answer == wx.ID_YES and not self.on_save_points():
                event.Veto()
                return

        self._closing = True
        self.shutdown()
        event.Skip()

    def shutdown(self) -> None:
        with self._shutdown_lock:
            if self._shutdown_complete:
                return
            self._shutdown_complete = True
        self.service.shutdown()
        if self._hotkeys is not None:
            self._hotkeys.close()

    def _start(self, starter) -> None:
        try:
            if not starter():
                self._show_error(self._("Another automation mode is already running."))
        except AutomationError as error:
            if error.code == "no_points":
                self._show_error(self._("Record or load at least one point first."))
            else:
                self._show_error(str(error))

    def _load(self, path: Path) -> None:
        try:
            self.service.load_points(path)
        except PointFileError as error:
            self._show_error(str(error))

    def _save(self, path: Path) -> bool:
        try:
            self.service.save_points(path)
        except OSError as error:
            self._show_error(self._("Could not save points: {error}").format(error=error))
            return False
        return True

    def _confirm_replace_dirty_points(self) -> bool:
        if not self._has_savable_point_changes():
            return True
        answer = self.frame.confirm_discard_changes()
        if answer == wx.ID_CANCEL:
            return False
        if answer == wx.ID_YES:
            return self.on_save_points()
        return True

    def _has_savable_point_changes(self) -> bool:
        return self.service.dirty and bool(self.service.points())

    def _points_changed(self, points, dirty, path) -> None:
        self._call_after(self._set_points_if_open, points, dirty, path)

    def _mode_changed(self, mode: RunMode) -> None:
        self._call_after(self._set_mode_if_open, mode)

    def _worker_failed(self, error: Exception) -> None:
        self._show_error(self._("Automation stopped because of an error: {error}").format(error=error))

    def _show_error(self, message: str) -> None:
        self._call_after(self._show_error_if_open, message)

    def _set_points_if_open(self, points, dirty, path) -> None:
        if not self._closing:
            self.frame.set_points(points, dirty, path)

    def _set_mode_if_open(self, mode: RunMode) -> None:
        if not self._closing:
            self.frame.set_mode(mode)

    def _show_error_if_open(self, message: str) -> None:
        if not self._closing:
            self.frame.show_error(message)
