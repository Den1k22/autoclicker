

ADD_POINT = "add_point_shortcut"
REMOVE_LAST_POINT = "remove_last_point_shortcut"
REMOVE_ALL_POINTS = "remove_all_points_shortcut"
START_AUTOCLICKER = "start_autoclicker_shortcut"
STOP_AUTOCLICKER = "stop_autoclicker_shortcut"
ONE_AUTOCLICK_RUN = "one_autoclick_run_shortcut"
SAVE_POINTS = "save_points_shortcut"
LOAD_POINTS = "load_points_shortcut"
EXIT = "exit_shortcut"


_hotkeys = {
    ADD_POINT: "ctrl+alt+space",
    REMOVE_LAST_POINT: "ctrl+alt+z",
    REMOVE_ALL_POINTS: "ctrl+alt+c",
    START_AUTOCLICKER: "ctrl+alt+[",
    STOP_AUTOCLICKER: "ctrl+alt+]",
    ONE_AUTOCLICK_RUN: "ctrl+alt+'",
    SAVE_POINTS: "ctrl+alt+s",
    LOAD_POINTS: "ctrl+alt+l",
    EXIT: "ctrl+alt+q"
    }

def get_all_available_pairs():
    present_keys = {}

    for key, value in _hotkeys.items():
        if (get_hotkey_by_tag(key)):
            present_keys[key] = value

    return present_keys


def get_hotkey_by_tag(tag):
    if tag in _hotkeys:
        return _hotkeys[tag]
    else:
        return None


def set_hotkey_by_tag(tag, hotkey):
    if tag in _hotkeys:
        _hotkeys[tag] = hotkey
        return True
    else:
        return False