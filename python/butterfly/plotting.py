"""Publication-oriented parameter-plane raster construction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


SPECIAL_CODES = {
    "numerical_failure": -3,
    "escaping": -2,
    "unresolved": -1,
    "quasiperiodic": 0,
    "chaotic": 33,
    "multistable": 34,
}


@dataclass(frozen=True, slots=True)
class ParameterPlane:
    values: np.ndarray
    a_values: np.ndarray
    c_values: np.ndarray
    periods_present: tuple[int, ...]
    labels_present: tuple[str, ...]


def parameter_plane(result: dict[str, Any], *, max_period: int = 32) -> ParameterPlane:
    """Encode indexed scan rows as a `c by a` categorical image array."""

    shape = result.get("shape")
    rows = result.get("rows")
    if (
        not isinstance(shape, list)
        or len(shape) != 2
        or not all(isinstance(value, int) and value > 0 for value in shape)
        or not isinstance(rows, list)
    ):
        raise ValueError("result must contain a positive two-dimensional shape and rows")
    a_count, c_count = shape
    total = a_count * c_count
    by_index = {row.get("point_index"): row for row in rows}
    if len(by_index) != total or set(by_index) != set(range(total)):
        raise ValueError("result rows must form an exact indexed grid")

    values = np.full((c_count, a_count), SPECIAL_CODES["unresolved"], dtype=np.int16)
    periods: set[int] = set()
    labels: set[str] = set()
    a_axis = np.empty(a_count, dtype=np.float64)
    c_axis = np.empty(c_count, dtype=np.float64)
    for index, row in by_index.items():
        a_index, c_index = divmod(index, c_count)
        a_axis[a_index] = float(row["a"])
        c_axis[c_index] = float(row["c"])
        label = str(row.get("label", "unresolved"))
        labels.add(label)
        if label == "periodic":
            period = row.get("fundamental_period")
            if not isinstance(period, int) or not 1 <= period <= max_period:
                raise ValueError("periodic rows require a bounded integer period")
            values[c_index, a_index] = period
            periods.add(period)
        else:
            values[c_index, a_index] = SPECIAL_CODES.get(
                label, SPECIAL_CODES["unresolved"]
            )
    if not (np.all(np.diff(a_axis) >= 0.0) and np.all(np.diff(c_axis) >= 0.0)):
        raise ValueError("parameter axes must be monotone")
    return ParameterPlane(
        values=values,
        a_values=a_axis,
        c_values=c_axis,
        periods_present=tuple(sorted(periods)),
        labels_present=tuple(sorted(labels)),
    )


def pixel_edges(values: np.ndarray) -> tuple[float, float]:
    """Return half-cell padding for a regularly spaced coordinate axis."""

    if len(values) == 1:
        return float(values[0] - 0.5), float(values[0] + 0.5)
    differences = np.diff(values)
    if not np.allclose(differences, differences[0], rtol=1e-10, atol=1e-12):
        raise ValueError("raster axes must be regularly spaced")
    half_step = float(differences[0] / 2.0)
    return float(values[0] - half_step), float(values[-1] + half_step)
