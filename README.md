# autoclicker

This autoclicker was developed for the single-coop game "Salt" for achievement "Master Navigator". However, it can be used for other purposes, and I hope that user of this autoclicker will use it for good :)

# How to use it

Run the tool with `autoclicker.exe`
Use hotkeys to control the tool. Hotkeys are defined in `conf/settings.ini`

# Hotkeys

* `add_point_hotkey` - add new point to click
* `remove_last_point_hotkey` - remove last added point
* `remove_all_points_hotkey` - remove all points
* `start_autoclicker_hotkey` - start autocliker continuously
* `stop_autoclicker_hotkey` - stop autoclicker
* `one_autoclick_run_hotkey` - it starts autoclicker but clicks all points only once. Can be interrupted with `stop_autoclicker_hotkey`
* `save_points_hotkey` - save current points to file `points.txt`
* `load_points_hotkey` - load points from `points.txt`. !NOTE: all currents points will be removed
* `create_mesh_hotkey` - create mesh of clicking points. It uses three user defined points. `amount_width` and `amount_height` defines how much points should be in the row and column respectively.
* `exit_hotkey` - exit from the tool
