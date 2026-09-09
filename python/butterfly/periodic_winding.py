"""Numerical closed-cycle winding and shorter-period checks, not a proof."""
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

from .projected_winding import hermite, polygon_measure, window_nodes


SCALES = np.array([15., 15., .01])


def dense_value(raw, method, t):
    """Replay retained SciPy polynomial coefficients without an ODE solve.

    DOP853 uses its alternating degree-seven recurrence; Radau stores Q for
    powers x,x^2,x^3 (without another step-size factor). No pickle is used.
    """
    times = raw["times"]
    if not times[0] <= t <= times[-1]:
        raise ValueError("dense query outside retained trajectory")
    i = max(0, int(np.searchsorted(times, t, side="left"))-1)
    x = (t-times[i])/(times[i+1]-times[i])
    old, coefficients = raw["dense_old"][i], raw["dense_coefficients"][i]
    if method == "DOP853":
        q = np.zeros_like(old)
        for j, f in enumerate(coefficients[::-1]):
            q = (q+f)*(x if j % 2 == 0 else 1-x)
        return q+old
    if method == "Radau":
        return old+coefficients @ np.cumprod(np.full(coefficients.shape[1], x))
    raise ValueError("unsupported retained dense method")


def interpolate(times, states, field, t):
    j = int(np.searchsorted(times, t))
    if j < len(times) and times[j] == t:
        return np.asarray(states[j]).copy()
    if not 0 < j < len(times):
        raise ValueError("query outside retained trajectory")
    return hermite(times[j-1], times[j], states[j-1], states[j],
                   field(times[j-1], states[j-1]), field(times[j], states[j]), t)


def measure_cycle(times, states, extrema, events, period, origin, field):
    """Two phase-aligned windows; winding is measured before comparing counts.

    A multiplicity must divide both section counts. Excluding each such
    divisor numerically is conditional on complete, transverse event counts.
    """
    if not np.isfinite(period) or period <= 0:
        raise ValueError("positive finite period required")
    windows = []
    for phase in (.25, 1.25):
        start, end = phase*period, (phase+1)*period
        nodes = window_nodes(times, states, extrema, field, start, end)
        endpoints = np.array([nodes["raw"][i][1] for i in (0, -1)])
        closure = float(np.linalg.norm((endpoints[1]-endpoints[0])/SCALES))
        geometry = {}
        for name, rows in nodes.items():
            xy = np.array([q[:2] for _, q in rows])-np.asarray(origin)[:2]
            geometry[name] = polygon_measure(np.vstack((xy, xy[0])))
        selected = {name: [e for e in rows if start <= e["time"] < end and e["accepted"]]
                    for name, rows in events.items()}
        counts = {name: len(rows) for name, rows in selected.items()}
        gcd = math.gcd(*counts.values())
        divisors = [m for m in range(2, gcd+1) if gcd % m == 0]
        shorter = []
        for m in divisors:
            point = interpolate(times, states, field, start+period/m)
            distance = float(np.linalg.norm((point-endpoints[0])/SCALES))
            shorter.append(dict(multiplicity=m, scaled_separation=distance, excluded=distance >= 1e-5))
        event_states = {name: [e["state"] for e in rows] for name, rows in selected.items()}
        distinct = {name: min((float(np.linalg.norm((np.array(a)-b)/SCALES))
                              for i, a in enumerate(rows) for b in rows[i+1:]), default=None)
                    for name, rows in event_states.items()}
        angles = [e["angle"] for rows in selected.values() for e in rows]
        boundary_margin = min((min(abs(e["time"]-start), abs(e["time"]-end))/period
                               for rows in events.values() for e in rows if e["accepted"]), default=0.)
        geometry_ok = all(g["qualified"] for g in geometry.values())
        indices = [g["cut_index"] for g in geometry.values()]
        winding_agrees = len(set(indices)) == 1 and indices[0] == counts["historical"]
        primitive = (all(n > 0 for n in counts.values()) and all(v["excluded"] for v in shorter)
                     and all(v is None or v >= 1e-5 for v in distinct.values()))
        qualified = (closure <= 1e-6 and geometry_ok and winding_agrees and primitive
                     and bool(angles) and min(angles) >= 1e-6 and boundary_margin >= 1e-7)
        windows.append(dict(phase=phase, closure_scaled=closure, geometry=geometry,
            counts=counts, shorter_periods=shorter, conditional_minimal_period=bool(primitive),
            minimum_distinct_event_separation=distinct, minimum_crossing_angle=min(angles) if angles else None,
            boundary_phase_margin=boundary_margin,
            event_states=event_states, event_phases={name: [(e["time"]-start)/period for e in rows]
                                                   for name, rows in selected.items()},
            endpoints=endpoints.tolist(), qualified=bool(qualified)))
    a, b = windows
    repeat = compare_windows(a, b)
    return dict(windows=windows, repeat=repeat,
                qualified=bool(all(w["qualified"] for w in windows) and repeat["passed"]),
                rigorous_minimal_period_proof=False)


def compare_windows(a, b):
    same = a["counts"] == b["counts"]
    state, phase = None, None
    if same and all(a["counts"].values()):
        state = max(float(np.max(np.linalg.norm((np.array(a["event_states"][k])-b["event_states"][k])/SCALES, axis=1)))
                    for k in a["counts"])
        phase = max(float(np.max(np.abs(np.array(a["event_phases"][k])-b["event_phases"][k]))) for k in a["counts"])
    return dict(same_counts=same, scaled_state_error=state, phase_error=phase,
                passed=bool(same and state is not None and state <= 1e-6 and phase <= 1e-7))


def observe(field, initial, period, sections, config, retain):
    """Retain ordinary events and independently bracket roots by extrema."""
    callbacks = []
    for section in sections.values():
        def plane(t, q, section=section):
            return section.value(q)
        def extremum(t, q, section=section):
            return float(np.dot(section.normal, field(t, q)))
        for callback in (plane, extremum):
            callback.direction, callback.terminal = 0, False
            callbacks.append(callback)
    sol = solve_ivp(field, (0., 2.5*period), initial, events=callbacks, dense_output=True, **config)
    raw = dict(times=sol.t, states=sol.y.T)
    raw["dense_old"] = np.array([s.y_old for s in sol.sol.interpolants])
    attribute = "F" if config["method"] == "DOP853" else "Q"
    raw["dense_coefficients"] = np.array([getattr(s, attribute) for s in sol.sol.interpolants])
    for i, name in enumerate(sections):
        for j, kind in enumerate(("ordinary", "extrema")):
            raw[name+"_"+kind+"_times"] = sol.t_events[2*i+j]
            raw[name+"_"+kind+"_states"] = sol.y_events[2*i+j].reshape(-1, 3)
    retain(raw)  # retain before any success/geometry test
    if not sol.success or not np.isfinite(sol.y).all():
        raise ValueError("cycle observation integration failed")
    events, extrema, uncertain = {}, [], []
    for i, (name, section) in enumerate(sections.items()):
        knots = np.unique(np.r_[0., sol.t_events[2*i+1], 2.5*period])
        values = [section.value(sol.sol(t)) for t in knots]
        rows = []
        for left, right, a, b in zip(knots[:-1], knots[1:], values[:-1], values[1:], strict=True):
            if a*b < 0:
                t = brentq(lambda t: section.value(sol.sol(t)), left, right, xtol=1e-12, rtol=1e-14)
                q = sol.sol(t)
                f = field(t, q)
                velocity = float(np.dot(section.normal, f))
                rows.append(dict(time=float(t), state=q.tolist(), normal_velocity=velocity,
                    angle=float(abs(velocity)/(np.linalg.norm(section.normal)*np.linalg.norm(f))),
                    residual=float(section.value(q)), bracket=[float(left), float(right)],
                    accepted=bool(section.accepts(q) and section.direction*velocity > 0)))
        events[name] = rows
        for t, q in zip(sol.t_events[2*i+1], sol.y_events[2*i+1], strict=True):
            e = dict(time=float(t), state=q.tolist(), section=name, plane_value=float(section.value(q)))
            extrema.append(e)
            if .25*period <= t <= 2.25*period and abs(e["plane_value"]) <= 1e-8:
                uncertain.append(e)
    return raw, dict(events=events, extrema=extrema, uncertain_extrema=uncertain,
                     maximum_event_residual=max((abs(e["residual"]) for rows in events.values() for e in rows), default=0.))
