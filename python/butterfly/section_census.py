"""Numerical section-root census bracketed by normal-velocity extrema.

Extrema are themselves detected numerically: this is not an all-root proof.
The ordinary solver event list is retained separately, never silently edited.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq


def collect(rhs, jacobian, initial, tangent, section, *, method="DOP853", max_step=.02,
            horizon=50., guard=1e-8, rtol=1e-10, atol=1e-12,
            extremum_margin=1e-10, first_step=None):
    initial, tangent = np.asarray(initial, float), np.asarray(tangent, float)
    if initial.shape != (3,) or tangent.shape != (3,) or not np.isfinite([*initial, *tangent]).all():
        raise ValueError("finite three-dimensional state/tangent required")
    if method not in ("DOP853", "Radau") or not 0 <= guard < horizon or min(max_step, rtol, atol, extremum_margin) <= 0:
        raise ValueError("invalid bounded census")
    n = np.asarray(section.normal)
    def augmented(t, q):
        return np.r_[rhs(t, q[:3]), np.asarray(jacobian(t, q[:3])) @ q[3:]]
    def plane(t, q):
        return section.value(q[:3])
    def extremum(t, q):
        return float(n @ rhs(t, q[:3]))
    for callback in (plane, extremum):
        callback.direction, callback.terminal = 0, False
    config = dict(method=method, rtol=rtol, atol=atol, max_step=max_step)
    start = np.r_[initial, tangent]
    if guard:
        prefix = solve_ivp(augmented, (0., guard), start, **config)
        if not prefix.success or not np.isfinite(prefix.y).all():
            raise ValueError("guard integration failed")
        start = prefix.y[:, -1]
    solution = solve_ivp(augmented, (guard, horizon), start, events=(plane, extremum),
                         dense_output=True, first_step=first_step, **config)
    if not solution.success or not np.isfinite(solution.y).all():
        raise ValueError("census integration failed")
    knots = np.unique(np.r_[guard, solution.t_events[1], horizon])
    values = np.array([plane(t, solution.sol(t)) for t in knots])
    uncertain = [dict(time=float(t), plane_value=float(plane(t, q)), state=q[:3].tolist())
                 for t, q in zip(solution.t_events[1], solution.y_events[1], strict=True)
                 if abs(plane(t, q)) <= extremum_margin]
    roots, brackets = [], []
    for left, right, a, b in zip(knots[:-1], knots[1:], values[:-1], values[1:], strict=True):
        if a*b < 0:
            root = brentq(lambda t: plane(t, solution.sol(t)), left, right, xtol=1e-12, rtol=1e-14)
            roots.append(root)
            brackets.append([float(left), float(right)])
    def record(t, value):
        q = np.asarray(value)[:3]
        f = np.asarray(rhs(float(t), q))
        velocity = float(n @ f)
        angle = abs(velocity)/(np.linalg.norm(n)*np.linalg.norm(f))
        return dict(time=float(t), state=q.tolist(), raw_tangent=np.asarray(value)[3:].tolist(),
                    normal_velocity=velocity, angle=float(angle), residual=section.value(q),
                    accepted=bool(section.accepts(q) and section.direction*velocity > 0))
    ordinary = [record(t, q) for t, q in zip(solution.t_events[0], solution.y_events[0], strict=True)]
    reconstructed = [dict(record(t, solution.sol(t)), bracket=interval)
                     for t, interval in zip(roots, brackets, strict=True)]
    extrema = [dict(record(t, q), plane_value=plane(t, q))
               for t, q in zip(solution.t_events[1], solution.y_events[1], strict=True)]
    report = dict(method=method, max_step=max_step, rtol=rtol, atol=atol, horizon=horizon, guard=guard,
                  initial_state=initial.tolist(), initial_tangent=tangent.tolist(),
                  ordinary=ordinary, reconstructed=reconstructed, extrema=extrema,
                  uncertain_extrema=uncertain, knots=knots.tolist(), knot_values=values.tolist(),
                  nfev=solution.nfev, njev=solution.njev, numerical_all_root_proof=False)
    return report, dict(integration_times=solution.t, integration_augmented_states=solution.y.T)
