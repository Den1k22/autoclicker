
import wx
from autoclicker.gui.about_dialog import AboutDialog

import gettext
t = gettext.gettext


class AutoClickerMenuBar (wx.MenuBar):

    def __init__(self, parent_frame):
        wx.MenuBar.__init__(self, 0)
        self.parent_frame = parent_frame

        self.file_menu = wx.Menu()
        self.save_menu_item = wx.MenuItem(self.file_menu, wx.ID_ANY, t(
            "Save") + "\t" + "Ctrl+S", wx.EmptyString, wx.ITEM_NORMAL)
        self.file_menu.Append(self.save_menu_item)

        self.load_menu_item = wx.MenuItem(self.file_menu, wx.ID_ANY, t(
            "Load") + "\t" + "Ctrl+L", wx.EmptyString, wx.ITEM_NORMAL)
        self.file_menu.Append(self.load_menu_item)

        self.exit_menu_item = wx.MenuItem(self.file_menu, wx.ID_ANY, t("Exit"), wx.EmptyString, wx.ITEM_NORMAL)
        self.file_menu.Append(self.exit_menu_item)

        self.Append(self.file_menu, t("File"))

        self.help_menu = wx.Menu()
        self.about_menu_item = wx.MenuItem(self.help_menu, wx.ID_ANY, t(
            "About...") + "\t" + "F1", wx.EmptyString, wx.ITEM_NORMAL)
        self.help_menu.Append(self.about_menu_item)

        self.Append(self.help_menu, t("Help"))

        self.Bind(wx.EVT_MENU, self.onSaveClick, id=self.save_menu_item.GetId())
        self.Bind(wx.EVT_MENU, self.onLoadClick, id=self.load_menu_item.GetId())
        self.Bind(wx.EVT_MENU, self.onExitClick, id=self.exit_menu_item.GetId())
        self.Bind(wx.EVT_MENU, self.onAboutClick, id=self.about_menu_item.GetId())

    def onSaveClick(self, event):
        print("save")
        event.Skip()

    def onLoadClick(self, event):
        print("load")
        event.Skip()

    def onExitClick(self, event):
        event.Skip()
        frame = self.GetTopLevelParent()
        frame.Close(True)

    def onAboutClick(self, event):
        event.Skip()
        dlg = AboutDialog(self.parent_frame)
        dlg.ShowModal()
        dlg.Destroy()
