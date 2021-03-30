
import threading
import keyboard
import os
import time

import hotkeys_storage
import points_controller
import mouse_controller
import util


class ThreadController:

    def __init__(self):
        self.work = True

    def is_working(self):
        return self.work

    def change_state(self, state):
        self.work = state


def on_add_point():
    pos = mouse_controller.get_mouse_position()
    points_controller.add_point(points_controller.create_point(pos[0], pos[1]))


def on_remove_last_point():
    points_controller.remove_last_point()


def remove_all_points():
    points_controller.remove_all_points()


def click_all_points(thread_controller, clicking_points):
    for point in clicking_points:
        if not thread_controller.is_working():
            break

        mouse_controller.set_mouse_position(point.get_x, point.get_y)
        time.sleep(point.get_delay_before)
        mouse_controller.click_left_button()
        time.sleep(point.get_delay_after)


def start_autoclicker(thread_controller, clicking_points):
    while True:
        if not thread_controller.is_working():
            break

        click_all_points(thread_controller, clicking_points)


def on_one_autoclick_run(thread_controller):
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


def on_start_autoclicker(thread_controller):
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


def on_stop_autoclicker(thread_controller):
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
        print ("Points loaded successfully")
    else:
        print ("Points were not loaded")


def load_custom_hotkeys(file_name="custom_keys.txt"):
    if not os.path.isfile(file_name):
        return

    f = open(file_name, "r")
    text = f.readlines()
    f.close()

    for line in text:
        clean_line = line.replace("\n", "")
        clean_line = clean_line.replace(" ", "")
        if (line == "" or line.startswith("#")):
            continue

        tag_and_hotkey = clean_line.split("=")

        if (tag_and_hotkey != 2):
            continue

        set_hotkey_by_tag(tag_and_hotkey[0], tag_and_hotkey[1])

    


def set_hotkeys(thread_controller):

    for tag, hotkey  in hotkeys_storage.get_all_available_pairs().items():

        if (tag == hotkeys_storage.ADD_POINT):
            print("ADD_POINT set:", hotkey)
            keyboard.add_hotkey(hotkey, on_add_point, args=[])

        if (tag == hotkeys_storage.REMOVE_LAST_POINT):
            print("REMOVE_LAST_POINT set:", hotkey)
            keyboard.add_hotkey(hotkey, on_remove_last_point, args=[])

        if (tag == hotkeys_storage.REMOVE_ALL_POINTS):
            print("REMOVE_ALL_POINTS set:", hotkey)
            keyboard.add_hotkey(hotkey, remove_all_points, args=[])

        if (tag == hotkeys_storage.START_AUTOCLICKER):
            print("START_AUTOCLICKER set:", hotkey)
            keyboard.add_hotkey(hotkey, on_start_autoclicker, args=[thread_controller])

        if (tag == hotkeys_storage.STOP_AUTOCLICKER):
            print("STOP_AUTOCLICKER set:", hotkey)
            keyboard.add_hotkey(hotkey, on_stop_autoclicker, args=[thread_controller])

        if (tag == hotkeys_storage.ONE_AUTOCLICK_RUN):
            print("ONE_AUTOCLICK_RUN set:", hotkey)
            keyboard.add_hotkey(hotkey, on_one_autoclick_run, args=[thread_controller])

        if (tag == hotkeys_storage.SAVE_POINTS):
            print("SAVE_POINTS set:", hotkey)
            keyboard.add_hotkey(hotkey, on_save_points, args=[])

        if (tag == hotkeys_storage.LOAD_POINTS):
            print("LOAD_POINTS set:", hotkey)
            keyboard.add_hotkey(hotkey, on_load_points, args=[])

        if (tag == hotkeys_storage.EXIT):
            print("EXIT set:", hotkey)
            keyboard.wait(hotkey)   


def main():
    print("Welcome to autoclicker v0.1")
    thread_controller = ThreadController()

    set_hotkeys(thread_controller)

main()