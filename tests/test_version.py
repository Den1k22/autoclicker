from __future__ import annotations

import unittest

from autoclicker.gui.dialogs.about import VERSION as ABOUT_VERSION
from autoclicker.version import VERSION


class VersionTests(unittest.TestCase):
    def test_about_dialog_uses_the_single_version_constant(self):
        self.assertEqual(ABOUT_VERSION, VERSION)
