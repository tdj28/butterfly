"""Reference sprinkler sampling for nonattracting chaotic invariant sets."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .models import RosslerParameters
from .poincare import PoincareSection


@dataclass(frozen=True, slots=True)
class SprinklerResult:
    """Long-lived ensemble and middle-time crossings from a sprinkler run."""

    capture_times: NDArray[np.float64]
    failed: NDArray[np.bool_]
    survivor_ids: NDArray[np.int64]
    survivor_initial_states: NDArray[np.float64]
    survivor_final_states: NDArray[np.float64]
    checkpoint_times: NDArray[np.float64]
    survivor_counts: NDArray[np.int64]
    midpoint_trajectory_ids: NDArray[np.int64]
    midpoint_times: NDArray[np.float64]
    midpoint_states: NDArray[np.float64]


def _rossler_rhs_batch(states, parameters):
    x = states[:, 0]
    y = states[:, 1]
    z = states[:, 2]
    return np.column_stack(
        (
            -y - z,
            x + parameters.a * y,
            parameters.b + z * (x - parameters.c),
        )
    )


def _rk4_batch_step(states, dt, parameters):
    k1 = _rossler_rhs_batch(states, parameters)
    k2 = _rossler_rhs_batch(states + 0.5 * dt * k1, parameters)
    k3 = _rossler_rhs_batch(states + 0.5 * dt * k2, parameters)
    k4 = _rossler_rhs_batch(states + dt * k3, parameters)
    return states + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def cycle_crossing_distances(
    crossing_states: ArrayLike,
    cycle_states: ArrayLike,
    *,
    coordinate_axes: tuple[int, int],
    coordinate_scales: tuple[float, float],
) -> NDArray[np.float64]:
    """Return each crossing's minimum scaled distance to a reference cycle."""

    crossings = np.asarray(crossing_states, dtype=np.float64)
    cycle = np.asarray(cycle_states, dtype=np.float64)
    axes = np.asarray(coordinate_axes, dtype=int)
    scales = np.asarray(coordinate_scales, dtype=np.float64)
    if crossings.ndim != 2 or crossings.shape[1] != 3:
        raise ValueError("crossing_states must have shape (n,3)")
    if cycle.ndim != 2 or cycle.shape[1] != 3 or len(cycle) == 0:
        raise ValueError("cycle_states must have nonempty shape (p,3)")
    if len(set(coordinate_axes)) != 2 or np.any((axes < 0) | (axes > 2)):
        raise ValueError("coordinate_axes must select two distinct state coordinates")
    if np.any(~np.isfinite(scales)) or np.any(scales <= 0.0):
        raise ValueError("coordinate_scales must be finite and positive")
    differences = (
        crossings[:, None, axes] - cycle[None, :, axes]
    ) / scales[None, None, :]
    return np.min(np.linalg.norm(differences, axis=2), axis=1)


def sprinkler_survivors(
    parameters: RosslerParameters,
    initial_states: ArrayLike,
    section: PoincareSection,
    cycle_states: ArrayLike,
    *,
    dt: float,
    horizon: float,
    capture_coordinate_axes: tuple[int, int],
    capture_coordinate_scales: tuple[float, float],
    capture_radius: float,
    required_capture_crossings: int,
    checkpoint_times: ArrayLike,
    midpoint_window: tuple[float, float],
    escape_radius: float = 1e4,
) -> SprinklerResult:
    """Select long-lived trajectories and their middle-time section points.

    The reference implementation is intentionally conservative and currently
    supports the positive-oriented axis-aligned section used by Barrio et al.
    A trajectory is captured only after a declared number of consecutive
    section returns within a scaled radius of the stable reference cycle.
    """

    initial = np.asarray(initial_states, dtype=np.float64)
    cycle = np.asarray(cycle_states, dtype=np.float64)
    checkpoints = np.asarray(checkpoint_times, dtype=np.float64)
    if initial.ndim != 2 or initial.shape[1] != 3 or len(initial) == 0:
        raise ValueError("initial_states must have nonempty shape (n,3)")
    if not np.all(np.isfinite(initial)):
        raise ValueError("initial_states must be finite")
    if section.normal != (1.0, 0.0, 0.0) or section.direction != 1:
        raise ValueError("sprinkler reference requires an x-plane with direction +1")
    if section.gate_axis is not None:
        raise ValueError("sprinkler reference does not support a gated section")
    if dt <= 0.0 or horizon <= 0.0 or capture_radius <= 0.0:
        raise ValueError("dt, horizon, and capture_radius must be positive")
    if required_capture_crossings < 1 or escape_radius <= 0.0:
        raise ValueError("capture repeats and escape radius must be positive")
    step_count = round(horizon / dt)
    if not np.isclose(step_count * dt, horizon, rtol=0.0, atol=1e-12):
        raise ValueError("horizon must be an integer multiple of dt")
    checkpoint_steps = np.rint(checkpoints / dt).astype(int)
    if (
        np.any(checkpoints <= 0.0)
        or np.any(checkpoints > horizon)
        or np.any(np.diff(checkpoints) <= 0.0)
        or not np.allclose(checkpoint_steps * dt, checkpoints, rtol=0.0, atol=1e-12)
    ):
        raise ValueError("checkpoint_times must be ordered step-aligned times")
    midpoint_start, midpoint_end = map(float, midpoint_window)
    if not (0.0 <= midpoint_start < midpoint_end <= horizon):
        raise ValueError("midpoint_window must lie inside the horizon")

    trajectory_count = len(initial)
    capture_times = np.full(trajectory_count, np.nan, dtype=np.float64)
    failed = np.zeros(trajectory_count, dtype=bool)
    capture_streaks = np.zeros(trajectory_count, dtype=np.int32)
    active_ids = np.arange(trajectory_count, dtype=np.int64)
    active_states = initial.copy()
    checkpoint_counts = []
    checkpoint_index = 0
    record_ids = []
    record_times = []
    record_states = []

    for step in range(1, step_count + 1):
        previous = active_states
        current = _rk4_batch_step(previous, dt, parameters)
        finite = np.all(np.isfinite(current), axis=1)
        bounded = np.linalg.norm(current, axis=1) <= escape_radius
        valid = finite & bounded
        if np.any(~valid):
            failed[active_ids[~valid]] = True

        previous_value = previous[:, 0] - section.offset
        current_value = current[:, 0] - section.offset
        crossed = valid & (previous_value < 0.0) & (current_value >= 0.0)
        crossed_local = np.flatnonzero(crossed)
        captured_local = np.zeros(len(active_ids), dtype=bool)
        if len(crossed_local):
            denominator = current_value[crossed_local] - previous_value[crossed_local]
            alpha = -previous_value[crossed_local] / denominator
            crossing = previous[crossed_local] + alpha[:, None] * (
                current[crossed_local] - previous[crossed_local]
            )
            crossed_ids = active_ids[crossed_local]
            distances = cycle_crossing_distances(
                crossing,
                cycle,
                coordinate_axes=capture_coordinate_axes,
                coordinate_scales=capture_coordinate_scales,
            )
            close = distances <= capture_radius
            capture_streaks[crossed_ids] = np.where(
                close, capture_streaks[crossed_ids] + 1, 0
            )
            newly_captured = (
                capture_streaks[crossed_ids] >= required_capture_crossings
            )
            if np.any(newly_captured):
                local = crossed_local[newly_captured]
                captured_local[local] = True
                capture_times[active_ids[local]] = (step - 1 + alpha[newly_captured]) * dt
            crossing_times = (step - 1 + alpha) * dt
            in_midpoint = (
                (crossing_times >= midpoint_start)
                & (crossing_times <= midpoint_end)
            )
            if np.any(in_midpoint):
                record_ids.append(crossed_ids[in_midpoint])
                record_times.append(crossing_times[in_midpoint])
                record_states.append(crossing[in_midpoint])

        retain = valid & ~captured_local
        active_ids = active_ids[retain]
        active_states = current[retain]
        while (
            checkpoint_index < len(checkpoint_steps)
            and step == checkpoint_steps[checkpoint_index]
        ):
            checkpoint_counts.append(len(active_ids))
            checkpoint_index += 1
        if len(active_ids) == 0:
            while checkpoint_index < len(checkpoint_steps):
                checkpoint_counts.append(0)
                checkpoint_index += 1
            break

    if record_ids:
        all_record_ids = np.concatenate(record_ids)
        all_record_times = np.concatenate(record_times)
        all_record_states = np.concatenate(record_states)
        retained_records = np.isin(all_record_ids, active_ids)
        midpoint_ids = all_record_ids[retained_records]
        midpoint_times = all_record_times[retained_records]
        midpoint_states = all_record_states[retained_records]
    else:
        midpoint_ids = np.empty(0, dtype=np.int64)
        midpoint_times = np.empty(0, dtype=np.float64)
        midpoint_states = np.empty((0, 3), dtype=np.float64)
    return SprinklerResult(
        capture_times=capture_times,
        failed=failed,
        survivor_ids=active_ids,
        survivor_initial_states=initial[active_ids],
        survivor_final_states=active_states,
        checkpoint_times=checkpoints,
        survivor_counts=np.asarray(checkpoint_counts, dtype=np.int64),
        midpoint_trajectory_ids=midpoint_ids,
        midpoint_times=midpoint_times,
        midpoint_states=midpoint_states,
    )
