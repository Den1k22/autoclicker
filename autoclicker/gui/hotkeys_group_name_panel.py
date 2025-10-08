
import wx


class HotkeysGroupNamePanel (wx.Panel):

    def __init__(self, parent, hotkeys_group_name):
        wx.Panel.__init__(self, parent, wx.ID_ANY,
                          wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)

        self.SetMaxSize(wx.Size(-1, 30))

        hotkeys_group_name_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.hotkeys_group_name = wx.StaticText(self, wx.ID_ANY, hotkeys_group_name,
                                                wx.DefaultPosition, wx.DefaultSize, 0)
        self.hotkeys_group_name.Wrap(-1)

        self.hotkeys_group_name.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(
        ), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString))

        hotkeys_group_name_sizer.Add(self.hotkeys_group_name, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.SetSizer(hotkeys_group_name_sizer)
        self.Layout()
        hotkeys_group_name_sizer.Fit(self)
