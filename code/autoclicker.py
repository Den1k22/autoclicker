
import threading
import keyboard
import os
import time

from thread_controller import ThreadController
import hotkeys_storage
import points_controller
import mouse_controller
import cv_controller
import settings
import util


def on_add_point():
    pos = mouse_controller.get_mouse_position()
    points_controller.add_point(points_controller.create_point(pos[0], pos[1]))


def on_remove_last_point():
    points_controller.remove_last_point()


def remove_all_points():
    points_controller.remove_all_points()


def click_all_points(thread_controller: ThreadController, clicking_points):
    for point in clicking_points:
        if not thread_controller.is_working():
            break

        mouse_controller.set_mouse_position(point.get_x, point.get_y)
        time.sleep(point.get_delay_before)
        mouse_controller.click_left_button()
        time.sleep(point.get_delay_after)


def start_autoclicker(thread_controller: ThreadController, clicking_points):
    while True:
        if not thread_controller.is_working():
            break

        click_all_points(thread_controller, clicking_points)


def on_one_autoclick_run(thread_controller: ThreadController):
    print("on_one_autoclick_run")

    for th in threading.enumerate():
        if th.name == "auto_clicker_job":
            return

    thread_controller.change_state(True)
    seq_thread = threading.Thread(
        target=click_all_points,
        daemon=True,
        args=[thread_controller, points_controller.get_points()],
        name="auto_clicker_job")
    seq_thread.start()


def on_start_autoclicker(thread_controller: ThreadController):
    print("on_start_autoclicker")

    for th in threading.enumerate():
        if th.name == "auto_clicker_job":
            return

    thread_controller.change_state(True)
    seq_thread = threading.Thread(
        target=start_autoclicker,
        daemon=True,
        args=[thread_controller, points_controller.get_points()],
        name="auto_clicker_job")
    seq_thread.start()


def on_stop_autoclicker(thread_controller: ThreadController):
    print("on_stop_autoclicker")
    thread_controller.change_state(False)


def on_save_points(file_name="points.txt"):
    f = open(file_name, "w")

    for point in points_controller.get_points():
        string_to_save = (str(point.get_x) + ","
                          + str(point.get_y) + ","
                          + str(util.float_seconds_to_int_ms(point.get_delay_before)) + ","
                          + str(util.float_seconds_to_int_ms(point.get_delay_after)) + "\n")
        f.write(string_to_save)

    f.close()


def load_points(file_name="points.txt"):
    if not os.path.isfile(file_name):
        return False

    f = open(file_name, "r")

    text = f.readlines()
    f.close()

    new_points = []
    ok_status = True

    for line in text:
        line = line.replace("\n", "")
        line = line.replace(" ", "")
        if (line == "" or line.startswith("#")):
            continue

        raw_points = line.split(",")
        if (len(raw_points) != 4):
            ok_status = False
            break

        if (util.are_all_strings_are_convertable_to_int(raw_points)):
            # TODO check that coordinates are in monitor's dimensions
            new_points.append(points_controller.create_point(
                int(raw_points[0]),
                int(raw_points[1]),
                util.int_ms_to_float_seconds(int(raw_points[2])),
                util.int_ms_to_float_seconds(int(raw_points[3])))
            )
        else:
            ok_status = False
            break

    if (len(new_points) > 0 and ok_status):
        points_controller.remove_all_points()

        for new_point in new_points:
            points_controller.add_point(new_point)

        return True
    else:
        return False


def on_load_points():
    if load_points():
        print("Points loaded successfully")
    else:
        print("Points were not loaded")


def on_create_mesh():
    points = points_controller.get_points()
    if len(points) != 3:
        print("You need three points to use mesh")
        return

    first_coordinate = points[0]
    second_coordinate = points[1]
    third_coordinate = points[2]
    height_amount = int(settings.get("MESH", "amount_height"))
    width_amount = int(settings.get("MESH", "amount_width"))

    delta_x = (second_coordinate._x - first_coordinate._x) / (width_amount-1)
    delta_y = (third_coordinate._y - first_coordinate._y) / (height_amount-1)
    init_x = first_coordinate._x
    init_y = first_coordinate._y

    points_controller.remove_all_points()

    for y in range(height_amount):
        for x in range(width_amount):
            point = points_controller.create_point(
                int(init_x + x*delta_x),
                int(init_y + y*delta_y),
                util.int_ms_to_float_seconds(int(settings.get("DELAYS", "delay_before"))),
                util.int_ms_to_float_seconds(int(settings.get("DELAYS", "delay_after")))
            )
            points_controller.add_point(point)


def on_start_stop_cv(thread_controller: ThreadController):
    if thread_controller.is_working():
        print("cv stop")
        thread_controller.change_state(False)
    else:
        print("cv start")
        thread_controller.change_state(True)
        seq_thread = threading.Thread(
            target=cv_controller.cv_runner,
            daemon=True,
            args=[thread_controller],
            name="cv_clicker_job")
        seq_thread.start()


def is_settings_valid():
    if (settings.getErrorStatus() != settings.ERROR_OK):
        print("Error status:", settings.getErrorStatus())
        return False
    try:
        int(settings.get("DELAYS", "delay_before"))
        int(settings.get("DELAYS", "delay_after"))
        int(settings.get("MESH", "amount_width"))
        int(settings.get("MESH", "amount_height"))
    except Exception as e:
        print(e)
        return False
    return True


def load_hotkeys_from_settings():
    for tag, hotkey in settings.get_hotkeys().items():
        hotkeys_storage.set_hotkey_by_tag(tag, hotkey)

    return hotkeys_storage.is_storage_valid()


def set_hotkeys(thread_controller):
    for tag, hotkey in hotkeys_storage.get_all_available_hotkeys().items():

        if (tag == hotkeys_storage.ADD_POINT_HOTKEY):
            print("ADD_POINT set:", hotkey)
            keyboard.add_hotkey(hotkey, on_add_point, args=())

        if (tag == hotkeys_storage.REMOVE_LAST_POINT_HOTKEY):
            print("REMOVE_LAST_POINT set:", hotkey)
            keyboard.add_hotkey(hotkey, on_remove_last_point, args=())

        if (tag == hotkeys_storage.REMOVE_ALL_POINTS_HOTKEY):
            print("REMOVE_ALL_POINTS set:", hotkey)
            keyboard.add_hotkey(hotkey, remove_all_points, args=())

        if (tag == hotkeys_storage.START_AUTOCLICKER_HOTKEY):
            print("START_AUTOCLICKER set:", hotkey)
            keyboard.add_hotkey(hotkey, on_start_autoclicker, args=(thread_controller,))

        if (tag == hotkeys_storage.STOP_AUTOCLICKER_HOTKEY):
            print("STOP_AUTOCLICKER set:", hotkey)
            keyboard.add_hotkey(hotkey, on_stop_autoclicker, args=(thread_controller,))

        if (tag == hotkeys_storage.ONE_AUTOCLICK_RUN_HOTKEY):
            print("ONE_AUTOCLICK_RUN set:", hotkey)
            keyboard.add_hotkey(hotkey, on_one_autoclick_run, args=(thread_controller,))

        if (tag == hotkeys_storage.SAVE_POINTS_HOTKEY):
            print("SAVE_POINTS set:", hotkey)
            keyboard.add_hotkey(hotkey, on_save_points, args=())

        if (tag == hotkeys_storage.LOAD_POINTS_HOTKEY):
            print("LOAD_POINTS set:", hotkey)
            keyboard.add_hotkey(hotkey, on_load_points, args=())

        if (tag == hotkeys_storage.CREATE_MESH_HOTKEY):
            print("CREATE_MESH_HOTKEY set:", hotkey)
            keyboard.add_hotkey(hotkey, on_create_mesh, args=())

        if (tag == hotkeys_storage.START_STOP_CV_HOTKEY):
            print("START_STOP_CV_HOTKEY set:", hotkey)
            keyboard.add_hotkey(hotkey, on_start_stop_cv, args=(thread_controller,))

        if (tag == hotkeys_storage.EXIT_HOTKEY):
            print("EXIT set:", hotkey)
            keyboard.wait(hotkey)


def main():
    print("Welcome to autoclicker v0.3")
    thread_controller = ThreadController()

    if not is_settings_valid():
        print("ERROR: settigns are not valid or not present")
        input("Press enter to exit")
        return

    if not load_hotkeys_from_settings():
        print("ERROR: load_hotkeys_from_settings failed")
        return

    set_hotkeys(thread_controller)


main()
