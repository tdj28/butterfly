"""Deterministic extraction of periodic-window components from scan grids."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import math
from typing import Any


@dataclass(frozen=True, slots=True)
class PeriodicComponent:
    """One grid-connected set of points carrying the same detected period."""

    period: int
    point_indices: tuple[int, ...]
    a_min: float
    a_max: float
    c_min: float
    c_max: float
    a_centroid: float
    c_centroid: float
    touches_grid_boundary: bool


def _indexed_grid(result: dict[str, Any]) -> tuple[int, int, dict[int, dict[str, Any]]]:
    shape = result.get("shape")
    rows = result.get("rows")
    if (
        not isinstance(shape, list)
        or len(shape) != 2
        or not all(isinstance(value, int) and value > 0 for value in shape)
        or not isinstance(rows, list)
    ):
        raise ValueError("result must contain a positive two-dimensional shape and rows")
    row_count, column_count = shape
    total = row_count * column_count
    by_index = {row.get("point_index"): row for row in rows}
    if len(by_index) != total or set(by_index) != set(range(total)):
        raise ValueError("result rows must form an exact indexed grid")
    return row_count, column_count, by_index


def periodic_components(
    result: dict[str, Any], *, connectivity: int = 8
) -> tuple[PeriodicComponent, ...]:
    """Return same-period 4- or 8-connected components in deterministic order.

    Components are discovery objects, not proofs of shrimp connectivity. Their
    purpose is to turn a broad raster into candidates for local refinement and
    periodic-orbit continuation.
    """

    if connectivity not in (4, 8):
        raise ValueError("connectivity must be 4 or 8")
    row_count, column_count, by_index = _indexed_grid(result)
    periodic = {
        index: int(row["fundamental_period"])
        for index, row in by_index.items()
        if row.get("label") == "periodic"
        and isinstance(row.get("fundamental_period"), int)
        and row["fundamental_period"] > 0
    }
    offsets = [(-1, 0), (0, -1), (0, 1), (1, 0)]
    if connectivity == 8:
        offsets.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
    remaining = set(periodic)
    components: list[PeriodicComponent] = []
    while remaining:
        seed = min(remaining)
        period = periodic[seed]
        queue = deque([seed])
        remaining.remove(seed)
        indices: list[int] = []
        while queue:
            index = queue.popleft()
            indices.append(index)
            grid_row, grid_column = divmod(index, column_count)
            for row_offset, column_offset in offsets:
                neighbor_row = grid_row + row_offset
                neighbor_column = grid_column + column_offset
                if not (
                    0 <= neighbor_row < row_count
                    and 0 <= neighbor_column < column_count
                ):
                    continue
                neighbor = neighbor_row * column_count + neighbor_column
                if neighbor in remaining and periodic.get(neighbor) == period:
                    remaining.remove(neighbor)
                    queue.append(neighbor)
        ordered = tuple(sorted(indices))
        rows = [by_index[index] for index in ordered]
        a_values = [float(row["a"]) for row in rows]
        c_values = [float(row["c"]) for row in rows]
        touches_boundary = any(
            (index // column_count) in (0, row_count - 1)
            or (index % column_count) in (0, column_count - 1)
            for index in ordered
        )
        components.append(
            PeriodicComponent(
                period=period,
                point_indices=ordered,
                a_min=min(a_values),
                a_max=max(a_values),
                c_min=min(c_values),
                c_max=max(c_values),
                a_centroid=sum(a_values) / len(a_values),
                c_centroid=sum(c_values) / len(c_values),
                touches_grid_boundary=touches_boundary,
            )
        )
    return tuple(
        sorted(components, key=lambda item: (item.period, item.point_indices[0]))
    )


def ranked_recurrence_candidates(
    result: dict[str, Any], *, limit: int, exclude_periodic: bool = True
) -> tuple[dict[str, Any], ...]:
    """Rank finite near-recurrences for refinement with stable tie breaking."""

    if limit < 1:
        raise ValueError("limit must be positive")
    _, _, by_index = _indexed_grid(result)
    candidates = []
    for index, row in by_index.items():
        score = row.get("candidate_normalized_error")
        if exclude_periodic and row.get("label") == "periodic":
            continue
        if not isinstance(score, (int, float)) or not math.isfinite(float(score)):
            continue
        candidates.append(
            {
                "point_index": index,
                "a": float(row["a"]),
                "b": float(row["b"]),
                "c": float(row["c"]),
                "candidate_period": row.get("candidate_period"),
                "candidate_normalized_error": float(score),
                "label": row.get("label"),
            }
        )
    candidates.sort(
        key=lambda row: (row["candidate_normalized_error"], row["point_index"])
    )
    return tuple(candidates[:limit])
