"""Fixed-time shooting for a section tangency, not a projected return fold."""
import numpy as np
from scipy.integrate import solve_ivp


def grazing_equations(state, tangent, field, jacobian, normal, offset):
    q, w, f, j, n = map(np.asarray, (state, tangent, field, jacobian, normal))
    residual = np.array([n@q-offset, n@f])
    matrix = np.array([[n@w, n@f], [n@j@w, n@j@f]])
    if not np.isfinite(residual).all() or not np.isfinite(matrix).all():
        raise ValueError("nonfinite grazing equations")
    return residual, matrix


def shoot(rhs, jacobian, initial, tangent, section, seed_time, *, method, plan, retain):
    """Solve h(delta,t)=h_t(delta,t)=0 using fixed-time IVPs and bounded Newton.

    No division by the vanishing section velocity is used. Every IVP is
    retained by the caller before a verdict; a failed iterate is not retried.
    """
    q0, v = np.asarray(initial), np.asarray(tangent)
    delta, end = 0., float(seed_time)
    trace = []
    for iteration in range(plan["newton_iterations"]):
        def augmented(t, q):
            return np.r_[rhs(t, q[:3]), jacobian(t, q[:3])@q[3:]]
        sol = solve_ivp(augmented, (0., end), np.r_[q0+delta*v, v],
                        method=method, **{k:plan[k] for k in ("rtol", "atol", "max_step")})
        retain(iteration, dict(integration_times=sol.t, integration_augmented_states=sol.y.T))
        if not sol.success or not np.isfinite(sol.y).all():
            return dict(converged=False, reason="integration failed", trace=trace)
        state, w = sol.y[:3,-1], sol.y[3:,-1]
        residual, matrix = grazing_equations(state, w, rhs(end,state), jacobian(end,state), section.normal, section.offset)
        row = dict(iteration=iteration, delta=delta, time=end, state=state.tolist(), raw_tangent=w.tolist(),
                   residual=residual.tolist(), jacobian=matrix.tolist())
        trace.append(row)
        if abs(residual[0]) <= plan["root_plane"] and abs(residual[1]) <= plan["root_velocity"]:
            return dict(converged=True, reason="residual tolerances", trace=trace)
        try:
            step = np.linalg.solve(matrix, residual)
        except np.linalg.LinAlgError:
            return dict(converged=False, reason="singular Newton matrix", trace=trace)
        row["newton_step"] = step.tolist()
        delta, end = float(delta-step[0]), float(end-step[1])
        if abs(delta) > plan["delta_bound"] or abs(end-seed_time) > plan["time_bound"] or end <= 0:
            return dict(converged=False, reason="prospective search box exceeded", trace=trace)
    return dict(converged=False, reason="iteration limit", trace=trace)


def side_verdict(report, root, dose, plan):
    local = [e for e in report["reconstructed"] if abs(e["time"]-root["time"]) < plan["window"]]
    uncertain = [e for e in report["uncertain_extrema"] if abs(e["time"]-root["time"]) < plan["window"]]
    matrix = np.asarray(root["jacobian"])
    expected = 2 if matrix[0,0]*dose*matrix[1,1] < 0 else 0
    before = [e for e in report["reconstructed"] if e["accepted"] and e["time"] <= root["time"]-plan["window"]]
    after = [e for e in report["reconstructed"] if e["accepted"] and e["time"] > root["time"]-plan["window"]]
    passed = len(local) == expected and sum(e["accepted"] for e in local) == expected//2 and not uncertain
    passed &= len(before) == plan["accepted_prefix"]
    passed &= all(abs(e["residual"]) <= plan["side_residual"] and e["angle"] >= plan["minimum_angle"] for e in local)
    return dict(dose=dose, expected_roots=expected, local_roots=local, uncertain_extrema=uncertain,
                accepted_prefix_count=len(before), next_accepted=after[0] if after else None,
                separation=local[1]["time"]-local[0]["time"] if len(local) == 2 else None, passed=bool(passed))
