

import subprocess
import sys
import os

sys.path.append('..')

MAIN_CONST = "../code/autoclicker.py"
ICON_WINDOWS = ""
PROGRAM_NAME = "autoclicker"

line = "pyinstaller -F --distpath . --workpath . -n " + PROGRAM_NAME + " " + ICON_WINDOWS + " " + MAIN_CONST
print(line)
subprocess.call(line, shell=True)
# os.remove(PROGRAM_NAME + ".spec")
# os.chdir("build")

a = input("Press Enter to exit")