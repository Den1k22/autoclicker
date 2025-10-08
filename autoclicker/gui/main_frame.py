from autoclicker.gui.hotkey_control_panel import HotkeyControlPanel
from autoclicker.gui.hotkeys_group_name_panel import HotkeysGroupNamePanel
from autoclicker.code.settings import GROUPED_HOTKEYS
import wx

import gettext
t = gettext.gettext


class MainFrame (wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                          size=wx.Size(800, 600), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        main_frame_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.points_setion_panel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.points_setion_panel.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        self.points_setion_panel.SetMaxSize(wx.Size(300, -1))

        points_section_sizer = wx.BoxSizer(wx.VERTICAL)

        self.points_section_name = wx.StaticText(self.points_setion_panel, wx.ID_ANY, t(
            u"Points"), wx.DefaultPosition, wx.DefaultSize, 0)
        self.points_section_name.Wrap(-1)

        self.points_section_name.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(
        ), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString))

        points_section_sizer.Add(self.points_section_name, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        self.points_list = wx.ListCtrl(self.points_setion_panel, wx.ID_ANY,
                                       wx.DefaultPosition, wx.DefaultSize, wx.LC_ALIGN_LEFT | wx.LC_ICON)
        self.points_list.SetMinSize(wx.Size(300, 500))

        points_section_sizer.Add(self.points_list, 0, wx.ALL, 5)

        self.points_setion_panel.SetSizer(points_section_sizer)
        self.points_setion_panel.Layout()
        points_section_sizer.Fit(self.points_setion_panel)
        main_frame_sizer.Add(self.points_setion_panel, 1, wx.EXPAND | wx.ALL, 5)

        self.settings_notebook = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
        self.settings_notebook.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

        self.general_panel = wx.Panel(self.settings_notebook, wx.ID_ANY,
                                      wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        general_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.general_panel.SetSizer(general_panel_sizer)
        self.general_panel.Layout()
        general_panel_sizer.Fit(self.general_panel)
        self.settings_notebook.AddPage(self.general_panel, t(u"General"), False)
        self.cv_panel = wx.Panel(self.settings_notebook, wx.ID_ANY,
                                 wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        cv_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.cv_panel.SetSizer(cv_panel_sizer)
        self.cv_panel.Layout()
        cv_panel_sizer.Fit(self.cv_panel)
        self.settings_notebook.AddPage(self.cv_panel, t(u"Computer vision"), False)
        self.mesh_panel = wx.Panel(self.settings_notebook, wx.ID_ANY,
                                   wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        mesh_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        mesh_options_radio_boxChoices = [t(u"3 dots"), t(u"1 dot")]
        self.mesh_options_radio_box = wx.RadioBox(self.mesh_panel, wx.ID_ANY, t(
            u"Mesh options"), wx.DefaultPosition, wx.DefaultSize, mesh_options_radio_boxChoices, 1, wx.RA_SPECIFY_ROWS)
        self.mesh_options_radio_box.SetSelection(0)
        mesh_panel_sizer.Add(self.mesh_options_radio_box, 0, wx.ALL, 5)

        self.valuel_int_panel = wx.Panel(self.mesh_panel, wx.ID_ANY, wx.DefaultPosition,
                                         wx.Size(-1, -1), wx.TAB_TRAVERSAL)
        self.valuel_int_panel.SetMaxSize(wx.Size(-1, 40))

        value_int_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.value_int_name = wx.StaticText(self.valuel_int_panel, wx.ID_ANY, t(
            u"Value Name"), wx.DefaultPosition, wx.Size(200, -1), 0)
        self.value_int_name.Wrap(-1)

        self.value_int_name.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT,
                                    wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))

        value_int_sizer.Add(self.value_int_name, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.velue_int_spin_ctrl = wx.SpinCtrl(
            self.valuel_int_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 999999999, 0)
        self.velue_int_spin_ctrl.SetMinSize(wx.Size(100, -1))

        value_int_sizer.Add(self.velue_int_spin_ctrl, 0, wx.ALL, 5)

        self.valuel_int_panel.SetSizer(value_int_sizer)
        self.valuel_int_panel.Layout()
        value_int_sizer.Fit(self.valuel_int_panel)
        mesh_panel_sizer.Add(self.valuel_int_panel, 1, wx.EXPAND | wx.ALL, 5)

        self.mesh_panel.SetSizer(mesh_panel_sizer)
        self.mesh_panel.Layout()
        mesh_panel_sizer.Fit(self.mesh_panel)
        self.settings_notebook.AddPage(self.mesh_panel, t(u"Mesh"), False)
        self.scrolled_controls_panel = wx.ScrolledWindow(
            self.settings_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL | wx.VSCROLL)
        self.scrolled_controls_panel.SetScrollRate(5, 5)
        controls_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        for hotkeys_group_name, hotkeys in GROUPED_HOTKEYS:
            hotkeys_group_name_panel = HotkeysGroupNamePanel(self.scrolled_controls_panel, hotkeys_group_name)
            controls_panel_sizer.Add(hotkeys_group_name_panel, 1, wx.ALL | wx.EXPAND, 5)

            for name, text in hotkeys:
                hotkey_panel = HotkeyControlPanel(self.scrolled_controls_panel, name, text)
                controls_panel_sizer.Add(hotkey_panel, 1, wx.ALL | wx.EXPAND, 5)

        self.scrolled_controls_panel.SetSizer(controls_panel_sizer)
        self.scrolled_controls_panel.Layout()
        controls_panel_sizer.Fit(self.scrolled_controls_panel)
        self.settings_notebook.AddPage(self.scrolled_controls_panel, t(u"Controls"), True)

        main_frame_sizer.Add(self.settings_notebook, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(main_frame_sizer)
        self.Layout()
        self.menu_bar = wx.MenuBar(0)
        self.file_menu = wx.Menu()
        self.save_menu_item = wx.MenuItem(self.file_menu, wx.ID_ANY, t(
            u"Save") + u"\t" + u"Ctrl+S", wx.EmptyString, wx.ITEM_NORMAL)
        self.file_menu.Append(self.save_menu_item)

        self.load_menu_item = wx.MenuItem(self.file_menu, wx.ID_ANY, t(
            u"Load") + u"\t" + u"Ctrl+L", wx.EmptyString, wx.ITEM_NORMAL)
        self.file_menu.Append(self.load_menu_item)

        self.exit_menu_item = wx.MenuItem(self.file_menu, wx.ID_ANY, t(u"Exit"), wx.EmptyString, wx.ITEM_NORMAL)
        self.file_menu.Append(self.exit_menu_item)

        self.menu_bar.Append(self.file_menu, t(u"File"))

        self.help_menu = wx.Menu()
        self.about_menu_item = wx.MenuItem(self.help_menu, wx.ID_ANY, t(
            u"About...") + u"\t" + u"F1", wx.EmptyString, wx.ITEM_NORMAL)
        self.help_menu.Append(self.about_menu_item)

        self.menu_bar.Append(self.help_menu, t(u"Help"))

        self.SetMenuBar(self.menu_bar)

        self.Centre(wx.BOTH)

        # Connect Events
        self.Bind(wx.EVT_MENU, self.onSaveClick, id=self.save_menu_item.GetId())
        self.Bind(wx.EVT_MENU, self.onLoadClick, id=self.load_menu_item.GetId())
        self.Bind(wx.EVT_MENU, self.onExitClick, id=self.exit_menu_item.GetId())
        self.Bind(wx.EVT_MENU, self.onAboutClick, id=self.about_menu_item.GetId())

    def __del__(self):
        pass

    # Virtual event handlers, override them in your derived class
    def onSaveClick(self, event):
        event.Skip()

    def onLoadClick(self, event):
        event.Skip()

    def onExitClick(self, event):
        event.Skip()

    def onAboutClick(self, event):
        event.Skip()
