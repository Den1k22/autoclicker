
import time
import cv2
import numpy as np
import mss

import mouse_controller

monitor_region = {"top": 480, "left": 470, "width": 670, "height": 80} # for 2k

# exact color 185, 238, 64
target_rgb = (188, 255, 71)
target_bgr = (target_rgb[2], target_rgb[1], target_rgb[0])  # BGR for OpenCV

from thread_controller import ThreadController

def cv_runner(thread_controller: ThreadController):
    with mss.mss() as sct:
        while thread_controller.is_working():
            # Capture screen
            screenshot = np.array(sct.grab(monitor_region))
            frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

            # Create a mask where pixels exactly match the target color
            mask = cv2.inRange(frame, np.array(target_bgr), np.array(target_bgr))

            # Find contours if needed
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                mouse_controller.click_left_button()
                time.sleep(0.2)
                mouse_controller.click_left_button()

            time.sleep(0.1)
