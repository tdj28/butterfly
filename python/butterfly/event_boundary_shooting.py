"""Bounded grazing roots and common-input two-sided event checks."""
import numpy as np
from scipy.integrate import solve_ivp

from .section_grazing import grazing_equations,side_verdict


def shoot(rhs,jac,section,c,p,method,retain,before_integrate=None):
    q0,v = np.asarray(c["initial_state"]),np.asarray(c["initial_tangent"])
    u,end = c["seed_u"],c["seed_time"]
    trace = []
    for iteration in range(p["newton_iterations"]):
        if before_integrate is not None:
            before_integrate()
        def augmented(t,q):
            return np.r_[rhs(t,q[:3]),jac(t,q[:3])@q[3:]]
        sol = solve_ivp(augmented,(0.,end),np.r_[q0+u*v,v],method=method,
                        **{k:p[k] for k in ("rtol","atol","max_step")})
        retain(iteration,dict(integration_times=sol.t,integration_augmented_states=sol.y.T))
        row = dict(iteration=iteration,u=u,time=end,reached_time=float(sol.t[-1]),
                   solver_success=bool(sol.success),state=sol.y[:3,-1].tolist(),raw_tangent=sol.y[3:,-1].tolist())
        trace.append(row)
        if not sol.success or not np.isfinite(sol.y).all():
            return dict(converged=False,reason="integration failed",trace=trace)
        q,w = sol.y[:3,-1],sol.y[3:,-1]
        residual,matrix = grazing_equations(q,w,rhs(end,q),jac(end,q),section.normal,section.offset)
        row.update(residual=residual.tolist(),jacobian=matrix.tolist())
        if abs(residual[0]) <= p["root_plane"] and abs(residual[1]) <= p["root_velocity"]:
            return dict(converged=True,reason="residual tolerances",trace=trace)
        try:
            step = np.linalg.solve(matrix,residual)
        except np.linalg.LinAlgError:
            return dict(converged=False,reason="singular Newton matrix",trace=trace)
        row["newton_step"] = step.tolist()
        u,end = float(u-step[0]),float(end-step[1])
        if not c["u_box"][0] <= u <= c["u_box"][1] or not c["time_box"][0] <= end <= c["time_box"][1] or end <= 0:
            return dict(converged=False,reason="prospective search box exceeded",trace=trace)
    return dict(converged=False,reason="iteration limit",trace=trace)


def root_pair(rows,c,p):
    if len(rows) != 2 or [r["method"] for r in rows] != ["DOP853","Radau"]:
        raise ValueError("complete ordered root pair required")
    checks = []
    roots = [r["shooting"]["trace"][-1] if r["shooting"]["trace"] else None for r in rows]
    for r,q in zip(rows,roots,strict=True):
        checks.append(bool(r["shooting"]["converged"] and q is not None
            and c["u_box"][0] <= q["u"] <= c["u_box"][1] and c["time_box"][0] <= q["time"] <= c["time_box"][1]
            and abs(q["residual"][0]) <= p["root_plane"] and abs(q["residual"][1]) <= p["root_velocity"]
            and abs(q["jacobian"][0][0]) >= p["minimum_unfolding"] and abs(q["jacobian"][1][1]) >= p["minimum_curvature"]))
    agreement,center = None,None
    if all(checks):
        a,b = roots
        agreement = dict(u=abs(a["u"]-b["u"]),time=abs(a["time"]-b["time"]),
            scaled_state=float(np.max(np.abs((np.asarray(a["state"])-b["state"])/p["scales"]))))
        if all(agreement[k] <= p["solver_"+k] for k in agreement):
            center = (a["u"]+b["u"])/2.
    inside = center is not None and all(c["u_box"][0] <= center+d <= c["u_box"][1] for d in c["doses"])
    return dict(root_checks=checks,agreement=agreement,common_center_u=center,side_inputs_inside=bool(inside),eligible=bool(inside))


def assess(rows,sides,c,p):
    roots = root_pair(rows,c,p)
    if not roots["eligible"]:
        if sides:
            raise ValueError("unqualified root pair must not have side targets")
        return dict(qualified=False,roots=roots,solvers=[],paired_sides=[],reason="root pair or side-box gate failed")
    if len(sides) != 4 or [s["dose"] for s in sides] != c["doses"] or any([r["method"] for r in s["reports"]] != ["DOP853","Radau"] for s in sides):
        raise ValueError("complete four-dose/two-solver side matrix required")
    verdicts = []
    for j,r in enumerate(rows):
        root = r["shooting"]["trace"][-1]
        local = []
        for side in sides:
            actual_u = roots["common_center_u"]+side["dose"]
            if side["u"] != actual_u:
                raise ValueError("shared side-input center differs")
            effective = actual_u-root["u"]
            report = side["reports"][j]
            v = side_verdict(report,root,effective,dict(p,accepted_prefix=c["accepted_prefix"]))
            prefix_uncertainty = [e for e in report["uncertain_extrema"] if e["time"] <= root["time"]+p["window"]
                or any(e["time"] in r["bracket"] for r in v["local_roots"])]
            v.update(prefix_uncertainty=prefix_uncertainty,passed=bool(v["passed"] and not prefix_uncertainty))
            local.append(dict(v,nominal_dose=side["dose"],u=actual_u))
        pairs = sorted([v for v in local if v["expected_roots"] == 2],key=lambda v:abs(v["nominal_dose"]))
        ratio = pairs[1]["separation"]/pairs[0]["separation"] if len(pairs) == 2 and all(v["separation"] is not None and v["separation"] > 0 for v in pairs) else None
        passed = all(v["passed"] for v in local) and ratio is not None and abs(ratio/np.sqrt(10)-1) <= p["square_root_ratio_relative_error"]
        verdicts.append(dict(method=r["method"],passed=bool(passed),root=root,sides=local,square_root_ratio=ratio))
    comparisons = []
    for s in sides:
        a,b = [[e for e in r["reconstructed"] if e["accepted"]] for r in s["reports"]]
        errors = []
        if len(a) == len(b):
            errors = [dict(time=abs(x["time"]-y["time"]),scaled_state=float(np.max(np.abs((np.asarray(x["state"])-y["state"])/p["scales"])))) for x,y in zip(a,b,strict=True)]
        passed = len(a) == len(b) and all(e["time"] <= p["side_solver_time"] and e["scaled_state"] <= p["side_solver_scaled_state"] for e in errors)
        comparisons.append(dict(dose=s["dose"],u=s["u"],counts=[len(a),len(b)],errors=errors,passed=bool(passed)))
    return dict(qualified=bool(all(v["passed"] for v in verdicts) and all(v["passed"] for v in comparisons)),roots=roots,solvers=verdicts,paired_sides=comparisons,reason=None)
