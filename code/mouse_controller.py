

from pynput import mouse

ONE_CLICK = 1

SUPPORTED_BUTTONS = {
    "left_button": mouse.Button.left,
    "right_button": mouse.Button.right,
    "middle_button": mouse.Button.middle,
    "x1_button": mouse.Button.x1,
    "x2_button": mouse.Button.x2
}


def get_mouse_position():
    return mouse_controller.position


def set_mouse_position(x, y):
    mouse_controller.position = (x, y)


def is_valid_button(button):
    return isinstance(button, str) and button.strip().lower() in SUPPORTED_BUTTONS


def click_button(button, times=ONE_CLICK):
    if not is_valid_button(button):
        raise ValueError("Unsupported mouse button: " + str(button))

    button_name = button.strip().lower()
    mouse_controller.click(SUPPORTED_BUTTONS[button_name], times)


def click_left_button(times=ONE_CLICK):
    click_button("left_button", times)


def click_right_button(times=ONE_CLICK):
    click_button("right_button", times)


def click_middle_button(times=ONE_CLICK):
    click_button("middle_button", times)


def click_x1_button(times=ONE_CLICK):
    click_button("x1_button", times)


def click_x2_button(times=ONE_CLICK):
    click_button("x2_button", times)


mouse_controller = mouse.Controller()
