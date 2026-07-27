# Agent Guide

## Purpose and safety

This repository contains a personal Windows autoclicker for repetitive actions
in single-player games. It records user-selected screen coordinates and clicks
their immutable snapshot once or continuously. Optional CV mode watches a
configured screen region for one exact RGB color, performs a first configured
action, waits, and performs a second action.

Keep changes limited to user-controlled local automation. Do not add anti-cheat
bypasses, process injection, credential handling, remote control, or features
that hide automation from a game or service.

## Platform and entry point

- Python 3.14 and Windows are the supported runtime.
- Install development dependencies with
  `.\.venv\Scripts\python.exe -m pip install -e ".[dev]"`.
- Run from the repository root with
  `.\.venv\Scripts\python.exe main.py`.
- Root `main.py` is a thin entry point for `autoclicker.app.main()`.
- wxPython owns the main event loop. Global hotkeys remain active while other
  applications have focus.
- `keyboard`, `pynput`, and `mss` can require suitable Windows permissions.
- Never trigger real global hooks, pointer movement, clicks, key presses, or
  screen capture during automated tests.

## Repository map

- `autoclicker/app.py`: application composition and wx lifecycle.
- `autoclicker/automation/`: point model/storage, point files, mesh generation,
  CV runner, and the thread-safe `AutomationService`.
- `autoclicker/adapters/`: keyboard, mouse, action dispatch, and screen-capture
  boundaries for third-party desktop APIs.
- `autoclicker/settings/`: typed immutable settings and atomic INI repository.
- `autoclicker/gui/`: wx frame, GUI controller, dialogs, and panels.
- `autoclicker/i18n/`: gettext translator, template, Russian PO, and compiled MO.
- `autoclicker/helpers/`: portable path resolution and time conversion only.
- `autoclicker/resources/default_settings.ini`: immutable first-run defaults.
- `config/settings.ini`: portable writable user configuration.
- `tests/`: standard-library `unittest` coverage with mocked desktop adapters.
- `make_build/autoclicker.spec`: checked-in deterministic one-file/windowed
  PyInstaller recipe; it consumes `PROGRAM_NAME` and `ICON_WINDOWS` from
  `make_build/make_build.py`.

## Runtime invariants

### Points

- `Point` is immutable and stores milliseconds.
- Adding a point records the current cursor location and current default delays.
- Each run receives a tuple snapshot. Later point edits affect the next run only.
- A point run moves, waits before, left-clicks, and waits after. Cancellation
  waits are interruptible.
- The active point document defaults to portable `points.txt`. GUI Open/Save As
  changes the active path used by GUI file actions.
- Each non-comment row is `x,y,delay_before_ms,delay_after_ms`. Loading is
  all-or-nothing and supports signed coordinates. Empty or comment-only files
  represent an empty point list.
- Do not show a save/discard confirmation when the current point list is empty,
  even if its internal document state is dirty.
- Mesh creation requires exactly three points. Width and height include both
  endpoints and must be greater than 1.

### CV

- CV receives an immutable `CvSettings` snapshot at worker startup; configuration
  is never read at module import.
- Monitor top/left are absolute coordinates and may be negative. Width and height
  must be positive.
- RGB is reversed to BGR for OpenCV. Matching remains exact through `cv2.inRange`
  with identical bounds.
- A qualifying detection executes the first action and schedules the second.
  The second executes after its delay even if the target disappears. A later
  qualifying detection may replace the pending deadline.
- Mouse actions are `left_button`, `right_button`, `middle_button`, `x1_button`,
  and `x2_button`. Other actions must be one keyboard key or simultaneous
  combination; comma-separated sequences are rejected.

### Threads and lifecycle

- `RunMode` is one of idle, points once, points continuous, or CV. Modes are
  mutually exclusive.
- Worker threads are daemon threads and use cancellation events.
- Hotkey callbacks and GUI controls call the same `AutomationService`.
- Worker and hotkey threads never access wx widgets directly. GUI updates use
  `wx.CallAfter`.
- Closing the main window stops work, unregisters every global hook, and exits.
- Account for rapid repeated starts/stops and make shutdown idempotent.

## Settings and localization

- `SettingsRepository` preserves unknown INI values, fills missing known values
  from immutable defaults, and replaces files atomically.
- All settings are parsed into frozen dataclasses and validated before hotkey
  registration or save.
- Hotkeys are required, valid, and unique. Replacement rolls back to the
  previous registration set on failure.
- Registered global hotkeys are suppressed so their final key cannot also
  activate a focused wx control.
- Hotkey changes apply immediately. Delays, mesh, and CV values affect the next
  operation. Language is `en` or `ru` and applies after restart.
- English strings are source fallback. Russian translations must remain complete.
- Do not install gettext functions into Python builtins.
- After UI text changes, update and compile catalogs:

```powershell
.\.venv\Scripts\pybabel.exe extract -F babel.cfg -o autoclicker\i18n\autoclicker.pot .
.\.venv\Scripts\pybabel.exe update -i autoclicker\i18n\autoclicker.pot -d autoclicker\i18n\locales -l ru -D autoclicker
.\.venv\Scripts\pybabel.exe compile -d autoclicker\i18n\locales -D autoclicker
```

## Development workflow

Use package imports and type hints. Keep desktop side effects behind adapters
and inject mocks/fakes in tests. Format Python with autopep8 at 120 columns.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m compileall -q autoclicker tests main.py
```

Build with:

```powershell
.\.venv\Scripts\python.exe make_build\make_build.py
```

The output is `build/autoclicker.exe`. Do not commit `points.txt`, logs, build
output, caches, virtual environments, or generated PyInstaller work files.

Update README, defaults, active INI, translation catalogs, tests, and build data
together when changing user-facing settings, hotkeys, point formats, actions,
or UI behavior.
