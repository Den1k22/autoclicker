
import gettext
import os
import wx

from autoclicker.gui.main_frame import MainFrame

APP_NAME = "autoclicker"
LANG_CODE = "en"

locales_dir = os.path.join(os.path.dirname(__file__), "..", "resources", "locales")
print(locales_dir)
gettext.bindtextdomain(APP_NAME, locales_dir)
gettext.textdomain(APP_NAME)
gettext.translation(APP_NAME, locales_dir, languages=[LANG_CODE], fallback=True).install()


class AutoclickerApp(wx.App):
    def OnInit(self):

        self.locale = wx.Locale()

        locales_dir = os.path.join(os.path.dirname(__file__), "resources", "locales")

        if LANG_CODE == "ru":
            self.locale.Init(wx.LANGUAGE_RUSSIAN)
        else:
            self.locale.Init(wx.LANGUAGE_ENGLISH)

        self.locale.AddCatalogLookupPathPrefix(locales_dir)
        self.locale.AddCatalog(APP_NAME)

        frame = MainFrame(None)
        frame.Show()
        return True
