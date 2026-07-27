from __future__ import annotations

import unittest

from autoclicker.i18n import Translator


class TranslatorTests(unittest.TestCase):
    def test_english_uses_source_fallback(self):
        translator = Translator("en")
        self.assertEqual(translator("Points"), "Points")
        self.assertEqual(translator("Unknown message"), "Unknown message")

    def test_russian_catalog_and_plural_forms_are_loaded(self):
        translator = Translator("ru")
        self.assertEqual(translator("Points"), "Точки")
        self.assertEqual(translator("Add point"), "Добавить точку")
        self.assertEqual(translator("Preset"), "Пресет")
        self.assertEqual(
            translator.ngettext("{count} point", "{count} points", 5).format(count=5),
            "5 точек",
        )
