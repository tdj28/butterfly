"""Bounded one-seed adaptive control for paired-section numerical checks.

Public SciPy DOP853/Radau steps and dense interpolants supply independent
integration/root arithmetic. Geometry and capture policy are shared with RK4.
Only endpoint-bracketed roots are located; this is not all-root detection.
No target inputs, execution authority, automatic retry or resume are supplied.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import DOP853, Radau
from scipy.optimize import brentq

from .paired_sampling import SECTIONS
from .paired_sections import CaptureSection, EVENT_DTYPES, classify_crossings, update_capture


def collect_adaptive_sections(rhs, initial_state, global_seed_id, sections, *, method, horizon,
        rtol, atol, max_step, state_scales, gate_margin, angle_margin, escape_radius,
        maximum_steps, maximum_field_evaluations, maximum_events, progress=None, recording_interval=1000):
    """Collect one seed without capture censoring; preserve committed prefixes.

    ``rhs`` has the same autonomous batched signature as the RK4 collector.
    A callback receives a detached full-prefix snapshot at the fixed interval
    and at completion/failure. It must persist it if durability is required.
    Callback failure stops without retry. A process kill cannot return a final
    snapshot; callers must never infer completion from the last progress file.
    """
    initial, scales = np.asarray(initial_state, float), np.asarray(state_scales, float)
    if (initial.shape != (3,) or not np.isfinite(initial).all() or scales.shape != (3,)
            or not np.isfinite(scales).all() or np.any(scales <= 0)
            or type(global_seed_id) is not int or not 0 <= global_seed_id <= np.iinfo(np.int64).max
            or method not in ("DOP853", "Radau") or list(sections) != list(SECTIONS)
            or not all(isinstance(s, CaptureSection) for s in sections.values())
            or not all(np.isfinite(x) and x > 0 for x in
                       (horizon, rtol, atol, max_step, gate_margin, angle_margin, escape_radius))
            or rtol < 100*np.finfo(float).eps or angle_margin > 1
            or any(type(x) is not int or x < 1 for x in
                   (maximum_steps, maximum_field_evaluations, maximum_events, recording_interval))
            or (progress is not None and not callable(progress))):
        raise ValueError("invalid bounded adaptive design")
    for spec in sections.values():
        spec.validate()
    on_plane = np.array([[initial @ s.section.normal == s.section.offset for s in sections.values()]])
    # Each appended row is an atomic state/event commit; unfinished steps never
    # leak a new horizon paired with an old event prefix.
    rows = [{"time": 0., "state": initial.copy(), "capture_times": np.full((1, 2), np.nan),
             "capture_streaks": np.zeros((1, 2), np.int64), "ambiguous": np.zeros((1, 2), bool),
             "events": {}, "event_count": 0}]
    calls = 0
    status, failure = "running", None
    phase = "initialization"

    def field(t, y):
        nonlocal calls
        if calls >= maximum_field_evaluations:
            raise RuntimeError("adaptive field-evaluation cap reached")
        calls += 1
        values = np.asarray(rhs(np.asarray(y)[None, :]), float)
        if values.shape != (1, 3) or not np.isfinite(values).all():
            raise ValueError("invalid adaptive field value")
        return values[0]

    def snapshot():
        latest = rows[-1]
        events = {}
        for name in SECTIONS:
            chunks = [r["events"][name] for r in rows if name in r["events"]]
            events[name] = {k: np.concatenate([r[k] for r in chunks]) if chunks else
                np.empty((0, 3) if k == "states" else (0,), dtype=v) for k, v in EVENT_DTYPES.items()}
            events[name]["global_seed_ids"] = np.full(len(events[name]["times"]), global_seed_id, np.int64)
        return {"status": status, "completed": status == "completed", "method": method, "horizon": horizon,
            "completed_steps": len(rows)-1, "field_evaluations": calls, "observed_until": latest["time"],
            "global_seed_ids": np.array([global_seed_id], np.int64), "initial_states": initial[None, :].copy(),
            "final_states": latest["state"][None, :].copy(), "initial_on_plane": on_plane.copy(),
            **{key: latest[key].copy() for key in ("capture_times", "capture_streaks", "ambiguous")},
            "events": events, "integration_times": np.array([r["time"] for r in rows]),
            "integration_states": np.array([r["state"] for r in rows]), "failure": None if failure is None else dict(failure)}

    try:
        if np.linalg.norm(initial) > escape_radius:
            raise ValueError("initial state outside escape bound")
        solver = {"DOP853": DOP853, "Radau": Radau}[method](field, 0., initial.copy(), horizon,
            rtol=rtol, atol=atol, max_step=max_step, vectorized=False)
        while solver.status == "running":
            phase = "integration"
            if len(rows)-1 >= maximum_steps:
                raise RuntimeError("adaptive step cap reached")
            message = solver.step()
            if solver.status == "failed":
                raise RuntimeError(f"adaptive solver failed: {message}")
            previous, time, state = rows[-1], float(solver.t), solver.y.copy()
            if (not np.isfinite(state).all() or np.linalg.norm(state) > escape_radius
                    or not previous["time"] < time <= horizon):
                raise ValueError("invalid adaptive endpoint or escape")
            step = len(rows)
            pending = {}
            capture = {k: previous[k].copy() for k in ("capture_times", "capture_streaks", "ambiguous")}
            dense = None
            phase = "events"
            for index, (name, spec) in enumerate(sections.items()):
                section = spec.section
                left = section.value(previous["state"])
                right = section.value(state)
                if left == right == 0:
                    capture["ambiguous"][0, index] = True
                direction = -1 if left > 0 and right <= 0 else 1 if left < 0 and right >= 0 else 0
                if not direction:
                    continue  # t=0/root-left endpoints excluded, same as RK4
                if dense is None:
                    dense = solver.dense_output()
                root = float(brentq(lambda t: section.value(dense(t)), previous["time"], time,
                    xtol=4*np.finfo(float).eps, rtol=4*np.finfo(float).eps))
                event_state = dense(root)[None, :]
                event = {"seed_ids": np.array([0]), "steps": np.array([step]),
                    "times": np.array([root]), "states": event_state,
                    **classify_crossings(event_state, field(root, event_state[0])[None, :], direction,
                                        spec, scales, gate_margin, angle_margin)}
                event = {k: np.asarray(event[k], dtype=dtype) for k, dtype in EVENT_DTYPES.items()}
                pending[name] = event
                update_capture(event, spec, index, capture["capture_times"], capture["capture_streaks"], capture["ambiguous"])
            event_count = previous["event_count"] + sum(len(e["times"]) for e in pending.values())
            if event_count > maximum_events:
                raise RuntimeError("adaptive event cap reached")
            rows.append({"time": time, "state": state, **capture, "events": pending, "event_count": event_count})
            if progress is not None and step % recording_interval == 0:
                phase = "recording"
                progress(snapshot())
        if rows[-1]["time"] != horizon:
            raise RuntimeError("adaptive integration ended before declared horizon")
        status = "completed"
    except (Exception, KeyboardInterrupt) as error:
        status = "interrupted" if isinstance(error, KeyboardInterrupt) else "failed"
        failure = {"type": type(error).__name__, "message": str(error), "phase": phase,
                   "attempted_step": len(rows)}
    if progress is not None and not (failure is not None and phase == "recording"):
        try:
            progress(snapshot())
        except (Exception, KeyboardInterrupt) as error:
            status = "interrupted" if isinstance(error, KeyboardInterrupt) else "failed"
            failure = {"type": type(error).__name__, "message": str(error), "phase": "recording"}
    return snapshot()


def rk4_comparison_record(collection, global_seed_id):
    """Normalize a one-seed RK4 collection, without hiding numerical failure."""
    if (collection.initial_states.shape != (1, 3) or type(global_seed_id) is not int
            or not 0 <= global_seed_id <= np.iinfo(np.int64).max):
        raise ValueError("one RK4 seed and valid original global ID required")
    return {"status": collection.status if not collection.failed.any() else "failed",
        "global_seed_ids": np.array([global_seed_id], np.int64),
        "initial_states": collection.initial_states.copy(),
        "horizon": collection.requested_steps*collection.dt,
        "observed_until": collection.completed_steps*collection.dt,
        "ambiguous": collection.ambiguous.copy(), "initial_on_plane": collection.initial_on_plane.copy(),
        "capture_times": collection.capture_times.copy(),
        "events": {name: {**{k: v.copy() for k, v in event.items()},
            "global_seed_ids": np.full(len(event["times"]), global_seed_id, np.int64)}
            for name, event in collection.events.items()}}


def compare_event_profiles(left, right, *, state_scales, maximum_state_difference, maximum_time_difference):
    """Compare one original seed, including rejected roots and capture labels.

    Inputs are normalized by a future source-bound qualification wrapper.
    Exact counts/orientation/membership/ambiguity masks and finite ordered
    event coordinates are required. No alignment, deletion or phase rotation.
    """
    scales = np.asarray(state_scales, float)
    if (scales.shape != (3,) or not np.isfinite(scales).all() or np.any(scales <= 0)
            or not all(np.isfinite(x) and x > 0 for x in (maximum_state_difference, maximum_time_difference))):
        raise ValueError("finite positive numerical comparison tolerances required")
    if (not np.array_equal(left["global_seed_ids"], right["global_seed_ids"])
            or np.asarray(left["global_seed_ids"]).shape != (1,)
            or not np.array_equal(left["initial_states"], right["initial_states"])
            or np.asarray(left["initial_states"]).shape != (1, 3)
            or not np.isfinite(left["initial_states"]).all()
            or left["horizon"] != right["horizon"]):
        raise ValueError("comparison needs the same original seed and horizon")
    result = {"passed": False, "sections": {}, "reason": "incomplete or ambiguous profile"}
    if any(p["status"] != "completed" or p["observed_until"] != p["horizon"]
           or np.asarray(p["ambiguous"]).any() for p in (left, right)):
        return result
    if any(list(p["events"]) != list(SECTIONS) for p in (left, right)):
        raise ValueError("exact ordered two-section set required")
    if not np.array_equal(left["initial_on_plane"], right["initial_on_plane"]):
        return {**result, "reason": "initial-plane membership differs"}
    for name in SECTIONS:
        a, b = left["events"][name], right["events"][name]
        row = {"left_raw_count": len(a["times"]), "right_raw_count": len(b["times"]),
               "left_accepted_count": int(a["accepted"].sum()), "right_accepted_count": int(b["accepted"].sum()),
               "passed": False}
        result["sections"][name] = row
        for e in (a, b):
            for key, dtype in {**EVENT_DTYPES, "global_seed_ids": np.int64}.items():
                value = np.asarray(e[key])
                shape = (len(e["times"]), 3) if key == "states" else (len(e["times"]),)
                if value.shape != shape or value.dtype.kind != np.dtype(dtype).kind:
                    raise ValueError("invalid raw event field shape or dtype")
            if (not np.isfinite(e["times"]).all() or not np.isfinite(e["states"]).all()
                    or np.asarray(e["states"]).shape != (len(e["times"]), 3)
                    or np.any(np.diff(e["times"]) <= 0) or np.any(e["times"] <= 0)
                    or np.any(e["times"] > left["horizon"])
                    or np.any(e["seed_ids"] != 0)
                    or not np.isin(e["orientation"], [-1, 1]).all()
                    or not np.all(e["global_seed_ids"] == left["global_seed_ids"][0])):
                raise ValueError("invalid ordered raw event table")
        same_masks = all(np.array_equal(a[k], b[k]) for k in
            ("orientation", "accepted", "gate_unresolved", "orientation_unresolved"))
        if any(np.asarray(e[k]).any() for e in (a, b) for k in ("gate_unresolved", "orientation_unresolved")):
            row["reason"] = "unresolved raw root"
            continue
        if len(a["times"]) != len(b["times"]) or not same_masks:
            row["reason"] = "raw event count or membership differs"
            continue
        state_error = float(np.max(np.linalg.norm((a["states"]-b["states"])/scales, axis=1), initial=0))
        time_error = float(np.max(np.abs(a["times"]-b["times"]), initial=0))
        row.update(maximum_scaled_state_difference=state_error, maximum_time_difference=time_error,
            passed=bool(state_error <= maximum_state_difference and time_error <= maximum_time_difference))
    ac, bc = np.asarray(left["capture_times"]), np.asarray(right["capture_times"])
    if (ac.shape != (1, 2) or bc.shape != (1, 2) or np.isinf(ac).any() or np.isinf(bc).any()
            or any(np.any(c[np.isfinite(c)] <= 0) or np.any(c[np.isfinite(c)] > left["horizon"]) for c in (ac, bc))):
        raise ValueError("invalid capture labels")
    same_capture = np.array_equal(np.isfinite(ac), np.isfinite(bc))
    capture_error = float(np.max(np.abs(ac[np.isfinite(ac)]-bc[np.isfinite(bc)]), initial=0)) if same_capture else None
    result.update(capture_membership_agrees=same_capture, maximum_capture_time_difference=capture_error,
        passed=bool(all(r["passed"] for r in result["sections"].values()) and same_capture
                    and capture_error <= maximum_time_difference),
        reason="ordered numerical event/capture comparison; no long-time or all-root guarantee")
    return result
