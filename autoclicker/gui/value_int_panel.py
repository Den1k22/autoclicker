
import wx


class ValueIntPanel (wx.Panel):

    def __init__(self, parent, name, value: int):
        wx.Panel.__init__(self, parent, wx.ID_ANY,
                          wx.DefaultPosition, wx.Size(-1, -1), wx.TAB_TRAVERSAL)

        self.SetMaxSize(wx.Size(-1, 40))

        value_int_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.value_int_name = wx.StaticText(self, wx.ID_ANY, name, wx.DefaultPosition, wx.Size(200, -1), 0)
        self.value_int_name.Wrap(-1)

        self.value_int_name.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT,
                                    wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))

        value_int_sizer.Add(self.value_int_name, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.velue_int_spin_ctrl = wx.SpinCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 999999999, value)
        self.velue_int_spin_ctrl.SetMinSize(wx.Size(100, -1))

        value_int_sizer.Add(self.velue_int_spin_ctrl, 0, wx.ALL, 5)

        self.SetSizer(value_int_sizer)
        self.Layout()
        value_int_sizer.Fit(self)
