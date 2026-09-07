"""Bounded, unfiltered dual-section trajectory collection for future studies.

No target runner or sampling/partition policy is supplied. Capture is a label,
never an integration stopping condition. Only endpoint-bracketed Hermite roots
are detected: step refinement/adaptive controls remain necessary. Tangencies
and multiple unbracketed crossings can be missed; this is not all-root detection.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .poincare import PoincareSection
from .saddle import _cubic_hermite_crossing, cycle_crossing_distances


@dataclass(frozen=True)
class CaptureSection:
    section: PoincareSection
    cycle_states: np.ndarray
    axes: tuple[int, int]
    scales: tuple[float, float]
    radius: float
    required_crossings: int

    def validate(self):
        s = self.section
        if (s.direction not in (-1, 1) or np.count_nonzero(s.normal) != 1
                or not np.isfinite(s.offset) or (s.gate_upper is not None and not np.isfinite(s.gate_upper))):
            raise ValueError("finite oriented axis-aligned section required")
        cycle = np.asarray(self.cycle_states, dtype=float)
        if (cycle.ndim != 2 or cycle.shape[1:] != (3,) or not len(cycle) or not np.isfinite(cycle).all()
                or len(self.axes) != 2 or any(type(a) is not int for a in self.axes)
                or len(set(self.axes)) != 2 or any(a not in (0, 1, 2) for a in self.axes)
                or len(self.scales) != 2 or not np.isfinite(self.scales).all() or min(self.scales) <= 0
                or not np.isfinite(self.radius) or self.radius <= 0
                or type(self.required_crossings) is not int or self.required_crossings < 1):
            raise ValueError("invalid capture geometry or threshold")


@dataclass
class PairedCollection:
    status: str
    completed_steps: int
    requested_steps: int
    dt: float
    initial_states: np.ndarray
    final_states: np.ndarray
    failed: np.ndarray
    failure_steps: np.ndarray
    failure_states: np.ndarray
    capture_times: np.ndarray
    capture_streaks: np.ndarray
    ambiguous: np.ndarray
    initial_on_plane: np.ndarray
    events: dict[str, dict[str, np.ndarray]]
    checkpoints: list[dict]
    failure: dict | None
    event_range_start_step: int = 0

    def contingency(self):
        """Mutually exclusive valid-seed capture labels, plus numerical exclusions.

        Not a survivor-selection rule or estimator. Capture and failure arrays
        retain overlaps for any later, explicitly frozen conditioning analysis.
        """
        valid = ~self.failed & ~self.ambiguous.any(axis=1)
        captured = np.isfinite(self.capture_times)
        return {"neither": int(np.sum(valid & ~captured.any(axis=1))),
                "first_only": int(np.sum(valid & captured[:, 0] & ~captured[:, 1])),
                "second_only": int(np.sum(valid & ~captured[:, 0] & captured[:, 1])),
                "both": int(np.sum(valid & captured.all(axis=1))),
                "failed": int(self.failed.sum()),
                "ambiguous_nonfailed": int(np.sum(~self.failed & self.ambiguous.any(axis=1)))}


def rk4_step(rhs, states, dt):
    """The existing batch RK4 arithmetic, with an explicit synthetic-test field."""
    k1 = rhs(states)
    k2 = rhs(states + .5*dt*k1)
    k3 = rhs(states + .5*dt*k2)
    k4 = rhs(states + dt*k3)
    return states + dt/6*(k1 + 2*k2 + 2*k3 + k4)


EVENT_DTYPES = {"seed_ids": np.int64, "steps": np.int64, "times": float, "states": float,
    "orientation": np.int8, "accepted": bool, "signed_scaled_gate_distance": float,
    "normalized_angle": float, "gate_unresolved": bool, "orientation_unresolved": bool,
    "capture_distance": float}


def classify_crossings(states, fields, directions, spec, state_scales, gate_margin, angle_margin):
    """Shared geometry only: root location is owned by the chosen integrator."""
    section = spec.section
    normal = np.asarray(section.normal)
    if fields.shape != states.shape or not np.isfinite(fields).all() or not np.isfinite(states).all():
        raise ValueError("nonfinite or malformed interpolated event field")
    velocity = fields @ normal
    denominator = np.linalg.norm(fields, axis=1)*np.linalg.norm(normal)
    angles = np.divide(np.abs(velocity), denominator, out=np.zeros(len(states)), where=denominator > 0)
    uncertain_orientation = (angles < angle_margin) | (velocity*directions <= 0)
    if section.gate_axis is None:
        gate_distance = np.zeros(len(states))
        gate_ok, uncertain_gate = np.ones(len(states), dtype=bool), np.zeros(len(states), dtype=bool)
    else:
        gate_distance = (states[:, section.gate_axis]-section.gate_upper)/state_scales[section.gate_axis]
        gate_ok = gate_distance < 0
        uncertain_gate = (np.abs(gate_distance) <= gate_margin) & (directions == section.direction)
    return {"orientation": np.broadcast_to(directions, (len(states),)).copy(),
        "accepted": gate_ok & (directions == section.direction),
        "signed_scaled_gate_distance": gate_distance, "normalized_angle": angles,
        "gate_unresolved": uncertain_gate, "orientation_unresolved": uncertain_orientation,
        "capture_distance": cycle_crossing_distances(states, spec.cycle_states,
            coordinate_axes=spec.axes, coordinate_scales=spec.scales)}


def update_capture(event, spec, index, capture_times, streaks, ambiguous):
    """Update one step's labels, with at most one event per seed/section.

    Call in time order. Ambiguity is sticky; no capture label stops a solver.
    """
    event_ids = event["seed_ids"]
    if len(np.unique(event_ids)) != len(event_ids):
        raise ValueError("capture updates require unique seed IDs per event step")
    unresolved = event["gate_unresolved"] | event["orientation_unresolved"]
    ambiguous[event_ids[unresolved], index] = True
    streaks[event_ids[unresolved], index] = 0
    selected = event["accepted"] & ~unresolved & ~ambiguous[event_ids, index]
    selected_ids = event_ids[selected]
    close = event["capture_distance"][selected] <= spec.radius
    streaks[selected_ids, index] = np.where(close, streaks[selected_ids, index]+1, 0)
    newly = (streaks[selected_ids, index] >= spec.required_crossings) & ~np.isfinite(capture_times[selected_ids, index])
    capture_times[selected_ids[newly], index] = event["times"][selected][newly]


def _events(previous, current, ids, left_field, right_field, rhs, spec, step, dt,
            state_scales, gate_margin, angle_margin):
    section = spec.section
    normal = np.asarray(section.normal)
    left, right = previous @ normal-section.offset, current @ normal-section.offset
    groups = []
    for direction in (-1, 1):
        bracket = ((left > 0) & (right <= 0) if direction == -1 else (left < 0) & (right >= 0))
        indices = np.flatnonzero(bracket)
        if not len(indices):
            continue
        alpha, states = _cubic_hermite_crossing(previous[indices], current[indices],
            left_field[indices], right_field[indices], dt=dt, normal=normal,
            offset=section.offset, direction=direction)
        fields = np.asarray(rhs(states))
        # accepted is nominal geometric membership; ambiguous flags are retained
        # separately and are never allowed to increment capture streaks.
        groups.append({"seed_ids": ids[indices], "steps": np.full(len(states), step),
            "times": (step-1+alpha)*dt, "states": states,
            **classify_crossings(states, fields, direction, spec, state_scales, gate_margin, angle_margin)})
    if not groups:
        return {k: np.empty((0, 3) if k == "states" else (0,), dtype=v) for k, v in EVENT_DTYPES.items()}
    combined = {k: np.concatenate([g[k] for g in groups]).astype(v) for k, v in EVENT_DTYPES.items()}
    order = np.lexsort((combined["times"], combined["seed_ids"]))
    return {k: v[order] for k, v in combined.items()}


def validate_collection(
    initial_states, sections: dict[str, CaptureSection], *, dt: float,
    horizon: float, checkpoint_times, state_scales, gate_margin: float,
    angle_margin: float, escape_radius: float, maximum_events: int, maximum_steps: int,
):
    """Validate numerical declarations without calling a field or a solver."""
    initial = np.asarray(initial_states, dtype=float)
    scales = np.asarray(state_scales, dtype=float)
    checkpoints = np.asarray(checkpoint_times, dtype=float)
    if (initial.ndim != 2 or initial.shape[1:] != (3,) or not len(initial) or not np.isfinite(initial).all()
            or len(sections) != 2 or not all(isinstance(k, str) and k for k in sections)
            or scales.shape != (3,) or not np.isfinite(scales).all() or np.any(scales <= 0)
            or not all(np.isfinite(x) and x > 0 for x in (dt, horizon, gate_margin, angle_margin, escape_radius))
            or angle_margin > 1 or type(maximum_events) is not int or maximum_events < 1
            or type(maximum_steps) is not int or maximum_steps < 1):
        raise ValueError("invalid paired collector design")
    for spec in sections.values():
        spec.validate()
    steps = round(horizon/dt)
    if steps < 1 or steps > maximum_steps or not np.isclose(steps*dt, horizon, rtol=0, atol=1e-12):
        raise ValueError("horizon must be bounded and step aligned")
    if (checkpoints.ndim != 1 or not len(checkpoints) or not np.isfinite(checkpoints).all()
            or np.any(checkpoints <= 0) or np.any(np.diff(checkpoints) <= 0) or checkpoints[-1] != horizon):
        raise ValueError("checkpoints must be ordered and end at horizon")
    checkpoint_steps = np.rint(checkpoints/dt).astype(int)
    if not np.allclose(checkpoint_steps*dt, checkpoints, rtol=0, atol=1e-12):
        raise ValueError("checkpoints must be step aligned")
    return initial, scales, steps, checkpoint_steps


def collect_paired_sections(
    rhs: Callable, initial_states, sections: dict[str, CaptureSection], *, dt: float,
    horizon: float, checkpoint_times, state_scales, gate_margin: float,
    angle_margin: float, escape_radius: float, maximum_events: int, maximum_steps: int,
    progress: Callable | None = None, journal_interval_steps: int | None = None,
) -> PairedCollection:
    """Observe two planes on a shared batch, without capture censoring.

    Optional progress callbacks receive detached state snapshots and raw event
    deltas after committed steps. The final return still contains all events.
    A failed callback stops collection without retry. A callback alone does
    not authorize targets or guarantee persistence; the supplied sink owns IO.
    Initial t=0 roots are excluded and flagged; later roots belong to their
    ending step. Caps/interruption never return a truncated prefix as complete.
    """
    if ((progress is None) != (journal_interval_steps is None)
            or (progress is not None and (not callable(progress) or type(journal_interval_steps) is not int
                                         or journal_interval_steps < 1))):
        raise ValueError("progress requires a callable and a positive integer interval")
    initial, scales, steps, checkpoint_steps = validate_collection(initial_states, sections, dt=dt,
        horizon=horizon, checkpoint_times=checkpoint_times, state_scales=state_scales,
        gate_margin=gate_margin, angle_margin=angle_margin, escape_radius=escape_radius,
        maximum_events=maximum_events, maximum_steps=maximum_steps)
    count = len(initial)
    state = initial.copy()
    failed = np.linalg.norm(initial, axis=1) > escape_radius
    failure_steps = np.where(failed, 0, -1)
    failure_states = np.full_like(initial, np.nan)
    failure_states[failed] = initial[failed]
    capture_times = np.full((count, 2), np.nan)
    streaks = np.zeros((count, 2), dtype=int)
    ambiguous = np.zeros((count, 2), dtype=bool)
    on_plane = np.column_stack([initial @ s.section.normal == s.section.offset for s in sections.values()])
    chunks = {name: [] for name in sections}
    snapshots, completed, event_count = [], 0, 0
    status, failure = "completed", None
    # One tuple assignment publishes a whole step. Interruptions during array
    # updates must not pair a new state/capture label with an old horizon.
    committed = (state, failed, failure_steps, failure_states, capture_times, streaks, ambiguous, completed, event_count)
    last_emitted_step = 0

    def snapshot(snapshot_status, snapshot_failure, start=0):
        st, bad, fsteps, fstates, ct, streak, amb, end, _ = committed
        events = {}
        for name, items in chunks.items():
            selected = [item for item in items if start < item["steps"][0] <= end]
            events[name] = {k: np.concatenate([item[k] for item in selected]) if selected else
                           np.empty((0, 3) if k == "states" else (0,), dtype=v) for k, v in EVENT_DTYPES.items()}
        checkpoints_copy = [{k: v.copy() if isinstance(v, np.ndarray) else v for k, v in item.items()}
                            for item in snapshots if item["step"] <= end]
        return PairedCollection(snapshot_status, end, steps, dt, initial.copy(), st.copy(), bad.copy(), fsteps.copy(),
            fstates.copy(), ct.copy(), streak.copy(), amb.copy(), on_plane.copy(), events, checkpoints_copy,
            snapshot_failure, start)
    try:
        for step in range(1, steps+1):
            failure_phase = "integration"
            ids = np.flatnonzero(~failed)
            previous = state[ids]
            current = rk4_step(rhs, previous, dt) if len(ids) else previous.copy()
            if np.shape(current) != previous.shape:
                raise ValueError("batch field/step changed array shape")
            valid = np.isfinite(current).all(axis=1) & (np.linalg.norm(current, axis=1) <= escape_radius)
            good_ids = ids[valid]
            left, right = ((np.asarray(rhs(previous[valid])), np.asarray(rhs(current[valid]))) if len(good_ids)
                           else (np.empty((0, 3)), np.empty((0, 3))))
            if (left.shape != previous[valid].shape or right.shape != current[valid].shape
                    or not np.isfinite(left).all() or not np.isfinite(right).all()):
                raise ValueError("invalid endpoint field")
            pending = {name: _events(previous[valid], current[valid], good_ids, left, right, rhs, spec,
                step, dt, scales, gate_margin, angle_margin) for name, spec in sections.items()}
            added = sum(len(x["times"]) for x in pending.values())
            if event_count + added > maximum_events:
                status, failure = "event-limit", {"attempted_step": step, "uncommitted_step_events": added}
                break
            # All-or-nothing step commit: both sections and state share the same
            # completed horizon even if the record cap or an event call fails.
            state, failed, failure_steps, failure_states, capture_times, streaks, ambiguous = (
                value.copy() for value in committed[:7])
            failure_steps[ids[~valid]] = step
            failure_states[ids[~valid]] = current[~valid]
            failed[ids[~valid]] = True
            state[good_ids] = current[valid]
            for index, (name, spec) in enumerate(sections.items()):
                event = pending[name]
                if len(event["times"]):
                    chunks[name].append(event)
                # A segment lying in a plane has no endpoint sign change. Keep
                # its ambiguity explicit instead of silently declaring no returns.
                sliding = ((previous[valid] @ spec.section.normal == spec.section.offset)
                           & (current[valid] @ spec.section.normal == spec.section.offset))
                ambiguous[good_ids[sliding], index] = True
                update_capture(event, spec, index, capture_times, streaks, ambiguous)
            if step in checkpoint_steps:
                snapshots.append({"step": step, "time": step*dt, "failed": failed.copy(),
                                  "captured": np.isfinite(capture_times).copy(), "ambiguous": ambiguous.copy()})
            committed = (state, failed, failure_steps, failure_states, capture_times, streaks, ambiguous, step, event_count+added)
            completed, event_count = committed[-2:]
            if progress is not None and (step % journal_interval_steps == 0 or step == steps):
                failure_phase = "journal"
                progress(snapshot("running", None, last_emitted_step))
                last_emitted_step = step
    except (Exception, KeyboardInterrupt) as error:
        status = "interrupted" if isinstance(error, KeyboardInterrupt) else "failed"
        failure = {"type": type(error).__name__, "message": str(error), "attempted_step": step,
                   "phase": failure_phase}
    return snapshot(status, failure)
