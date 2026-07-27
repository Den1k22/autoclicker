from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import wx

from autoclicker.automation.points import Point
from autoclicker.automation.service import RunMode
from autoclicker.gui.dialogs import AboutDialog
from autoclicker.gui.panels import PointsPanel, SettingsNotebook
from autoclicker.settings.model import AppSettings


class MainFrame(wx.Frame):
    def __init__(
        self,
        settings: AppSettings,
        defaults: AppSettings,
        translate: Callable[[str], str],
        preset_names: tuple[str, ...] | None = None,
        active_preset: int = 0,
    ):
        super().__init__(None, title="Autoclicker", size=(1120, 700))
        self.SetMinSize((900, 600))
        self._ = translate
        self._n = getattr(
            translate,
            "ngettext",
            lambda singular, plural, count: singular if count == 1 else plural,
        )
        self._controller = None
        self._build_menu()

        root = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        content = wx.BoxSizer(wx.HORIZONTAL)
        self.points_panel = PointsPanel(root, translate)
        self.settings_panel = SettingsNotebook(
            root,
            settings,
            defaults,
            translate,
            preset_names,
            active_preset,
        )
        content.Add(self.points_panel, 0, wx.EXPAND | wx.ALL, 6)
        content.Add(self.settings_panel, 1, wx.EXPAND | wx.ALL, 6)
        outer.Add(content, 1, wx.EXPAND)

        controls = wx.BoxSizer(wx.HORIZONTAL)
        self.run_once_button = wx.Button(root, label=self._("Run once"))
        self.start_points_button = wx.Button(root, label=self._("Start points"))
        self.start_cv_button = wx.Button(root, label=self._("Start CV"))
        self.stop_button = wx.Button(root, label=self._("Stop"))
        self.stop_button.SetForegroundColour(wx.Colour(180, 0, 0))
        controls.Add(self.run_once_button, 0, wx.RIGHT, 8)
        controls.Add(self.start_points_button, 0, wx.RIGHT, 8)
        controls.Add(self.start_cv_button, 0, wx.RIGHT, 8)
        controls.AddStretchSpacer()
        controls.Add(self.stop_button)
        outer.Add(controls, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        root.SetSizer(outer)

        self.CreateStatusBar(2)
        self.SetStatusWidths([-1, 220])
        self.set_mode(RunMode.IDLE)
        self.Centre()

    def bind_controller(self, controller) -> None:
        self._controller = controller
        self.points_panel.bind_actions(
            controller.on_edit_point,
            controller.on_remove_point,
            controller.on_clear_points,
            controller.on_move_point,
        )
        self.settings_panel.apply_button.Bind(wx.EVT_BUTTON, controller.on_apply_settings)
        self.settings_panel.preset_choice.Bind(wx.EVT_CHOICE, controller.on_select_preset)
        self.settings_panel.general.browse_points_button.Bind(
            wx.EVT_BUTTON,
            controller.on_browse_points_path,
        )
        self.settings_panel.mesh.create_button.Bind(wx.EVT_BUTTON, controller.on_create_mesh)
        self.run_once_button.Bind(wx.EVT_BUTTON, controller.on_run_once)
        self.start_points_button.Bind(wx.EVT_BUTTON, controller.on_start_points)
        self.start_cv_button.Bind(wx.EVT_BUTTON, controller.on_start_cv)
        self.stop_button.Bind(wx.EVT_BUTTON, controller.on_stop)
        self.Bind(wx.EVT_MENU, controller.on_load_points, id=self.load_item.GetId())
        self.Bind(wx.EVT_MENU, controller.on_save_points, id=self.save_item.GetId())
        self.Bind(wx.EVT_MENU, controller.on_save_points_as, id=self.save_as_item.GetId())
        self.Bind(wx.EVT_MENU, controller.on_exit, id=self.exit_item.GetId())
        self.Bind(wx.EVT_MENU, self._show_about, id=self.about_item.GetId())
        self.Bind(wx.EVT_CLOSE, controller.on_close)

    def candidate_settings(self) -> AppSettings:
        return self.settings_panel.values()

    def set_preset(
        self,
        settings: AppSettings,
        defaults: AppSettings,
        preset_names: tuple[str, ...],
        active_preset: int,
    ) -> None:
        self.settings_panel.set_preset(settings, defaults, preset_names, active_preset)

    def set_points(self, points: tuple[Point, ...], dirty: bool, path: Path) -> None:
        self.points_panel.set_points(points)
        marker = "*" if dirty else ""
        self.SetTitle(f"Autoclicker — {path.name}{marker}")
        label = self._n("{count} point", "{count} points", len(points)).format(count=len(points))
        self.SetStatusText(label, 1)

    def set_mode(self, mode: RunMode) -> None:
        names = {
            RunMode.IDLE: self._("Idle"),
            RunMode.POINTS_ONCE: self._("Running points once"),
            RunMode.POINTS_CONTINUOUS: self._("Running points continuously"),
            RunMode.CV: self._("Running computer vision"),
        }
        self.SetStatusText(names[mode], 0)
        active = mode != RunMode.IDLE
        self.run_once_button.Enable(not active)
        self.start_points_button.Enable(not active)
        self.start_cv_button.Enable(not active)
        self.stop_button.Enable(active)

    def show_error(self, message: str) -> None:
        wx.MessageBox(message, self._("Autoclicker error"), wx.OK | wx.ICON_ERROR, self)

    def show_info(self, message: str) -> None:
        wx.MessageBox(message, self._("Autoclicker"), wx.OK | wx.ICON_INFORMATION, self)

    def confirm_discard_changes(self) -> int:
        dialog = wx.MessageDialog(
            self,
            self._("The points list has unsaved changes. Save before continuing?"),
            self._("Unsaved points"),
            wx.YES_NO | wx.CANCEL | wx.CANCEL_DEFAULT | wx.ICON_WARNING,
        )
        try:
            return dialog.ShowModal()
        finally:
            dialog.Destroy()

    def choose_points_to_open(self, initial_path: Path) -> Path | None:
        dialog = wx.FileDialog(
            self,
            self._("Load points"),
            defaultDir=str(initial_path.parent),
            defaultFile=initial_path.name,
            wildcard=self._("Text files (*.txt)|*.txt|All files (*.*)|*.*"),
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        )
        try:
            return Path(dialog.GetPath()) if dialog.ShowModal() == wx.ID_OK else None
        finally:
            dialog.Destroy()

    def choose_points_to_save(self, initial_path: Path) -> Path | None:
        dialog = wx.FileDialog(
            self,
            self._("Save points as"),
            defaultDir=str(initial_path.parent),
            defaultFile=initial_path.name,
            wildcard=self._("Text files (*.txt)|*.txt|All files (*.*)|*.*"),
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        )
        try:
            return Path(dialog.GetPath()) if dialog.ShowModal() == wx.ID_OK else None
        finally:
            dialog.Destroy()

    def choose_preset_points_path(self, initial_path: Path) -> Path | None:
        dialog = wx.FileDialog(
            self,
            self._("Choose preset points file"),
            defaultDir=str(initial_path.parent),
            defaultFile=initial_path.name,
            wildcard=self._("Text files (*.txt)|*.txt|All files (*.*)|*.*"),
            style=wx.FD_SAVE,
        )
        try:
            return Path(dialog.GetPath()) if dialog.ShowModal() == wx.ID_OK else None
        finally:
            dialog.Destroy()

    def _build_menu(self) -> None:
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        self.load_item = file_menu.Append(wx.ID_OPEN, self._("&Load points...\tCtrl+O"))
        self.save_item = file_menu.Append(wx.ID_SAVE, self._("&Save points\tCtrl+S"))
        self.save_as_item = file_menu.Append(wx.ID_SAVEAS, self._("Save points &as..."))
        file_menu.AppendSeparator()
        self.exit_item = file_menu.Append(wx.ID_EXIT, self._("E&xit"))
        menu_bar.Append(file_menu, self._("&File"))

        help_menu = wx.Menu()
        self.about_item = help_menu.Append(wx.ID_ABOUT, self._("&About..."))
        menu_bar.Append(help_menu, self._("&Help"))
        self.SetMenuBar(menu_bar)

    def _show_about(self, event: wx.CommandEvent) -> None:
        dialog = AboutDialog(self, self._)
        try:
            dialog.ShowModal()
        finally:
            dialog.Destroy()
