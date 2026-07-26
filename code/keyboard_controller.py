import keyboard


def press_and_release(key):
    keyboard.press_and_release(key)


def add_hotkey(hotkey, callback, args=()):
    return keyboard.add_hotkey(hotkey, callback, args=args)


def wait_for_hotkey(hotkey):
    keyboard.wait(hotkey)


def is_valid_key(key):
    if not isinstance(key, str) or not key.strip():
        return False

    try:
        # A comma creates a multi-step sequence. CV actions support one key or
        # one simultaneous key combination only.
        return len(keyboard.parse_hotkey(key.strip())) == 1
    except (KeyError, ValueError):
        return False
