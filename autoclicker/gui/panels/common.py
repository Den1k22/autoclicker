from __future__ import annotations

import wx


def add_labeled_spin(
    panel: wx.Window,
    sizer: wx.FlexGridSizer,
    label: str,
    value: int,
    minimum: int = 0,
    maximum: int = 999_999_999,
) -> wx.SpinCtrl:
    text = wx.StaticText(panel, label=label)
    control = wx.SpinCtrl(panel, min=minimum, max=maximum, initial=value)
    control.SetMinSize((120, -1))
    sizer.Add(text, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
    sizer.Add(control, 1, wx.EXPAND)
    return control


def add_labeled_text(
    panel: wx.Window,
    sizer: wx.FlexGridSizer,
    label: str,
    value: str,
) -> wx.TextCtrl:
    text = wx.StaticText(panel, label=label)
    control = wx.TextCtrl(panel, value=value)
    sizer.Add(text, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
    sizer.Add(control, 1, wx.EXPAND)
    return control
