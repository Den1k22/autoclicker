# Agent Guide

## Project purpose

This repository contains a personal Windows autoclicker for repetitive actions in
single-player games. Its primary mode records screen coordinates chosen by the
user and clicks them once or repeatedly. Its optional computer-vision (CV) mode
watches a configured screen region for an exact RGB color, performs a first
keyboard or mouse action, waits for a configured delay, and then performs a
second action.

Keep changes aligned with user-controlled, local automation. Do not add
anti-cheat bypasses, process injection, credential handling, remote control, or
features intended to hide automation from a game or service.

## Platform and entry point

- The application is Python and is designed for Windows.
- Run it from the repository root so relative paths resolve correctly:
  `.\.venv\Scripts\python.exe code\autoclicker.py`
- The executable build entry point is `code/autoclicker.py`.
- There is no GUI. Users control the running process through global hotkeys from
  `config/settings.ini`; status is printed to the console.
- `keyboard` supplies global keyboard hooks/actions, `pynput` controls the
  pointer and mouse buttons, `mss` captures the screen, and OpenCV/NumPy perform
  color detection.
- Global input hooks or mouse control can require suitable Windows permissions.
  Do not trigger real hotkeys, pointer movement, clicks, or key presses during
  automated tests.

## Repository map

- `code/autoclicker.py`: orchestration, hotkey callbacks, point execution,
  point-file persistence, mesh generation, startup, shutdown, and worker-thread
  creation.
- `code/points_controller.py`: in-memory `Point` model and point storage.
  `get_points()` returns a tuple snapshot.
- `code/mouse_controller.py`: `pynput` mouse adapter and supported configurable
  mouse actions.
- `code/keyboard_controller.py`: `keyboard` adapter, hotkey registration and
  cleanup, and validation of a single key or simultaneous combination.
- `code/action_controller.py`: parses a configured CV action as either a
  keyboard action or a named mouse-button action, then dispatches it.
- `code/cv_controller.py`: import-time CV configuration and the screen-capture
  loop.
- `code/thread_controller.py`: shared boolean run/stop state used by background
  work.
- `code/hotkeys_storage.py`: required hotkey names and their loaded values.
- `code/settings.py`: INI loading, defaults, and settings access.
- `code/util.py`: millisecond/second conversion and point-file integer checks.
- `config/settings.ini`: active runtime settings.
- `config/car_mechanic_simulator_cv_params.txt`: reference presets only; the
  application does not load this file.
- `tests/`: `unittest` tests that mock system input and screen capture.
- `make_build/make_build.py`: PyInstaller helper. It assumes its working
  directory is `make_build` and pauses for input when finished.
- `requirements.txt`: pinned development, runtime, and packaging dependencies.

## Runtime behavior and invariants

### Recorded-point mode

- Adding a point records the current cursor coordinates with default delays of
  50 ms before and after its click.
- Starting a run passes the current tuple of points to a daemon thread named
  `auto_clicker_job`. Later edits to point storage do not alter that active run.
- Continuous mode loops over the snapshot until stopped. One-run mode traverses
  it once. Starting either mode is ignored while a thread with that name exists.
- Each point moves the cursor, waits its `delay_before`, left-clicks, then waits
  its `delay_after`. Preserve stop checks between points unless deliberately
  changing interruption semantics.
- `points.txt` is a generated, ignored file in the process working directory.
  Each non-comment row is `x,y,delay_before_ms,delay_after_ms`. Loading is
  all-or-nothing and replaces current points only after at least one valid row
  has been parsed.
- Mesh creation requires exactly three points: the first is the origin, the
  second determines horizontal extent, and the third determines vertical
  extent. `amount_width` and `amount_height` include both endpoints and must
  remain greater than 1 to avoid division by zero.

### CV mode

- `cv_controller.py` reads its region, color, timing, and action values at module
  import time. Tests that change those settings must reload or patch the module;
  changing the INI does not alter a process that is already running.
- `monitor_region_*` values use absolute screen coordinates and pixels.
- RGB values from the INI are reversed into BGR for OpenCV.
- Detection currently requires an exact pixel-color match via `cv2.inRange`
  with identical lower and upper bounds. Do not silently introduce a tolerance
  or a different color space.
- When a contour is present and `click_cooldown` has elapsed, `first_action`
  executes and schedules `second_action` for `second_click_delay` later.
  The second action executes after that delay even if the target color is no
  longer present. A later qualifying detection can replace the pending
  second-action deadline.
- Supported mouse action names are `left_button`, `right_button`,
  `middle_button`, `x1_button`, and `x2_button`. Other non-empty actions must be
  one keyboard key or one simultaneous combination accepted by `keyboard`;
  comma-separated sequences are intentionally rejected.

### Threads and shutdown

- The application currently shares one `ThreadController` between recorded-point
  and CV work. Starting/stopping one mode can therefore affect the other. Treat
  this as existing behavior and test any change to it explicitly.
- Worker threads are daemon threads. The main thread blocks on an exit event.
- The exit callback stops work and signals that event. `main()` must always
  remove global keyboard hooks in its `finally` block.
- Avoid long blocking operations in hotkey callbacks and worker loops. When
  changing threaded code, account for rapid repeated hotkeys and clean shutdown.

## Configuration rules

- `settings.py` expects `config/settings.ini` relative to the current working
  directory. Prefer running commands from the repository root.
- Every tag in `hotkeys_storage.HOTKEY_TAGS` is required. When adding or
  removing a hotkey, update together:
  `settings.DEFAULTS`, `config/settings.ini`, `hotkeys_storage.py`,
  `autoclicker.set_hotkeys()`, and the README.
- Numeric INI values are strings and are converted at their use sites.
  Validate new numeric values before worker threads start.
- When adding a CV action type, update parsing, execution, startup validation,
  tests, configuration examples, and the README as one change.
- Keep user-specific screen coordinates and colors configurable rather than
  hard-coding them in Python.

## Development workflow

Use the repository virtual environment when available:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m compileall -q code tests
```

The test suite uses standard-library `unittest`; no pytest dependency is
required. Add focused regression tests under `tests/` for behavior changes.
Mock `keyboard`, `pynput`, `mss`, time, and action dispatch at the project
adapter boundary so tests never operate the real desktop.

Format Python with `autopep8` using a 120-character maximum line length. Keep the
current flat-module import style because the entry point is run directly from
`code/`. If converting `code/` into a package, update the entry point, tests,
and PyInstaller build together.

To build the single-file executable:

```powershell
Set-Location make_build
..\.venv\Scripts\python.exe make_build.py
```

The output goes to `build/`. Building is slower and interactive, so unit tests
and compilation are the normal verification for code-only changes.

## Change checklist

1. Read the affected adapters, orchestration code, configuration, and tests
   before editing; several modules initialize global state at import time.
2. Preserve existing user changes and do not commit generated `points.txt`,
   `build/`, `.spec`, cache, or virtual-environment files.
3. Keep real desktop side effects behind `keyboard_controller`,
   `mouse_controller`, and `cv_controller`, and mock them in tests.
4. Update `README.md` and `config/settings.ini` when user-facing hotkeys,
   actions, point formats, or CV semantics change.
5. Run the complete unit-test and compilation commands above from the repository
   root. Report any Windows-only behavior that could not be verified safely
   without generating real input.

Be clear and concise
