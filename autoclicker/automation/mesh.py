from __future__ import annotations

from autoclicker.automation.points import Point


def create_mesh(
    source: tuple[Point, ...],
    amount_width: int,
    amount_height: int,
    delay_before_ms: int,
    delay_after_ms: int,
) -> tuple[Point, ...]:
    if len(source) != 3:
        raise ValueError("mesh_requires_three_points")
    if amount_width <= 1 or amount_height <= 1:
        raise ValueError("mesh_dimensions")

    origin, horizontal, vertical = source
    delta_x = (horizontal.x - origin.x) / (amount_width - 1)
    delta_y = (vertical.y - origin.y) / (amount_height - 1)

    return tuple(
        Point(
            x=int(origin.x + x_index * delta_x),
            y=int(origin.y + y_index * delta_y),
            delay_before_ms=delay_before_ms,
            delay_after_ms=delay_after_ms,
        )
        for y_index in range(amount_height)
        for x_index in range(amount_width)
    )
