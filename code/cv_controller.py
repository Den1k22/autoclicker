
from thread_controller import ThreadController
import time
import cv2
import numpy as np
import mss

import action_controller
import settings
import util

top = int(settings.get("CV", "monitor_region_top"))
left = int(settings.get("CV", "monitor_region_left"))
width = int(settings.get("CV", "monitor_region_width"))
height = int(settings.get("CV", "monitor_region_height"))

monitor_region = {"top": top, "left": left, "width": width, "height": height}

target_rgb_r = int(settings.get("CV", "target_rgb_r"))
target_rgb_g = int(settings.get("CV", "target_rgb_g"))
target_rgb_b = int(settings.get("CV", "target_rgb_b"))

delay_bettween_frames = util.int_ms_to_float_seconds(int(settings.get("CV", "delay_between_frames")))
click_cooldown = util.int_ms_to_float_seconds(int(settings.get("CV", "click_cooldown")))
second_click_delay = util.int_ms_to_float_seconds(int(settings.get("CV", "second_click_delay")))
first_action = settings.get("CV", "first_action")
second_action = settings.get("CV", "second_action")

target_bgr = (target_rgb_b, target_rgb_g, target_rgb_r)  # BGR for OpenCV


def cv_runner(thread_controller: ThreadController):
    last_click = 0.0
    awaiting_second_click = False
    second_click_time = 0.0

    with mss.mss() as sct:
        while thread_controller.is_working():
            # Capture screen
            screenshot = np.array(sct.grab(monitor_region))
            frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

            # Create a mask where pixels exactly match the target color
            mask = cv2.inRange(frame, np.array(target_bgr), np.array(target_bgr))

            # Find contours if needed
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            now = time.time()

            if contours:
                if now - last_click >= click_cooldown:
                    action_controller.execute_action(first_action)
                    last_click = now
                    awaiting_second_click = True
                    second_click_time = now + second_click_delay

            if awaiting_second_click and now >= second_click_time:
                # current `contours` corresponds to the most recent frame
                action_controller.execute_action(second_action)
                awaiting_second_click = False

            time.sleep(delay_bettween_frames)
