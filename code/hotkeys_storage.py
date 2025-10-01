

ADD_POINT_HOTKEY = "add_point_hotkey"
REMOVE_LAST_POINT_HOTKEY = "remove_last_point_hotkey"
REMOVE_ALL_POINTS_HOTKEY = "remove_all_points_hotkey"
START_AUTOCLICKER_HOTKEY = "start_autoclicker_hotkey"
STOP_AUTOCLICKER_HOTKEY = "stop_autoclicker_hotkey"
ONE_AUTOCLICK_RUN_HOTKEY = "one_autoclick_run_hotkey"
SAVE_POINTS_HOTKEY = "save_points_hotkey"
LOAD_POINTS_HOTKEY = "load_points_hotkey"
CREATE_MESH_HOTKEY = "create_mesh_hotkey"
START_STOP_CV_HOTKEY = "start_stop_cv_hotkey"
EXIT_HOTKEY = "exit_hotkey"

HOTKEY_TAGS = (ADD_POINT_HOTKEY, REMOVE_LAST_POINT_HOTKEY, REMOVE_ALL_POINTS_HOTKEY, START_AUTOCLICKER_HOTKEY,
               STOP_AUTOCLICKER_HOTKEY, ONE_AUTOCLICK_RUN_HOTKEY, SAVE_POINTS_HOTKEY, LOAD_POINTS_HOTKEY, CREATE_MESH_HOTKEY,
               START_STOP_CV_HOTKEY, EXIT_HOTKEY)  # EXIT_HOTKEY must be last

_hotkeys = {}


def init():
    for shotcut_tag in HOTKEY_TAGS:
        _hotkeys[shotcut_tag] = ""


def get_all_available_hotkeys():
    return _hotkeys


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


def is_storage_valid():
    valid = True
    for hotkey_tag in HOTKEY_TAGS:
        if (_hotkeys[hotkey_tag] == ""):
            valid = False
            break
    return valid


init()
