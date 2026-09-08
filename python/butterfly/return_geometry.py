"""Local two-dimensional return geometry, not a fitted scalar partition.

Differentiating n.T phi(tau(q), q) = offset gives
DP = (I - f n.T / (n.T f)) D_q phi. A projected critical point additionally
requires a justified curve tangent; a coordinate partial alone is not it.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

from .poincare import PoincareSection


def event_corrected_tangent(flow_tangent, field, normal, *, minimum_angle=1e-7):
    """Correct fixed-time sensitivities for the moving return time."""
    tangent = np.asarray(flow_tangent, float)
    field, normal = np.asarray(field, float), np.asarray(normal, float)
    if (field.shape != (3,) or normal.shape != (3,) or tangent.ndim != 2
            or tangent.shape[0] != 3 or not np.isfinite(tangent).all()
            or not np.isfinite(field).all() or not np.isfinite(normal).all()
            or not np.isfinite(minimum_angle) or not 0 < minimum_angle < 1):
        raise ValueError("finite 3D sensitivity, field, normal and positive angle required")
    denominator = float(normal @ field)
    scale = float(np.linalg.norm(normal)*np.linalg.norm(field))
    if scale == 0 or abs(denominator)/scale < minimum_angle:
        raise ValueError("return is not sufficiently transverse")
    time_gradient = -(normal @ tangent)/denominator
    corrected = tangent + np.outer(field, time_gradient)
    return corrected, time_gradient


def first_return_geometry(rhs, jacobian, initial_state, section: PoincareSection, *,
                          method="DOP853", rtol=1e-10, atol=1e-12, max_step=.02,
                          horizon=20., initial_root_guard=1e-8, minimum_angle=1e-7):
    """Integrate a state and two section-tangent columns to its first return.

    All detected oriented roots are retained, including rejected gates and the
    initial root. Initial states must lie on an oriented axis-aligned section.
    Dense solver event detection is not an interval proof or all-root guarantee.
    Horizon, finite data, transversality and integration success are explicit.
    """
    state = np.asarray(initial_state, float)
    normal = np.asarray(section.normal, float)
    if (state.shape != (3,) or not np.isfinite(state).all()
            or np.count_nonzero(normal) != 1 or section.direction not in (-1, 1)
            or method not in ("DOP853", "Radau")
            or not np.isfinite([rtol, atol, max_step, horizon, initial_root_guard, minimum_angle]).all()
            or min(rtol, atol, max_step, horizon, initial_root_guard, minimum_angle) <= 0
            or initial_root_guard >= horizon or minimum_angle >= 1
            or abs(section.value(state)) > 1e-10 or not section.accepts(state)):
        raise ValueError("invalid initial section or bounded solver declaration")
    initial_field = np.asarray(rhs(0., state), float)
    axes = tuple(np.flatnonzero(normal == 0).tolist())
    basis = np.eye(3)[:, axes]
    event_corrected_tangent(basis, initial_field, normal, minimum_angle=minimum_angle)
    if normal @ initial_field * section.direction <= 0:
        raise ValueError("initial orientation disagrees with section")

    def augmented(time, value):
        current, tangent = value[:3], value[3:].reshape(3, 2)
        field = np.asarray(rhs(time, current), float)
        matrix = np.asarray(jacobian(time, current), float)
        if field.shape != (3,) or matrix.shape != (3, 3) or not np.isfinite(field).all() or not np.isfinite(matrix).all():
            raise ValueError("field/Jacobian returned malformed or nonfinite values")
        return np.r_[field, (matrix @ tangent).ravel()]

    def event(_time, value):
        return float(normal @ value[:3]-section.offset)
    event.direction = section.direction
    event.terminal = False
    solution = solve_ivp(augmented, (0., horizon), np.r_[state, basis.ravel()],
        method=method, rtol=rtol, atol=atol, max_step=max_step, events=event)
    times = solution.t_events[0]
    raw = np.asarray(solution.y_events[0]).reshape(-1, 9)
    if not solution.success or not np.isfinite(solution.y).all() or not np.isfinite(raw).all():
        raise ValueError("state/variational integration failed or became nonfinite")
    gates = np.array([section.accepts(row[:3]) for row in raw], bool)
    selected = np.flatnonzero((times > initial_root_guard) & gates)
    result = dict(status="no-return", axes=list(axes), initial_state=state,
        raw_event_times=times, raw_event_states=raw[:, :3], raw_event_tangents=raw[:, 3:].reshape(-1, 3, 2),
        raw_event_gate_accepted=gates, method=method, rtol=rtol, atol=atol,
        max_step=max_step, horizon=horizon, initial_root_guard=initial_root_guard,
        minimum_angle=minimum_angle, nfev=solution.nfev, njev=solution.njev)
    if not len(selected):
        return result
    index = int(selected[0])
    duration, final = float(times[index]), raw[index, :3]
    field = np.asarray(rhs(duration, final), float)
    corrected, time_gradient = event_corrected_tangent(raw[index, 3:].reshape(3, 2), field, normal,
                                                       minimum_angle=minimum_angle)
    return dict(result, status="returned", selected_event=index, return_time=duration,
        return_state=final, section_tangent=corrected, return_jacobian=corrected[list(axes)],
        return_time_gradient=time_gradient,
        normalized_angle=float(abs(normal @ field)/(np.linalg.norm(normal)*np.linalg.norm(field))),
        section_residual=float(section.value(final)))
