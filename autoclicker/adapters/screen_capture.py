from __future__ import annotations

import cv2
import mss
import numpy as np


class ScreenCaptureAdapter:
    """Capture screen frames and perform the exact BGR match used by CV mode."""

    def __init__(self):
        self._capture = None

    def __enter__(self) -> ScreenCaptureAdapter:
        self._capture = mss.mss()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._capture is not None:
            self._capture.close()
            self._capture = None

    def has_exact_color(
        self,
        monitor_region: dict[str, int],
        target_bgr: tuple[int, int, int],
    ) -> bool:
        if self._capture is None:
            raise RuntimeError("Screen capture adapter must be used as a context manager.")

        screenshot = np.array(self._capture.grab(monitor_region))
        frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
        target = np.array(target_bgr)
        mask = cv2.inRange(frame, target, target)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return bool(contours)
