import wx
from autoclicker.gui.main_frame import MainFrame


class AutoclickerApp(wx.App):
    def OnInit(self):
        frame = MainFrame(None)
        frame.Show()
        return True
