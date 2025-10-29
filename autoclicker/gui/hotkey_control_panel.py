
import wx


class HotkeyControlPanel (wx.Panel):

    def __init__(self, parent, hotkey_name, hotkey_translated_name, hotkey_text, handler):
        wx.Panel.__init__(self, parent, wx.ID_ANY,
                          wx.DefaultPosition, wx.Size(-1, -1), wx.TAB_TRAVERSAL)

        self.SetMaxSize(wx.Size(-1, 40))

        hotkey_control_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.hotkey_name = wx.StaticText(self, wx.ID_ANY,
                                         hotkey_translated_name, wx.DefaultPosition, wx.Size(200, -1), 0)
        self.hotkey_name.Wrap(-1)

        self.hotkey_name.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT,
                                         wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))

        hotkey_control_sizer.Add(self.hotkey_name, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.hotkey_text = wx.TextCtrl(self, wx.ID_ANY,
                                       hotkey_text, wx.DefaultPosition, wx.Size(300, -1), style=wx.TE_PROCESS_ENTER, name=hotkey_name)

        self.hotkey_text.Bind(wx.EVT_TEXT_ENTER, handler)

        hotkey_control_sizer.Add(self.hotkey_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.SetSizer(hotkey_control_sizer)
        self.Layout()
        hotkey_control_sizer.Fit(self)
