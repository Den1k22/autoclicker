from __future__ import annotations

from collections.abc import Callable

import wx

from autoclicker.gui.panels.common import add_labeled_spin, add_labeled_text
from autoclicker.i18n.translator import SUPPORTED_LANGUAGES
from autoclicker.settings.model import (
    AppSettings,
    CvSettings,
    DelaySettings,
    HOTKEY_LABELS,
    HotkeySettings,
    MeshSettings,
    PointsSettings,
    UiSettings,
)


class GeneralPanel(wx.Panel):
    def __init__(self, parent: wx.Window, settings: AppSettings, translate: Callable[[str], str]):
        super().__init__(parent)
        self._ = translate
        outer = wx.BoxSizer(wx.VERTICAL)

        preset_grid = wx.FlexGridSizer(cols=2, vgap=10, hgap=8)
        preset_grid.AddGrowableCol(1, 1)
        self.preset_name = add_labeled_text(
            self,
            preset_grid,
            self._("Preset name"),
            settings.preset_name,
        )
        preset_grid.Add(
            wx.StaticText(self, label=self._("Points file")),
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
            8,
        )
        points_controls = wx.BoxSizer(wx.HORIZONTAL)
        self.points_path = wx.TextCtrl(self, value=settings.points.points_path)
        self.browse_points_button = wx.Button(self, label=self._("Browse..."))
        points_controls.Add(self.points_path, 1, wx.RIGHT, 8)
        points_controls.Add(self.browse_points_button)
        preset_grid.Add(points_controls, 1, wx.EXPAND)
        outer.Add(preset_grid, 0, wx.EXPAND | wx.ALL, 12)

        language_grid = wx.FlexGridSizer(cols=2, vgap=10, hgap=8)
        language_grid.AddGrowableCol(1, 1)
        language_grid.Add(
            wx.StaticText(self, label=self._("Language")),
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
            8,
        )
        self.language = wx.Choice(self, choices=list(SUPPORTED_LANGUAGES.values()))
        language_codes = list(SUPPORTED_LANGUAGES)
        language = settings.ui.language if settings.ui.language in language_codes else "en"
        self.language.SetSelection(language_codes.index(language))
        language_grid.Add(self.language, 1, wx.EXPAND)
        outer.Add(language_grid, 0, wx.EXPAND | wx.ALL, 12)

        self.language_note = wx.StaticText(
            self,
            label=self._("Language change takes effect after restarting the application."),
        )
        self.language_note.Wrap(520)
        outer.Add(self.language_note, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        delay_grid = wx.FlexGridSizer(cols=2, vgap=10, hgap=8)
        delay_grid.AddGrowableCol(1, 1)
        self.delay_before = add_labeled_spin(
            self,
            delay_grid,
            self._("Default delay before click (ms)"),
            settings.delays.delay_before_ms,
        )
        self.delay_after = add_labeled_spin(
            self,
            delay_grid,
            self._("Default delay after click (ms)"),
            settings.delays.delay_after_ms,
        )
        outer.Add(delay_grid, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        self.SetSizer(outer)

    def values(self) -> tuple[UiSettings, DelaySettings, str, PointsSettings]:
        selection = max(self.language.GetSelection(), 0)
        language = list(SUPPORTED_LANGUAGES)[selection]
        return (
            UiSettings(language=language),
            DelaySettings(
                delay_before_ms=self.delay_before.GetValue(),
                delay_after_ms=self.delay_after.GetValue(),
            ),
            self.preset_name.GetValue().strip(),
            PointsSettings(self.points_path.GetValue().strip()),
        )

    def set_values(self, settings: AppSettings) -> None:
        language = settings.ui.language if settings.ui.language in SUPPORTED_LANGUAGES else "en"
        self.language.SetSelection(list(SUPPORTED_LANGUAGES).index(language))
        self.delay_before.SetValue(settings.delays.delay_before_ms)
        self.delay_after.SetValue(settings.delays.delay_after_ms)
        self.preset_name.SetValue(settings.preset_name)
        self.points_path.SetValue(settings.points.points_path)


class CvPanel(wx.ScrolledWindow):
    def __init__(self, parent: wx.Window, settings: AppSettings, translate: Callable[[str], str]):
        super().__init__(parent, style=wx.VSCROLL)
        self._ = translate
        self.SetScrollRate(0, 10)
        outer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(cols=2, vgap=8, hgap=8)
        grid.AddGrowableCol(1, 1)
        cv = settings.cv

        self.top = add_labeled_spin(self, grid, self._("Region top"), cv.monitor_region_top, -999_999)
        self.left = add_labeled_spin(self, grid, self._("Region left"), cv.monitor_region_left, -999_999)
        self.width = add_labeled_spin(self, grid, self._("Region width"), cv.monitor_region_width, 1)
        self.height = add_labeled_spin(self, grid, self._("Region height"), cv.monitor_region_height, 1)
        self.red = add_labeled_spin(self, grid, self._("Target red"), cv.target_rgb_r, 0, 255)
        self.green = add_labeled_spin(self, grid, self._("Target green"), cv.target_rgb_g, 0, 255)
        self.blue = add_labeled_spin(self, grid, self._("Target blue"), cv.target_rgb_b, 0, 255)
        self.frame_delay = add_labeled_spin(
            self, grid, self._("Delay between frames (ms)"), cv.delay_between_frames_ms
        )
        self.cooldown = add_labeled_spin(self, grid, self._("Action cooldown (ms)"), cv.click_cooldown_ms)
        self.second_delay = add_labeled_spin(
            self, grid, self._("Second action delay (ms)"), cv.second_click_delay_ms
        )
        self.first_action = add_labeled_text(self, grid, self._("First action"), cv.first_action)
        self.second_action = add_labeled_text(self, grid, self._("Second action"), cv.second_action)
        outer.Add(grid, 0, wx.EXPAND | wx.ALL, 12)
        self.SetSizer(outer)
        self.FitInside()

    def values(self) -> CvSettings:
        return CvSettings(
            monitor_region_top=self.top.GetValue(),
            monitor_region_left=self.left.GetValue(),
            monitor_region_width=self.width.GetValue(),
            monitor_region_height=self.height.GetValue(),
            target_rgb_r=self.red.GetValue(),
            target_rgb_g=self.green.GetValue(),
            target_rgb_b=self.blue.GetValue(),
            delay_between_frames_ms=self.frame_delay.GetValue(),
            click_cooldown_ms=self.cooldown.GetValue(),
            second_click_delay_ms=self.second_delay.GetValue(),
            first_action=self.first_action.GetValue().strip(),
            second_action=self.second_action.GetValue().strip(),
        )

    def set_values(self, settings: AppSettings) -> None:
        cv = settings.cv
        controls = (
            (self.top, cv.monitor_region_top),
            (self.left, cv.monitor_region_left),
            (self.width, cv.monitor_region_width),
            (self.height, cv.monitor_region_height),
            (self.red, cv.target_rgb_r),
            (self.green, cv.target_rgb_g),
            (self.blue, cv.target_rgb_b),
            (self.frame_delay, cv.delay_between_frames_ms),
            (self.cooldown, cv.click_cooldown_ms),
            (self.second_delay, cv.second_click_delay_ms),
        )
        for control, value in controls:
            control.SetValue(value)
        self.first_action.SetValue(cv.first_action)
        self.second_action.SetValue(cv.second_action)


class MeshPanel(wx.Panel):
    def __init__(self, parent: wx.Window, settings: AppSettings, translate: Callable[[str], str]):
        super().__init__(parent)
        self._ = translate
        outer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(cols=2, vgap=10, hgap=8)
        grid.AddGrowableCol(1, 1)
        self.width = add_labeled_spin(self, grid, self._("Points across"), settings.mesh.amount_width, 2)
        self.height = add_labeled_spin(self, grid, self._("Points down"), settings.mesh.amount_height, 2)
        outer.Add(grid, 0, wx.EXPAND | wx.ALL, 12)
        explanation = wx.StaticText(
            self,
            label=self._(
                "Mesh generation uses exactly three recorded points: "
                "origin, horizontal extent, and vertical extent."
            ),
        )
        explanation.Wrap(520)
        outer.Add(explanation, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        self.create_button = wx.Button(self, label=self._("Create mesh"))
        outer.Add(self.create_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        self.SetSizer(outer)

    def values(self) -> MeshSettings:
        return MeshSettings(self.width.GetValue(), self.height.GetValue())

    def set_values(self, settings: AppSettings) -> None:
        self.width.SetValue(settings.mesh.amount_width)
        self.height.SetValue(settings.mesh.amount_height)


class HotkeysPanel(wx.ScrolledWindow):
    def __init__(self, parent: wx.Window, settings: AppSettings, translate: Callable[[str], str]):
        super().__init__(parent, style=wx.VSCROLL)
        self._ = translate
        self.SetScrollRate(0, 10)
        outer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(cols=2, vgap=8, hgap=8)
        grid.AddGrowableCol(1, 1)
        self.controls: dict[str, wx.TextCtrl] = {}

        values = settings.hotkeys.as_dict()
        for name, label in HOTKEY_LABELS.items():
            control = add_labeled_text(self, grid, self._(label), values[name])
            control.SetToolTip(self._("Use one key or one simultaneous combination, for example ctrl+alt+s."))
            self.controls[name] = control

        outer.Add(grid, 0, wx.EXPAND | wx.ALL, 12)
        self.reset_button = wx.Button(self, label=self._("Restore default hotkeys"))
        outer.Add(self.reset_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        self.SetSizer(outer)
        self.FitInside()

    def values(self) -> HotkeySettings:
        return HotkeySettings(**{name: control.GetValue().strip() for name, control in self.controls.items()})

    def set_values(self, settings: AppSettings) -> None:
        for name, value in settings.hotkeys.as_dict().items():
            self.controls[name].SetValue(value)
        self.clear_errors()

    def set_errors(self, errors: dict[str, str]) -> None:
        self.clear_errors()
        for name, message in errors.items():
            control = self.controls.get(name)
            if control is not None:
                control.SetBackgroundColour(wx.Colour(255, 225, 225))
                control.SetToolTip(message)
                control.Refresh()

    def clear_errors(self) -> None:
        for control in self.controls.values():
            control.SetBackgroundColour(wx.NullColour)
            control.SetToolTip(self._("Use one key or one simultaneous combination, for example ctrl+alt+s."))
            control.Refresh()


class SettingsNotebook(wx.Panel):
    def __init__(
        self,
        parent: wx.Window,
        settings: AppSettings,
        defaults: AppSettings,
        translate: Callable[[str], str],
        preset_names: tuple[str, ...] | None = None,
        active_preset: int = 0,
    ):
        super().__init__(parent)
        self._ = translate
        self.defaults = defaults
        outer = wx.BoxSizer(wx.VERTICAL)
        self.notebook = wx.Notebook(self)
        self.general = GeneralPanel(self.notebook, settings, translate)
        self.cv = CvPanel(self.notebook, settings, translate)
        self.mesh = MeshPanel(self.notebook, settings, translate)
        self.hotkeys = HotkeysPanel(self.notebook, settings, translate)
        self.notebook.AddPage(self.general, self._("General"))
        self.notebook.AddPage(self.cv, self._("Computer vision"))
        self.notebook.AddPage(self.mesh, self._("Mesh"))
        self.notebook.AddPage(self.hotkeys, self._("Hotkeys"))
        outer.Add(self.notebook, 1, wx.EXPAND)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.preset_label = wx.StaticText(self, label=self._("Preset"))
        self.preset_choice = wx.Choice(
            self,
            choices=list(preset_names or (settings.preset_name,)),
        )
        self.preset_choice.SetMinSize((190, -1))
        self.preset_choice.SetSelection(active_preset)
        buttons.Add(self.preset_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        buttons.Add(self.preset_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        buttons.AddStretchSpacer()
        self.reset_button = wx.Button(self, label=self._("Restore all defaults"))
        self.apply_button = wx.Button(self, label=self._("Apply settings"))
        buttons.Add(self.reset_button, 0, wx.RIGHT, 8)
        buttons.Add(self.apply_button)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(outer)

        self.reset_button.Bind(wx.EVT_BUTTON, lambda event: self.set_values(self.defaults))
        self.hotkeys.reset_button.Bind(
            wx.EVT_BUTTON,
            lambda event: self.hotkeys.set_values(self.defaults),
        )

    def values(self) -> AppSettings:
        ui, delays, preset_name, points = self.general.values()
        return AppSettings(
            hotkeys=self.hotkeys.values(),
            delays=delays,
            mesh=self.mesh.values(),
            cv=self.cv.values(),
            ui=ui,
            preset_name=preset_name,
            points=points,
        )

    def set_values(self, settings: AppSettings) -> None:
        self.general.set_values(settings)
        self.cv.set_values(settings)
        self.mesh.set_values(settings)
        self.hotkeys.set_values(settings)

    def set_preset(
        self,
        settings: AppSettings,
        defaults: AppSettings,
        preset_names: tuple[str, ...],
        active_preset: int,
    ) -> None:
        self.defaults = defaults
        self.set_values(settings)
        self.set_preset_names(preset_names)
        self.preset_choice.SetSelection(active_preset)

    def set_preset_names(self, names: tuple[str, ...]) -> None:
        selection = self.preset_choice.GetSelection()
        self.preset_choice.Set(list(names))
        if 0 <= selection < len(names):
            self.preset_choice.SetSelection(selection)
