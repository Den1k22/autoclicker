from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from autoclicker.automation.mesh import create_mesh
from autoclicker.automation.points import (
    Point,
    PointFileError,
    PointStore,
    load_points_file,
    save_points_file,
)


class PointStoreTests(unittest.TestCase):
    def test_snapshot_is_immutable_and_later_edits_do_not_change_it(self):
        store = PointStore()
        first = Point(10, 20)
        store.add(first)
        snapshot = store.snapshot()

        store.update(0, Point(30, 40))

        self.assertEqual(snapshot, (first,))
        self.assertEqual(store.snapshot(), (Point(30, 40),))

    def test_move_remove_and_clear_handle_boundaries(self):
        store = PointStore()
        store.replace([Point(1, 1), Point(2, 2)])

        self.assertEqual(store.move(0, -1), 0)
        self.assertEqual(store.move(0, 1), 1)
        self.assertEqual(store.snapshot()[0], Point(2, 2))
        self.assertTrue(store.remove_last())
        self.assertTrue(store.clear())
        self.assertFalse(store.clear())


class PointFileTests(unittest.TestCase):
    def test_round_trip_supports_negative_multi_monitor_coordinates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "points.txt"
            expected = (Point(-50, 25, 10, 20), Point(100, -30, 0, 5))

            save_points_file(path, expected)

            self.assertEqual(load_points_file(path), expected)

    def test_loading_is_all_or_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "points.txt"
            path.write_text("1,2,3,4\ninvalid\n", encoding="utf-8")

            with self.assertRaises(PointFileError):
                load_points_file(path)

    def test_comments_and_blank_lines_are_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "points.txt"
            path.write_text("# comment\n\n 1, 2, 3, 4 \n", encoding="utf-8")

            self.assertEqual(load_points_file(path), (Point(1, 2, 3, 4),))

    def test_empty_and_comment_only_files_represent_an_empty_point_list(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "points.txt"

            path.write_text("", encoding="utf-8")
            self.assertEqual(load_points_file(path), ())

            path.write_text("# no recorded points yet\n\n", encoding="utf-8")
            self.assertEqual(load_points_file(path), ())


class MeshTests(unittest.TestCase):
    def test_mesh_uses_three_points_and_includes_both_endpoints(self):
        mesh = create_mesh(
            (Point(0, 0), Point(10, 0), Point(0, 20)),
            amount_width=3,
            amount_height=3,
            delay_before_ms=7,
            delay_after_ms=8,
        )

        self.assertEqual(len(mesh), 9)
        self.assertEqual(mesh[0], Point(0, 0, 7, 8))
        self.assertEqual(mesh[-1], Point(10, 20, 7, 8))

    def test_mesh_rejects_invalid_source_and_dimensions(self):
        with self.assertRaisesRegex(ValueError, "mesh_requires_three_points"):
            create_mesh((Point(0, 0),), 2, 2, 0, 0)
        with self.assertRaisesRegex(ValueError, "mesh_dimensions"):
            create_mesh((Point(0, 0), Point(1, 0), Point(0, 1)), 1, 2, 0, 0)
