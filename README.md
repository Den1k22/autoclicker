# Autoclicker

Autoclicker is a local Windows utility for repetitive actions in single-player
games. It records screen coordinates, clicks them once or continuously, and can
optionally watch a screen region for an exact RGB color before performing two
configured keyboard or mouse actions.

The program has a native wxPython GUI for settings and point management. Global
hotkeys remain active while another application has focus, so normal operation
does not require switching back to the GUI.

## Features

- Record cursor positions with global hotkeys.
- View, edit, reorder, remove, save, and load points in the GUI.
- Run the current point snapshot once or continuously.
- Generate a rectangular mesh from exactly three recorded points.
- Detect an exact configured RGB color inside an absolute screen region.
- Execute configurable keyboard combinations or mouse buttons in CV mode.
- Configure and immediately re-register global hotkeys.
- Keep ten named presets and switch between them with global Ctrl+number shortcuts.
- English and Russian interface languages.
- Portable `config/settings.ini` and preset point files beside the program.

Only one automation mode can run at a time. Closing the main window stops the
current worker, unregisters all global keyboard hooks, and exits completely.

## Running from source

Python 3.14 is required. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe main.py
```

Global keyboard hooks and pointer control can require suitable Windows
permissions.

## GUI

The left side of the window shows the active points document. Coordinates and
delays are editable. Point capture itself stays hotkey-driven because clicking a
GUI capture button would record the GUI's cursor position.

The right side contains:

- **General**: preset name, points file, language, and default point delays.
- **Computer vision**: capture region, exact target RGB value, timings, and
  actions.
- **Mesh**: width and height, including both endpoints.
- **Hotkeys**: every global action shortcut.

Use **Apply settings** to validate and save the full form. Hotkeys are
re-registered immediately. Other values are used by the next operation; an
already-running worker keeps its startup snapshot. A language change takes
effect after restarting.

The preset selector beside the settings buttons switches among ten presets.
Preset names, point paths, delays, mesh values, CV values, and action hotkeys
belong to the selected preset. Language and runtime mode remain global. Use
Ctrl+1 through Ctrl+9 for Presets 1 through 9 and Ctrl+0 for Preset 10.
Switching stops active automation and leaves it idle. Dirty points are saved
before the target preset is loaded; unapplied form edits are not saved.

The status bar shows the active mode and number of points. The bottom controls
call the same service operations as the global hotkeys.

## Hotkeys

Default shortcuts are defined in `config/settings.ini`:

| Setting | Action |
|---|---|
| `add_point_hotkey` | Record the current cursor position |
| `remove_last_point_hotkey` | Remove the last point |
| `remove_all_points_hotkey` | Clear all points |
| `start_autoclicker_hotkey` | Start continuous point clicking |
| `stop_autoclicker_hotkey` | Stop the active automation mode |
| `one_autoclick_run_hotkey` | Traverse the point snapshot once |
| `start_stop_cv_hotkey` | Start or stop CV mode |
| `exit_hotkey` | Close the application |

Each shortcut must be one key or one simultaneous combination accepted by the
`keyboard` library. Duplicate shortcuts are rejected. Ctrl+0 through Ctrl+9 are
reserved for preset selection and cannot be assigned to another action.

## Point files

Each preset has a `points_path` value. Relative paths are resolved from the
portable `config` directory, so the default `points.txt` means
`config/points.txt`. All ten presets initially share that path; choose another
file in **General**, **Load points**, or **Save points as** to give a preset its
own document. Existing root-level `points.txt` is copied into `config` during
the first compatible startup when the new destination does not exist.

Each non-comment line has this format:

```text
x,y,delay_before_ms,delay_after_ms
```

Loading is all-or-nothing. Blank lines and lines beginning with `#` are ignored.
An empty or comment-only document represents an empty point list. Negative
coordinates are supported for multi-monitor layouts. GUI **Load** and **Save
As** change the active document and persist its path for the current preset.

## CV actions

Detection uses an exact RGB match; no tolerance or color-space conversion is
applied beyond reversing RGB to OpenCV's BGR order.

Keyboard actions may be one key or one simultaneous combination, such as
`space`, `f5`, or `ctrl+shift+a`. Comma-separated sequences are not supported.
Mouse actions are:

- `left_button`
- `right_button`
- `middle_button`
- `x1_button`
- `x2_button`

When a target is detected after the cooldown, `first_action` executes and
`second_action` remains scheduled for `second_click_delay`, even if the target
disappears. A later qualifying detection may replace that deadline.

## Translations

English source messages are the fallback. Russian translations are stored in
`autoclicker/i18n/locales/ru/LC_MESSAGES`.

Update and compile catalogs from the repository root:

```powershell
$projectVersion = & .\.venv\Scripts\python.exe -c "from autoclicker.version import VERSION; print(VERSION)"
.\.venv\Scripts\pybabel.exe extract -F babel.cfg --project Autoclicker --version $projectVersion --copyright-holder Den1k22 --msgid-bugs-address https://github.com/Den1k22/autoclicker/issues -o autoclicker\i18n\autoclicker.pot .
.\.venv\Scripts\pybabel.exe update -i autoclicker\i18n\autoclicker.pot -d autoclicker\i18n\locales -l ru -D autoclicker
.\.venv\Scripts\pybabel.exe compile -d autoclicker\i18n\locales -D autoclicker
```

## Development

Desktop effects are isolated behind adapters and must be mocked in automated
tests. Runtime and development dependency versions are maintained once in
`pyproject.toml`; `requirements.txt` is a compatibility wrapper for tools that
still expect `pip install -r requirements.txt`. Run:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m compileall -q autoclicker tests main.py
```

Format Python with `autopep8` using a 120-character maximum line length.
Change `VERSION` in `autoclicker/version.py` when releasing a new version.
Setuptools and the About dialog both read that value.

## Building

The deterministic PyInstaller specification creates a single windowed
`build/autoclicker.exe` and bundles immutable defaults plus compiled
translations:

```powershell
.\.venv\Scripts\python.exe make_build\make_build.py
```

`make_build/autoclicker.spec` is a checked-in build recipe, not a generated
artifact. It defines the entry point and bundled package data. Change
`PROGRAM_NAME` in `make_build/make_build.py` to rename the executable. To add a
Windows icon later, set `ICON_WINDOWS` there to an `.ico` path relative to the
repository root.

The writable configuration is not embedded. On first launch, the executable
creates `config/settings.ini` beside itself. If that directory is not writable,
the GUI reports the problem instead of silently moving files elsewhere.
Existing single-preset files are migrated into Preset 1, while Presets 2–10 are
filled from immutable defaults. The active preset is stored in `[MAIN]`; each
preset uses `PRESET_n` and `PRESET_n.HOTKEYS`, `.DELAYS`, `.MESH`, `.CV`, and
`.POINTS` sections.
