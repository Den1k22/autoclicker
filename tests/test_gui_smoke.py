from __future__ import annotations

import unittest

import wx

from autoclicker.gui.main_frame import MainFrame
from autoclicker.i18n import Translator
from tests.factories import make_settings


class GuiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = wx.App(False)

    @classmethod
    def tearDownClass(cls):
        cls.app.Destroy()

    def test_hidden_main_frame_builds_all_primary_controls(self):
        settings = make_settings()
        frame = MainFrame(settings, settings, Translator("en"))
        try:
            self.assertEqual(frame.points_panel.table.GetColumnCount(), 5)
            self.assertEqual(frame.settings_panel.notebook.GetPageCount(), 4)
            self.assertEqual(len(frame.settings_panel.hotkeys.controls), 8)
            self.assertFalse(frame.stop_button.IsEnabled())
            general = frame.settings_panel.general
            frame.Layout()
            self.assertLess(
                general.language_note.GetPosition().y,
                general.delay_before.GetPosition().y,
            )
        finally:
            frame.Destroy()
