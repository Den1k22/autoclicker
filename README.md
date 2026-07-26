# Autoclicker
This autoclicker was developed for the single-coop game "Salt" for achievement "Master Navigator". However, it can be used for other purposes, and I hope that user of this autoclicker will use it for good :)

Autoclickers are type of tools which emulate mouse button clicks. This autoclicker emulates clicking on recorded points on the screen. It can go through recorded points once or continuously. It is possible to save current points and load them from file.

# How to use it
Run the tool with `autoclicker.exe`
Use hotkeys to control the tool. Hotkeys are defined in `config/settings.ini`

# Hotkeys
* `add_point_hotkey` - add to points to click current cursor location 
* `remove_last_point_hotkey` - remove last added point
* `remove_all_points_hotkey` - remove all points
* `start_autoclicker_hotkey` - start autocliker continuously
* `stop_autoclicker_hotkey` - stop autoclicker
* `one_autoclick_run_hotkey` - it starts autoclicker but clicks all points only once. Can be interrupted with `stop_autoclicker_hotkey`
* `save_points_hotkey` - save current points to file `points.txt`
* `load_points_hotkey` - load points from `points.txt`. !NOTE: all currents points will be removed
* `create_mesh_hotkey` - create mesh of clicking points. It uses three user defined points. `amount_width` and `amount_height` in `config/settings.ini` defines how much points should be in the row and column respectively.
* `exit_hotkey` - exit from the tool

# CV actions
The `[CV]` section in `config/settings.ini` defines two configurable input actions:

* `first_action` runs when the target-color contours are detected and the click cooldown has elapsed.
* `second_action` runs after `second_click_delay` has elapsed following the first action.

Use a keyboard key or combination directly. For a mouse click, use one of the mouse action names. For example:

```ini
first_action = space
second_action = left_button
```

Keyboard actions can contain one key or one simultaneous combination accepted by the installed `keyboard` library. Examples include characters (`a`, `1`, `/`), named keys (`space`, `enter`, `tab`, `esc`), editing and navigation keys (`backspace`, `delete`, `insert`, `home`, `end`, `page up`, `page down`, `up`, `down`, `left`, `right`), modifiers (`ctrl`, `shift`, `alt`, `windows`), function keys (`f1` through `f24`), and combinations such as `ctrl+shift+a`. Exact key-name availability can depend on the operating system and keyboard layout. Comma-separated key sequences are not supported.

Mouse actions support `left_button`, `right_button`, `middle_button`, `x1_button`, and `x2_button`. The `x1` and `x2` names refer to the extra side buttons commonly used for Back and Forward; they require compatible mouse hardware and operating-system support. Each mouse action performs one click.

# For Devs
Write this in settings for autopep8
```
"[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.autopep8"
},
"autopep8.args": ["--max-line-length", "120"]
```
