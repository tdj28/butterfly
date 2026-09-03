"""Deterministic selection of parameter-grid candidates and neighbors."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any


@dataclass(frozen=True, slots=True)
class CandidateSelection:
    core_indices: tuple[int, ...]
    selected_indices: tuple[int, ...]
    parent_core_indices: dict[int, tuple[int, ...]]


def select_low_score_with_neighbors(
    result: dict[str, Any], *, fraction: float, neighbor_radius: int
) -> CandidateSelection:
    """Select the lowest finite score fraction and its square-grid neighbors."""

    if not 0.0 < fraction <= 1.0:
        raise ValueError("selection fraction must be in (0, 1]")
    if neighbor_radius < 0:
        raise ValueError("neighbor radius must be nonnegative")
    shape = result.get("shape")
    rows = result.get("rows")
    if (
        not isinstance(shape, list)
        or len(shape) != 2
        or not all(isinstance(value, int) and value > 0 for value in shape)
        or not isinstance(rows, list)
    ):
        raise ValueError("result must contain a positive two-dimensional shape and rows")
    total = shape[0] * shape[1]
    by_index = {row.get("point_index"): row for row in rows}
    if len(by_index) != total or set(by_index) != set(range(total)):
        raise ValueError("result rows must form an exact indexed grid")
    finite_rows = [
        row
        for row in rows
        if isinstance(row.get("candidate_normalized_error"), (int, float))
        and math.isfinite(float(row["candidate_normalized_error"]))
    ]
    if not finite_rows:
        raise ValueError("result contains no finite candidate scores")
    finite_rows.sort(
        key=lambda row: (float(row["candidate_normalized_error"]), row["point_index"])
    )
    core_count = max(1, math.ceil(fraction * len(finite_rows)))
    core_indices = tuple(row["point_index"] for row in finite_rows[:core_count])
    parents: dict[int, set[int]] = {}
    row_count, column_count = shape
    for core_index in core_indices:
        grid_row, grid_column = divmod(core_index, column_count)
        for row_offset in range(-neighbor_radius, neighbor_radius + 1):
            for column_offset in range(-neighbor_radius, neighbor_radius + 1):
                neighbor_row = grid_row + row_offset
                neighbor_column = grid_column + column_offset
                if 0 <= neighbor_row < row_count and 0 <= neighbor_column < column_count:
                    neighbor = neighbor_row * column_count + neighbor_column
                    parents.setdefault(neighbor, set()).add(core_index)
    return CandidateSelection(
        core_indices=core_indices,
        selected_indices=tuple(sorted(parents)),
        parent_core_indices={
            index: tuple(sorted(core_parents))
            for index, core_parents in sorted(parents.items())
        },
    )
