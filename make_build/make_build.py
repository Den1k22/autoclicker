from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SPEC_FILE = Path(__file__).resolve().parent / "autoclicker.spec"
BUILD_DIRECTORY = PROJECT_ROOT / "build"
PROGRAM_NAME = "autoclicker"
# Set this to an .ico path relative to PROJECT_ROOT when an icon is available.
ICON_WINDOWS = ""


def main() -> int:
    pybabel = Path(sys.executable).with_name("pybabel.exe")
    subprocess.run(
        [
            str(pybabel),
            "compile",
            "-d",
            str(PROJECT_ROOT / "autoclicker" / "i18n" / "locales"),
            "-D",
            "autoclicker",
        ],
        cwd=PROJECT_ROOT,
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--noconfirm",
            "--distpath",
            str(BUILD_DIRECTORY),
            "--workpath",
            str(BUILD_DIRECTORY / "work"),
            str(SPEC_FILE),
        ],
        cwd=PROJECT_ROOT,
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
