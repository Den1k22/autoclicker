from __future__ import annotations

from collections.abc import Callable
from importlib.metadata import PackageNotFoundError, version

import wx


try:
    APPLICATION_VERSION = version("den1k22-autoclicker")
except PackageNotFoundError:
    APPLICATION_VERSION = "development"


class AboutDialog(wx.Dialog):
    def __init__(self, parent: wx.Window, translate: Callable[[str], str]):
        super().__init__(parent, title=translate("About Autoclicker"))
        outer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label="Autoclicker")
        title_font = title.GetFont().Bold()
        title_font.SetPointSize(max(title_font.GetPointSize() + 4, 14))
        title.SetFont(title_font)
        outer.Add(title, 0, wx.ALIGN_CENTER | wx.ALL, 12)
        description = wx.StaticText(
            self,
            label=translate("Local automation for recorded screen points and exact-color CV actions."),
        )
        description.Wrap(520)
        outer.Add(description, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        outer.Add(
            wx.StaticText(self, label=f'{translate("Version")}: {APPLICATION_VERSION}'),
            0,
            wx.ALIGN_CENTER | wx.BOTTOM,
            12,
        )
        close_button = wx.Button(self, wx.ID_OK, translate("Close"))
        outer.Add(close_button, 0, wx.ALIGN_CENTER | wx.BOTTOM, 12)
        self.SetSizerAndFit(outer)
        self.CentreOnParent()
