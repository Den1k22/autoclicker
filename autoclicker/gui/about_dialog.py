import wx

import gettext
t = gettext.gettext


class AboutDialog (wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=t("About..."), pos=wx.DefaultPosition,
                           size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        about_autoclicker_sizer = wx.BoxSizer(wx.VERTICAL)

        self.about_autoclicker_message_label = wx.StaticText(self, wx.ID_ANY, t(
            "Thank you for using Autoclicker!"), wx.DefaultPosition, wx.DefaultSize, 0)
        self.about_autoclicker_message_label.Wrap(-1)

        about_autoclicker_sizer.Add(self.about_autoclicker_message_label, 0, wx.ALL, 5)

        version_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.version_label = wx.StaticText(self, wx.ID_ANY, t("Version:"), wx.DefaultPosition, wx.DefaultSize, 0)
        self.version_label.Wrap(-1)

        version_sizer.Add(self.version_label, 0, wx.ALL, 5)

        self.version_value = wx.StaticText(self, wx.ID_ANY, "0.3", wx.DefaultPosition, wx.DefaultSize, 0)
        self.version_value.Wrap(-1)

        version_sizer.Add(self.version_value, 0, wx.ALL, 5)

        about_autoclicker_sizer.Add(version_sizer, 1, wx.EXPAND, 5)

        close_button = wx.Button(self, label="Close")
        close_button.Bind(wx.EVT_BUTTON, self.onClose)

        about_autoclicker_sizer.Add(close_button, 0, wx.ALL | wx.ALIGN_CENTER, 10)

        self.SetSizer(about_autoclicker_sizer)
        self.Layout()
        about_autoclicker_sizer.Fit(self)

        self.Centre(wx.BOTH)

    def __del__(self):
        pass

    def onClose(self, event):
        event.Skip()
        self.Close()
