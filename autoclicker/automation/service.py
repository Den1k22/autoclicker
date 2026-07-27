from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from enum import Enum
from pathlib import Path

from autoclicker.automation.cv import run_cv
from autoclicker.automation.mesh import create_mesh
from autoclicker.automation.points import (
    Point,
    PointStore,
    load_points_file,
    save_points_file,
)
from autoclicker.helpers.time import milliseconds_to_seconds
from autoclicker.settings.model import AppSettings


LOGGER = logging.getLogger(__name__)


class RunMode(Enum):
    IDLE = "idle"
    POINTS_ONCE = "points_once"
    POINTS_CONTINUOUS = "points_continuous"
    CV = "cv"


class AutomationError(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class AutomationService:
    def __init__(
        self,
        settings: AppSettings,
        mouse,
        action_dispatcher,
        capture_factory,
        default_points_path: Path,
    ):
        self._settings = settings
        self._mouse = mouse
        self._action_dispatcher = action_dispatcher
        self._capture_factory = capture_factory
        self._points = PointStore()
        self._document_path = Path(default_points_path)
        self._dirty = False

        self._mode = RunMode.IDLE
        self._stop_event = threading.Event()
        self._worker: threading.Thread | None = None
        self._lock = threading.RLock()
        self._point_listeners: list[Callable[[tuple[Point, ...], bool, Path], None]] = []
        self._mode_listeners: list[Callable[[RunMode], None]] = []
        self._error_listeners: list[Callable[[Exception], None]] = []

    @property
    def settings(self) -> AppSettings:
        with self._lock:
            return self._settings

    @property
    def mode(self) -> RunMode:
        with self._lock:
            return self._mode

    @property
    def dirty(self) -> bool:
        with self._lock:
            return self._dirty

    @property
    def document_path(self) -> Path:
        with self._lock:
            return self._document_path

    def points(self) -> tuple[Point, ...]:
        return self._points.snapshot()

    def add_points_listener(self, listener: Callable[[tuple[Point, ...], bool, Path], None]) -> None:
        self._point_listeners.append(listener)

    def add_mode_listener(self, listener: Callable[[RunMode], None]) -> None:
        self._mode_listeners.append(listener)

    def add_error_listener(self, listener: Callable[[Exception], None]) -> None:
        self._error_listeners.append(listener)

    def publish_initial_state(self) -> None:
        self._notify_points()
        self._notify_mode()

    def update_settings(self, settings: AppSettings) -> None:
        with self._lock:
            self._settings = settings

    def record_current_point(self) -> Point:
        x, y = self._mouse.get_position()
        settings = self.settings
        point = Point(
            x,
            y,
            settings.delays.delay_before_ms,
            settings.delays.delay_after_ms,
        )
        self._points.add(point)
        self._mark_dirty()
        return point

    def update_point(self, index: int, point: Point) -> None:
        self._points.update(index, point)
        self._mark_dirty()

    def remove_point(self, index: int) -> None:
        self._points.remove(index)
        self._mark_dirty()

    def remove_last_point(self) -> bool:
        changed = self._points.remove_last()
        if changed:
            self._mark_dirty()
        return changed

    def clear_points(self) -> bool:
        changed = self._points.clear()
        if changed:
            self._mark_dirty()
        return changed

    def move_point(self, index: int, offset: int) -> int:
        target = self._points.move(index, offset)
        if target != index:
            self._mark_dirty()
        return target

    def create_mesh(self) -> None:
        settings = self.settings
        points = create_mesh(
            self.points(),
            settings.mesh.amount_width,
            settings.mesh.amount_height,
            settings.delays.delay_before_ms,
            settings.delays.delay_after_ms,
        )
        self._points.replace(points)
        self._mark_dirty()

    def load_points(self, path: Path | None = None) -> tuple[Point, ...]:
        target = Path(path) if path is not None else self.document_path
        points = load_points_file(target)
        self._points.replace(points)
        with self._lock:
            self._document_path = target
            self._dirty = False
        self._notify_points()
        return points

    def save_points(self, path: Path | None = None) -> Path:
        target = Path(path) if path is not None else self.document_path
        points = self.points()
        save_points_file(target, points)
        self.replace_points_document(points, target)
        return target

    def replace_points_document(self, points: tuple[Point, ...], path: Path) -> None:
        self._points.replace(points)
        with self._lock:
            self._document_path = Path(path)
            self._dirty = False
        self._notify_points()

    def start_points_once(self) -> bool:
        points = self.points()
        if not points:
            raise AutomationError("no_points")
        return self._start_worker(
            RunMode.POINTS_ONCE,
            "auto_clicker_job",
            lambda stop_event: self._run_points(stop_event, points, continuous=False),
        )

    def start_points_continuous(self) -> bool:
        points = self.points()
        if not points:
            raise AutomationError("no_points")
        return self._start_worker(
            RunMode.POINTS_CONTINUOUS,
            "auto_clicker_job",
            lambda stop_event: self._run_points(stop_event, points, continuous=True),
        )

    def start_cv(self) -> bool:
        settings = self.settings.cv
        return self._start_worker(
            RunMode.CV,
            "cv_clicker_job",
            lambda stop_event: run_cv(
                stop_event,
                settings,
                self._capture_factory,
                self._action_dispatcher.execute,
            ),
        )

    def toggle_cv(self) -> bool:
        if self.mode == RunMode.CV:
            self.stop()
            return False
        return self.start_cv()

    def stop(self) -> bool:
        with self._lock:
            if self._mode == RunMode.IDLE:
                return False
            self._stop_event.set()
            return True

    def stop_and_wait(self, timeout: float = 2.0) -> bool:
        self.stop()
        with self._lock:
            worker = self._worker
        if worker is not None and worker is not threading.current_thread():
            worker.join(timeout)
        return self.mode == RunMode.IDLE

    def shutdown(self, timeout: float = 2.0) -> None:
        self.stop()
        with self._lock:
            worker = self._worker
        if worker is not None and worker is not threading.current_thread():
            worker.join(timeout)

    def _start_worker(
        self,
        mode: RunMode,
        name: str,
        target: Callable[[threading.Event], None],
    ) -> bool:
        with self._lock:
            if self._mode != RunMode.IDLE or (self._worker is not None and self._worker.is_alive()):
                return False
            stop_event = threading.Event()
            self._stop_event = stop_event
            self._mode = mode

            def guarded_target() -> None:
                try:
                    target(stop_event)
                except Exception as error:
                    LOGGER.exception("Automation worker failed")
                    self._notify_error(error)
                finally:
                    self._finish_worker(threading.current_thread())

            worker = threading.Thread(target=guarded_target, daemon=True, name=name)
            self._worker = worker

        self._notify_mode()
        worker.start()
        return True

    def _finish_worker(self, worker: threading.Thread) -> None:
        with self._lock:
            if self._worker is not worker:
                return
            self._worker = None
            self._mode = RunMode.IDLE
        self._notify_mode()

    def _run_points(
        self,
        stop_event: threading.Event,
        points: tuple[Point, ...],
        continuous: bool,
    ) -> None:
        while not stop_event.is_set():
            for point in points:
                if stop_event.is_set():
                    return
                self._mouse.set_position(point.x, point.y)
                if stop_event.wait(milliseconds_to_seconds(point.delay_before_ms)):
                    return
                self._mouse.click_left()
                if stop_event.wait(milliseconds_to_seconds(point.delay_after_ms)):
                    return
            if not continuous:
                return

    def _mark_dirty(self) -> None:
        with self._lock:
            self._dirty = True
        self._notify_points()

    def _notify_points(self) -> None:
        snapshot = self.points()
        with self._lock:
            dirty = self._dirty
            path = self._document_path
        for listener in tuple(self._point_listeners):
            listener(snapshot, dirty, path)

    def _notify_mode(self) -> None:
        mode = self.mode
        for listener in tuple(self._mode_listeners):
            listener(mode)

    def _notify_error(self, error: Exception) -> None:
        for listener in tuple(self._error_listeners):
            listener(error)
