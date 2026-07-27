from __future__ import annotations

from collections.abc import Callable

import wx
import wx.dataview

from autoclicker.automation.points import Point


class PointsPanel(wx.Panel):
    def __init__(self, parent: wx.Window, translate: Callable[[str], str]):
        super().__init__(parent)
        self._ = translate
        self._refreshing = False
        self._on_edit: Callable[[int, Point], None] | None = None
        self._on_remove: Callable[[int], None] | None = None
        self._on_clear: Callable[[], None] | None = None
        self._on_move: Callable[[int, int], None] | None = None

        outer = wx.BoxSizer(wx.VERTICAL)
        heading = wx.StaticText(self, label=self._("Points"))
        heading.SetFont(heading.GetFont().Bold())
        outer.Add(heading, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 8)

        self.table = wx.dataview.DataViewListCtrl(
            self,
            style=wx.dataview.DV_ROW_LINES | wx.dataview.DV_VERT_RULES,
        )
        self.table.AppendTextColumn("#", width=45)
        editable = wx.dataview.DATAVIEW_CELL_EDITABLE
        self.table.AppendTextColumn(self._("X"), width=75, mode=editable)
        self.table.AppendTextColumn(self._("Y"), width=75, mode=editable)
        self.table.AppendTextColumn(self._("Before (ms)"), width=105, mode=editable)
        self.table.AppendTextColumn(self._("After (ms)"), width=105, mode=editable)
        self.table.Bind(wx.dataview.EVT_DATAVIEW_ITEM_VALUE_CHANGED, self._handle_edit)
        outer.Add(self.table, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.up_button = wx.Button(self, label=self._("Up"))
        self.down_button = wx.Button(self, label=self._("Down"))
        self.remove_button = wx.Button(self, label=self._("Remove"))
        self.clear_button = wx.Button(self, label=self._("Clear"))
        for button in (self.up_button, self.down_button, self.remove_button, self.clear_button):
            buttons.Add(button, 0, wx.RIGHT, 6)
        outer.Add(buttons, 0, wx.ALL, 8)

        self.up_button.Bind(wx.EVT_BUTTON, lambda event: self._move_selected(-1))
        self.down_button.Bind(wx.EVT_BUTTON, lambda event: self._move_selected(1))
        self.remove_button.Bind(wx.EVT_BUTTON, self._remove_selected)
        self.clear_button.Bind(wx.EVT_BUTTON, self._clear)
        self.SetSizer(outer)
        self.SetMinSize((430, 480))

    def bind_actions(
        self,
        on_edit: Callable[[int, Point], None],
        on_remove: Callable[[int], None],
        on_clear: Callable[[], None],
        on_move: Callable[[int, int], None],
    ) -> None:
        self._on_edit = on_edit
        self._on_remove = on_remove
        self._on_clear = on_clear
        self._on_move = on_move

    def set_points(self, points: tuple[Point, ...]) -> None:
        self._refreshing = True
        try:
            self.table.DeleteAllItems()
            for index, point in enumerate(points, start=1):
                self.table.AppendItem(
                    [
                        str(index),
                        str(point.x),
                        str(point.y),
                        str(point.delay_before_ms),
                        str(point.delay_after_ms),
                    ]
                )
        finally:
            self._refreshing = False

    def select_row(self, row: int) -> None:
        if 0 <= row < self.table.GetItemCount():
            self.table.SelectRow(row)

    def _selected_row(self) -> int:
        return self.table.GetSelectedRow()

    def _handle_edit(self, event: wx.dataview.DataViewEvent) -> None:
        if self._refreshing or self._on_edit is None:
            return
        row = self.table.ItemToRow(event.GetItem())
        try:
            values = [int(self.table.GetValue(row, column)) for column in range(1, 5)]
            point = Point(*values)
        except (TypeError, ValueError):
            point = None
        if point is None:
            self._on_edit(row, Point(0, 0, 0, 0))
            return
        self._on_edit(row, point)

    def _remove_selected(self, event: wx.CommandEvent) -> None:
        row = self._selected_row()
        if row >= 0 and self._on_remove is not None:
            self._on_remove(row)

    def _clear(self, event: wx.CommandEvent) -> None:
        if self._on_clear is not None:
            self._on_clear()

    def _move_selected(self, offset: int) -> None:
        row = self._selected_row()
        if row >= 0 and self._on_move is not None:
            self._on_move(row, offset)
