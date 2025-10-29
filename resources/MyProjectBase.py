# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

import gettext
_ = gettext.gettext

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 1083,653 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        main_frame_sizer = wx.BoxSizer( wx.HORIZONTAL )

        self.points_setion_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.points_setion_panel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
        self.points_setion_panel.SetMaxSize( wx.Size( 300,-1 ) )

        points_section_sizer = wx.BoxSizer( wx.VERTICAL )

        self.points_section_name = wx.StaticText( self.points_setion_panel, wx.ID_ANY, _(u"Points"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.points_section_name.Wrap( -1 )

        self.points_section_name.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

        points_section_sizer.Add( self.points_section_name, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )

        self.points_list = wx.ListCtrl( self.points_setion_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_ALIGN_LEFT|wx.LC_ICON )
        self.points_list.SetMinSize( wx.Size( 200,500 ) )

        points_section_sizer.Add( self.points_list, 0, wx.ALL, 5 )


        self.points_setion_panel.SetSizer( points_section_sizer )
        self.points_setion_panel.Layout()
        points_section_sizer.Fit( self.points_setion_panel )
        main_frame_sizer.Add( self.points_setion_panel, 1, wx.EXPAND |wx.ALL, 5 )

        self.settings_notebook = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.settings_notebook.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

        self.general_panel = wx.Panel( self.settings_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        general_panel_sizer = wx.BoxSizer( wx.HORIZONTAL )


        self.general_panel.SetSizer( general_panel_sizer )
        self.general_panel.Layout()
        general_panel_sizer.Fit( self.general_panel )
        self.settings_notebook.AddPage( self.general_panel, _(u"General"), False )
        self.cv_panel = wx.Panel( self.settings_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        cv_panel_sizer = wx.BoxSizer( wx.HORIZONTAL )


        self.cv_panel.SetSizer( cv_panel_sizer )
        self.cv_panel.Layout()
        cv_panel_sizer.Fit( self.cv_panel )
        self.settings_notebook.AddPage( self.cv_panel, _(u"Computer vision"), False )
        self.mesh_panel = wx.Panel( self.settings_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        mesh_panel_sizer = wx.BoxSizer( wx.VERTICAL )

        mesh_options_radio_boxChoices = [ _(u"3 dots"), _(u"1 dot") ]
        self.mesh_options_radio_box = wx.RadioBox( self.mesh_panel, wx.ID_ANY, _(u"Mesh options"), wx.DefaultPosition, wx.DefaultSize, mesh_options_radio_boxChoices, 1, wx.RA_SPECIFY_ROWS )
        self.mesh_options_radio_box.SetSelection( 0 )
        mesh_panel_sizer.Add( self.mesh_options_radio_box, 0, wx.ALL, 5 )

        self.valuel_int_panel = wx.Panel( self.mesh_panel, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TAB_TRAVERSAL )
        self.valuel_int_panel.SetMaxSize( wx.Size( -1,40 ) )

        value_int_sizer = wx.BoxSizer( wx.HORIZONTAL )

        self.value_int_name = wx.StaticText( self.valuel_int_panel, wx.ID_ANY, _(u"Value Name"), wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
        self.value_int_name.Wrap( -1 )

        self.value_int_name.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

        value_int_sizer.Add( self.value_int_name, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.velue_int_spin_ctrl = wx.SpinCtrl( self.valuel_int_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 999999999, 0 )
        self.velue_int_spin_ctrl.SetMinSize( wx.Size( 100,-1 ) )

        value_int_sizer.Add( self.velue_int_spin_ctrl, 0, wx.ALL, 5 )


        self.valuel_int_panel.SetSizer( value_int_sizer )
        self.valuel_int_panel.Layout()
        value_int_sizer.Fit( self.valuel_int_panel )
        mesh_panel_sizer.Add( self.valuel_int_panel, 1, wx.EXPAND |wx.ALL, 5 )


        self.mesh_panel.SetSizer( mesh_panel_sizer )
        self.mesh_panel.Layout()
        mesh_panel_sizer.Fit( self.mesh_panel )
        self.settings_notebook.AddPage( self.mesh_panel, _(u"Mesh"), False )
        self.controls_panel = wx.Panel( self.settings_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        controls_panel_sizer = wx.BoxSizer( wx.VERTICAL )

        self.hotkeys_group_name_panel = wx.Panel( self.controls_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.hotkeys_group_name_panel.SetMaxSize( wx.Size( -1,30 ) )

        hotkeys_group_name_sizer = wx.BoxSizer( wx.HORIZONTAL )

        self.hotkeys_group_name = wx.StaticText( self.hotkeys_group_name_panel, wx.ID_ANY, _(u"Group name"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.hotkeys_group_name.Wrap( -1 )

        self.hotkeys_group_name.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

        hotkeys_group_name_sizer.Add( self.hotkeys_group_name, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        self.hotkeys_group_name_panel.SetSizer( hotkeys_group_name_sizer )
        self.hotkeys_group_name_panel.Layout()
        hotkeys_group_name_sizer.Fit( self.hotkeys_group_name_panel )
        controls_panel_sizer.Add( self.hotkeys_group_name_panel, 1, wx.ALL|wx.EXPAND, 5 )

        self.hotkey_control_panel = wx.Panel( self.controls_panel, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TAB_TRAVERSAL )
        self.hotkey_control_panel.SetMaxSize( wx.Size( -1,40 ) )

        hotkey_control_sizer = wx.BoxSizer( wx.HORIZONTAL )

        self.hotkey_name = wx.StaticText( self.hotkey_control_panel, wx.ID_ANY, _(u"Hotkey Name"), wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
        self.hotkey_name.Wrap( -1 )

        self.hotkey_name.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

        hotkey_control_sizer.Add( self.hotkey_name, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.hotkey_text = wx.TextCtrl( self.hotkey_control_panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 300,-1 ), 0 )
        hotkey_control_sizer.Add( self.hotkey_text, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        self.hotkey_control_panel.SetSizer( hotkey_control_sizer )
        self.hotkey_control_panel.Layout()
        hotkey_control_sizer.Fit( self.hotkey_control_panel )
        controls_panel_sizer.Add( self.hotkey_control_panel, 1, wx.ALL|wx.EXPAND, 5 )


        self.controls_panel.SetSizer( controls_panel_sizer )
        self.controls_panel.Layout()
        controls_panel_sizer.Fit( self.controls_panel )
        self.settings_notebook.AddPage( self.controls_panel, _(u"Controls"), True )

        main_frame_sizer.Add( self.settings_notebook, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( main_frame_sizer )
        self.Layout()
        self.menu_bar = wx.MenuBar( 0 )
        self.file_menu = wx.Menu()
        self.save_menu_item = wx.MenuItem( self.file_menu, wx.ID_ANY, _(u"Save")+ u"\t" + u"Ctrl+S", wx.EmptyString, wx.ITEM_NORMAL )
        self.file_menu.Append( self.save_menu_item )

        self.load_menu_item = wx.MenuItem( self.file_menu, wx.ID_ANY, _(u"Load")+ u"\t" + u"Ctrl+L", wx.EmptyString, wx.ITEM_NORMAL )
        self.file_menu.Append( self.load_menu_item )

        self.exit_menu_item = wx.MenuItem( self.file_menu, wx.ID_ANY, _(u"Exit"), wx.EmptyString, wx.ITEM_NORMAL )
        self.file_menu.Append( self.exit_menu_item )

        self.menu_bar.Append( self.file_menu, _(u"File") )

        self.help_menu = wx.Menu()
        self.about_menu_item = wx.MenuItem( self.help_menu, wx.ID_ANY, _(u"About...")+ u"\t" + u"F1", wx.EmptyString, wx.ITEM_NORMAL )
        self.help_menu.Append( self.about_menu_item )

        self.menu_bar.Append( self.help_menu, _(u"Help") )

        self.SetMenuBar( self.menu_bar )


        self.Centre( wx.BOTH )

        # Connect Events
        self.hotkey_text.Bind( wx.EVT_TEXT_ENTER, self.onHotkeyValueChanged )
        self.Bind( wx.EVT_MENU, self.onSaveClick, id = self.save_menu_item.GetId() )
        self.Bind( wx.EVT_MENU, self.onLoadClick, id = self.load_menu_item.GetId() )
        self.Bind( wx.EVT_MENU, self.onExitClick, id = self.exit_menu_item.GetId() )
        self.Bind( wx.EVT_MENU, self.onAboutClick, id = self.about_menu_item.GetId() )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def onHotkeyValueChanged( self, event ):
        event.Skip()

    def onSaveClick( self, event ):
        event.Skip()

    def onLoadClick( self, event ):
        event.Skip()

    def onExitClick( self, event ):
        event.Skip()

    def onAboutClick( self, event ):
        event.Skip()


###########################################################################
## Class AboutDialog
###########################################################################

class AboutDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        about_autoclicker_sizer = wx.BoxSizer( wx.VERTICAL )

        self.about_autoclicker_message_label = wx.StaticText( self, wx.ID_ANY, _(u"Thank you for using Autoclicker!"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.about_autoclicker_message_label.Wrap( -1 )

        about_autoclicker_sizer.Add( self.about_autoclicker_message_label, 0, wx.ALL, 5 )

        version_sizer = wx.BoxSizer( wx.HORIZONTAL )

        self.version_label = wx.StaticText( self, wx.ID_ANY, _(u"Version:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.version_label.Wrap( -1 )

        version_sizer.Add( self.version_label, 0, wx.ALL, 5 )

        self.version_value = wx.StaticText( self, wx.ID_ANY, _(u"0.3"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.version_value.Wrap( -1 )

        version_sizer.Add( self.version_value, 0, wx.ALL, 5 )


        about_autoclicker_sizer.Add( version_sizer, 1, wx.EXPAND, 5 )


        self.SetSizer( about_autoclicker_sizer )
        self.Layout()
        about_autoclicker_sizer.Fit( self )

        self.Centre( wx.BOTH )

    def __del__( self ):
        pass


