"""Deterministic unstable-periodic-orbit seed selection from section states."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike


@dataclass(frozen=True, slots=True)
class CloseReturnCandidate:
    """One lagged close return in a scaled Poincare-section state sequence."""

    lag: int
    start_index: int
    end_index: int
    normalized_distance: float


def project_floquet_direction_to_section(
    direction: ArrayLike,
    flow_direction: ArrayLike,
    section_normal: ArrayLike,
    *,
    coordinate_scales: ArrayLike,
) -> np.ndarray:
    """Remove flow phase and normalize a Floquet direction in a section.

    The correction subtracts a multiple of the flow direction so that the
    result is tangent to the declared Poincare plane. Normalization uses the
    same coordinate scales as downstream manifold-distance calculations.
    """

    vector = np.asarray(direction, dtype=np.float64)
    flow = np.asarray(flow_direction, dtype=np.float64)
    normal = np.asarray(section_normal, dtype=np.float64)
    scales = np.asarray(coordinate_scales, dtype=np.float64)
    if any(value.shape != (3,) for value in (vector, flow, normal, scales)):
        raise ValueError("direction, flow, normal, and scales must have shape (3,)")
    if any(
        np.any(~np.isfinite(value)) for value in (vector, flow, normal, scales)
    ):
        raise ValueError("section-direction inputs must be finite")
    if np.any(scales <= 0.0) or np.linalg.norm(normal) == 0.0:
        raise ValueError("coordinate scales and section normal must be nondegenerate")
    section_speed = float(np.dot(normal, flow))
    tangency_scale = (
        np.finfo(np.float64).eps * np.linalg.norm(normal) * np.linalg.norm(flow)
    )
    if abs(section_speed) <= tangency_scale:
        raise ValueError("flow is tangent to the section")
    projected = vector - flow * (float(np.dot(normal, vector)) / section_speed)
    scaled_norm = float(np.linalg.norm(projected / scales))
    if scaled_norm <= np.finfo(np.float64).eps:
        raise ValueError("projected Floquet direction is degenerate")
    return projected / scaled_norm


def select_close_return_candidates(
    states: ArrayLike,
    *,
    coordinate_scales: ArrayLike,
    minimum_lag: int,
    maximum_lag: int,
    candidates_per_lag: int = 1,
    exclusion_radius: int = 1,
) -> tuple[CloseReturnCandidate, ...]:
    """Rank separated close returns for each declared lag.

    Selection uses only scaled state distance.  It does not assert that the
    PIM pseudo-orbit segment is an exact flow segment; downstream recovery must
    independently integrate the return map before periodic shooting.
    """

    values = np.asarray(states, dtype=np.float64)
    scales = np.asarray(coordinate_scales, dtype=np.float64)
    if values.ndim != 2 or not len(values):
        raise ValueError("states must have nonempty shape (n,d)")
    if scales.shape != (values.shape[1],):
        raise ValueError("coordinate_scales must have shape (d,)")
    if np.any(~np.isfinite(values)) or np.any(~np.isfinite(scales)):
        raise ValueError("states and coordinate scales must be finite")
    if np.any(scales <= 0.0):
        raise ValueError("coordinate scales must be positive")
    if minimum_lag < 1 or maximum_lag < minimum_lag:
        raise ValueError("invalid lag interval")
    if maximum_lag >= len(values):
        raise ValueError("maximum_lag must be smaller than the state count")
    if candidates_per_lag < 1 or exclusion_radius < 0:
        raise ValueError("invalid selection controls")

    candidates = []
    for lag in range(minimum_lag, maximum_lag + 1):
        distances = np.linalg.norm(
            (values[lag:] - values[:-lag]) / scales,
            axis=1,
        )
        order = np.argsort(distances, kind="stable")
        selected = []
        for index in order:
            start = int(index)
            if any(abs(start - prior) <= exclusion_radius for prior in selected):
                continue
            selected.append(start)
            candidates.append(
                CloseReturnCandidate(
                    lag=lag,
                    start_index=start,
                    end_index=start + lag,
                    normalized_distance=float(distances[start]),
                )
            )
            if len(selected) == candidates_per_lag:
                break
    return tuple(
        sorted(
            candidates,
            key=lambda row: (
                row.normalized_distance,
                row.lag,
                row.start_index,
            ),
        )
    )
