from __future__ import annotations

import os
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Point:
    x: int
    y: int
    delay_before_ms: int = 50
    delay_after_ms: int = 50

    def __post_init__(self) -> None:
        if self.delay_before_ms < 0 or self.delay_after_ms < 0:
            raise ValueError("Point delays cannot be negative.")


class PointFileError(ValueError):
    pass


class PointStore:
    def __init__(self):
        self._points: list[Point] = []
        self._lock = threading.RLock()

    def snapshot(self) -> tuple[Point, ...]:
        with self._lock:
            return tuple(self._points)

    def replace(self, points: tuple[Point, ...] | list[Point]) -> None:
        with self._lock:
            self._points = list(points)

    def add(self, point: Point) -> None:
        with self._lock:
            self._points.append(point)

    def update(self, index: int, point: Point) -> None:
        with self._lock:
            self._points[index] = point

    def remove(self, index: int) -> None:
        with self._lock:
            del self._points[index]

    def remove_last(self) -> bool:
        with self._lock:
            if not self._points:
                return False
            self._points.pop()
            return True

    def clear(self) -> bool:
        with self._lock:
            if not self._points:
                return False
            self._points.clear()
            return True

    def move(self, index: int, offset: int) -> int:
        with self._lock:
            target = index + offset
            if not 0 <= index < len(self._points) or not 0 <= target < len(self._points):
                return index
            self._points[index], self._points[target] = self._points[target], self._points[index]
            return target


def load_points_file(path: Path) -> tuple[Point, ...]:
    if not path.is_file():
        raise PointFileError(f"Points file does not exist: {path}")

    parsed: list[Point] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise PointFileError(f"Could not read points file: {error}") from error

    for line_number, line in enumerate(lines, start=1):
        cleaned = line.replace(" ", "")
        if not cleaned or cleaned.startswith("#"):
            continue
        values = cleaned.split(",")
        if len(values) != 4:
            raise PointFileError(f"Line {line_number} must contain four comma-separated integers.")
        try:
            x, y, delay_before, delay_after = (int(value) for value in values)
            parsed.append(Point(x, y, delay_before, delay_after))
        except ValueError as error:
            raise PointFileError(f"Line {line_number} contains an invalid integer or delay.") from error

    return tuple(parsed)


def save_points_file(path: Path, points: tuple[Point, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            delete=False,
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
        ) as temporary:
            for point in points:
                temporary.write(
                    f"{point.x},{point.y},{point.delay_before_ms},{point.delay_after_ms}\n"
                )
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, path)
    except OSError:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise
