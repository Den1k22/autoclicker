# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import runpy

from PyInstaller.utils.hooks import copy_metadata


project_root = Path(SPECPATH).resolve().parent
build_settings = runpy.run_path(str(project_root / "make_build" / "make_build.py"))
program_name = build_settings["PROGRAM_NAME"]
icon_windows = build_settings["ICON_WINDOWS"]
icon_path = str(project_root / icon_windows) if icon_windows else None

analysis = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=copy_metadata("den1k22-autoclicker") + [
        (
            str(project_root / "autoclicker" / "resources"),
            "autoclicker/resources",
        ),
        (
            str(project_root / "autoclicker" / "i18n" / "locales"),
            "autoclicker/i18n/locales",
        ),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(analysis.pure)

executable = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name=program_name,
    icon=icon_path,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
