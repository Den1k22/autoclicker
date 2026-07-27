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
- English and Russian interface languages.
- Portable `config/settings.ini` and `points.txt` files beside the program.

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

- **General**: language and default point delays.
- **Computer vision**: capture region, exact target RGB value, timings, and
  actions.
- **Mesh**: width and height, including both endpoints.
- **Hotkeys**: every global action shortcut.

Use **Apply settings** to validate and save the full form. Hotkeys are
re-registered immediately. Other values are used by the next operation; an
already-running worker keeps its startup snapshot. A language change takes
effect after restarting.

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
`keyboard` library. Duplicate shortcuts are rejected.

## Point files

The default document is `points.txt` beside the executable and is loaded
automatically when present. Each non-comment line has this format:

```text
x,y,delay_before_ms,delay_after_ms
```

Loading is all-or-nothing. Blank lines and lines beginning with `#` are ignored.
An empty or comment-only document represents an empty point list. Negative
coordinates are supported for multi-monitor layouts. GUI **Load** and **Save
As** change the active document used by the GUI file actions.

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
.\.venv\Scripts\pybabel.exe extract -F babel.cfg --project Autoclicker --version 0.4.0 --copyright-holder Den1k22 --msgid-bugs-address https://github.com/Den1k22/autoclicker/issues -o autoclicker\i18n\autoclicker.pot .
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
