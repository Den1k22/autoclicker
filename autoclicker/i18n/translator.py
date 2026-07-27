from __future__ import annotations

import gettext
from pathlib import Path


DOMAIN = "autoclicker"
SUPPORTED_LANGUAGES = {"en": "English", "ru": "Русский"}


class Translator:
    def __init__(self, language: str, locales_dir: Path | None = None):
        self.language = language if language in SUPPORTED_LANGUAGES else "en"
        self.locales_dir = locales_dir or Path(__file__).resolve().parent / "locales"
        self._translation = gettext.translation(
            DOMAIN,
            localedir=self.locales_dir,
            languages=[self.language],
            fallback=True,
        )

    def gettext(self, message: str) -> str:
        return self._translation.gettext(message)

    def ngettext(self, singular: str, plural: str, count: int) -> str:
        return self._translation.ngettext(singular, plural, count)

    def __call__(self, message: str) -> str:
        return self.gettext(message)
