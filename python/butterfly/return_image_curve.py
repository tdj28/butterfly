"""Continuous finite-return image curves and their event-time sensitivities.

This is not an invariant-manifold constructor. Every oriented root must pass
the section gate; a rejected root makes this specialized path unresolved.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

from .return_geometry import event_corrected_tangent


def image_returns(rhs, jacobian, state, tangent, section, *, count, method="DOP853",
                  rtol=1e-10, atol=1e-12, max_step=.02, time_per_return=20.,
                  initial_root_guard=1e-8, minimum_angle=1e-7):
    state, tangent = np.asarray(state, float), np.asarray(tangent, float)
    normal = np.asarray(section.normal, float)
    if (state.shape != (3,) or tangent.shape != (3,)
            or not np.isfinite(state).all() or not np.isfinite(tangent).all()
            or np.linalg.norm(tangent) == 0 or abs(normal @ tangent) > 1e-12
            or section.direction not in (-1, 1) or not section.accepts(state)
            or abs(section.value(state)) > 1e-10 or type(count) is not int or not 1 <= count <= 32
            or method not in ("DOP853", "Radau")
            or not np.isfinite([rtol, atol, max_step, time_per_return, initial_root_guard, minimum_angle]).all()
            or min(rtol, atol, max_step, time_per_return, initial_root_guard, minimum_angle) <= 0
            or initial_root_guard >= time_per_return or minimum_angle >= 1):
        raise ValueError("invalid bounded image-curve declaration")
    field = np.asarray(rhs(0., state), float)
    event_corrected_tangent(tangent[:, None], field, normal, minimum_angle=minimum_angle)
    if section.direction*(normal @ field) <= 0:
        raise ValueError("wrong initial orientation")

    def augmented(time, value):
        field = np.asarray(rhs(time, value[:3]), float)
        matrix = np.asarray(jacobian(time, value[:3]), float)
        if field.shape != (3,) or matrix.shape != (3, 3) or not np.isfinite(field).all() or not np.isfinite(matrix).all():
            raise ValueError("nonfinite or malformed field/Jacobian")
        return np.r_[field, matrix @ value[3:]]

    initial = np.r_[state, tangent]
    kwargs = dict(method=method, rtol=rtol, atol=atol, max_step=max_step)
    guard = solve_ivp(augmented, (0., initial_root_guard), initial, **kwargs)
    if not guard.success or not np.isfinite(guard.y).all():
        raise ValueError("initial root-guard integration failed")
    guarded = guard.y[:, -1]
    if section.direction*section.value(guarded[:3]) <= 0:
        raise ValueError("initial guard did not leave the section in the required direction")

    def event(_time, value):
        return float(normal @ value[:3]-section.offset)
    event.direction = section.direction
    event.terminal = count
    solution = solve_ivp(augmented, (initial_root_guard, count*time_per_return), guarded,
                         events=event, **kwargs)
    raw = np.asarray(solution.y_events[0]).reshape(-1, 6)
    times = solution.t_events[0]
    if not solution.success or not np.isfinite(solution.y).all() or not np.isfinite(raw).all():
        raise ValueError("continuous state/variational integration failed")
    rows = []
    for time, value in zip(times, raw, strict=True):
        field = np.asarray(rhs(float(time), value[:3]), float)
        denominator = np.linalg.norm(normal)*np.linalg.norm(field)
        angle = abs(normal @ field)/denominator if denominator else 0.
        valid = bool(section.accepts(value[:3]) and section.direction*(normal @ field) > 0
                     and np.isfinite(angle) and angle >= minimum_angle)
        corrected, time_gradient = (None, None)
        if valid:
            corrected, time_gradient = event_corrected_tangent(value[3:, None], field, normal, minimum_angle=minimum_angle)
        rows.append(dict(time=float(time), state=value[:3].tolist(), raw_tangent=value[3:].tolist(),
            tangent=corrected[:, 0].tolist() if valid else None,
            time_gradient=float(time_gradient[0]) if valid else None,
            normalized_angle=float(angle), section_residual=section.value(value[:3]),
            accepted=section.accepts(value[:3]), valid=valid))
    return dict(status="returned" if len(rows) == count and all(r["valid"] for r in rows) else "unresolved",
        requested_returns=count, initial_state=state.tolist(), initial_tangent=tangent.tolist(),
        guarded_state=guarded[:3].tolist(), guarded_tangent=guarded[3:].tolist(),
        method=method, rtol=rtol, atol=atol, max_step=max_step, time_per_return=time_per_return,
        initial_root_guard=initial_root_guard, minimum_angle=minimum_angle, events=rows,
        nfev=guard.nfev+solution.nfev, njev=guard.njev+solution.njev)


def observe_curve(result, *, scales=(15., .01), minimum_gain=1e-4, minimum_x_component=.001):
    if result["status"] != "returned" or len(result["events"]) < 2:
        return dict(valid=False, reason="missing or invalid image return")
    before, after = result["events"][-2:]
    scale = np.asarray(scales, float)
    v = np.asarray(before["tangent"])[[0, 2]]/scale
    w = np.asarray(after["tangent"])[[0, 2]]/scale
    gain = float(np.linalg.norm(v))
    fraction = abs(v[0])/gain if gain else 0.
    valid = gain >= minimum_gain and fraction >= minimum_x_component
    return dict(valid=bool(valid), image_state=before["state"], next_state=after["state"],
        gain=gain, normalized_x_component=float(fraction), input_x_tangent=float(v[0]),
        normalized_output_derivative=float(w[0]/gain) if gain else None,
        x_graph_slope=float(w[0]/v[0]) if valid else None)


def candidate_intervals(observations):
    """All adjacent signs, with input-projection turns and gaps excluded.

    Exact grid zeros require both neighbors; no arbitrary nearest-grid root.
    Entries are grid indices; touching intervals at an exact zero are one item.
    """
    brackets = []
    def connected(indices):
        return all(observations[i]["valid"] for i in indices) and (
            all(observations[i]["input_x_tangent"] > 0 for i in indices)
            or all(observations[i]["input_x_tangent"] < 0 for i in indices))
    for i in range(len(observations)-1):
        if connected([i, i+1]) and observations[i]["x_graph_slope"]*observations[i+1]["x_graph_slope"] < 0:
            brackets.append([i, i+1])
    for i in range(1, len(observations)-1):
        if connected([i-1, i, i+1]) and observations[i]["x_graph_slope"] == 0 and observations[i-1]["x_graph_slope"]*observations[i+1]["x_graph_slope"] < 0:
            brackets.append([i-1, i+1])
    return sorted(brackets)
