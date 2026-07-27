from __future__ import annotations

import sys
from pathlib import Path


def application_dir() -> Path:
    """Return the portable directory that owns writable application files."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def config_path() -> Path:
    return application_dir() / "config" / "settings.ini"


def points_path() -> Path:
    return config_path().parent / "points.txt"


def legacy_points_path() -> Path:
    return application_dir() / "points.txt"


def default_settings_path() -> Path:
    return Path(__file__).resolve().parents[1] / "resources" / "default_settings.ini"
