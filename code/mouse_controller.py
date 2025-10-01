

from pynput import mouse

ONE_CLICK = 1


def get_mouse_position():
    return mouse_controller.position


def set_mouse_position(x, y):
    mouse_controller.position = (x, y)


def click_left_button(times=ONE_CLICK):
    mouse_controller.click(mouse.Button.left, times)


mouse_controller = mouse.Controller()
