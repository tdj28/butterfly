"""Sampled event-sheet screening, not a continuous-interval certificate."""
import numpy as np

from .projected_fold_qualification import image_from_census
from .return_image_curve import observe_curve


def profile(report, candidate, rhs, section, plan):
    th = plan["thresholds"]
    selected = [e for e in report["reconstructed"] if e["accepted"]][:candidate["count"]]
    image = image_from_census(report,candidate["count"],rhs,section,th)
    # The last crossing can precede an uncertain extremum in its own bracket.
    # Checking only extrema earlier than that crossing misses this case.
    adjacent_uncertainty = any(t["time"] in e["bracket"] for t in report["uncertain_extrema"] for e in selected)
    if adjacent_uncertainty:
        image = dict(status="unresolved",events=[],reason="uncertain extremum adjacent to selected crossing")
    observation = observe_curve(image,minimum_gain=th["minimum_gain"],minimum_x_component=th["minimum_x_component"])
    gradients = None
    if image["status"] == "returned":
        gradients = [-float(np.dot(section.normal,e["raw_tangent"]))/float(np.dot(section.normal,rhs(e["time"],np.asarray(e["state"])))) for e in selected]
    missing = [i for i,e in enumerate(selected) if not any(o["accepted"] and abs(o["time"]-e["time"]) <= th["time"] and np.max(np.abs((np.asarray(o["state"])-e["state"])/plan["scales"])) <= th["state"] for o in report["ordinary"])]
    return dict(method=report["method"],status=image["status"],reason=image.get("reason"),
                events=image["events"],selected_raw=selected,time_gradients=gradients,
                observation=observation,adjacent_uncertainty=adjacent_uncertainty,missing_ordinary_prefix_indices=missing,
                accepted_count=sum(e["accepted"] for e in report["reconstructed"]))


def pair(profiles, plan):
    if len(profiles) != 2 or [r["method"] for r in profiles] != ["DOP853","Radau"]:
        raise ValueError("complete ordered solver pair required")
    errors = []
    if all(r["status"] == "returned" for r in profiles):
        a,b = profiles
        if len(a["events"]) != len(b["events"]):
            raise ValueError("requested prefixes differ")
        for i,(x,y) in enumerate(zip(a["events"],b["events"],strict=True)):
            vx,vy = np.asarray(x["tangent"])/plan["scales"],np.asarray(y["tangent"])/plan["scales"]
            tx,ty = a["time_gradients"][i],b["time_gradients"][i]
            errors.append(dict(state=float(np.max(np.abs((np.asarray(x["state"])-y["state"])/plan["scales"]))),
                time=abs(x["time"]-y["time"]),tangent_relative=float(np.max(np.abs(vx-vy))/max(1.,np.max(np.abs(vx)),np.max(np.abs(vy)))),
                time_gradient_relative=abs(tx-ty)/max(1.,abs(tx),abs(ty))))
    numeric = bool(errors) and all(e[k] <= plan["thresholds"][k] for e in errors for k in ("state","time","tangent_relative","time_gradient_relative"))
    return dict(numeric_qualified=bool(numeric),projection_qualified=bool(numeric and all(r["observation"]["valid"] for r in profiles)),errors=errors,profiles=profiles)


def interval(points, us, plan):
    if len(points) != 3 or len(us) != 3 or not np.isfinite(us).all() or not np.all(np.diff(us)>0):
        raise ValueError("three ordered sample points required")
    rows = []
    for method_index,method in enumerate(("DOP853","Radau")):
        profiles = [p["profiles"][method_index] for p in points]
        if any(r["method"] != method for r in profiles):
            raise ValueError("interval solver identity differs")
        obs = [r["observation"] for r in profiles]
        dx = [r.get("input_x_tangent") for r in obs]
        signs_kept = all(x is not None and x != 0 for x in dx) and len({np.sign(x) for x in dx}) == 1
        endpoints_reverse = None if not all(obs[i]["valid"] for i in (0,2)) else bool(obs[0]["x_graph_slope"]*obs[2]["x_graph_slope"] < 0)
        comparisons = []
        if all(r["status"] == "returned" for r in profiles):
            for half in (0,1):
                a,b = profiles[half:half+2]
                if len(a["events"]) != len(b["events"]):
                    raise ValueError("interval requested prefixes differ")
                for i,(x,y) in enumerate(zip(a["events"],b["events"],strict=True)):
                    dt = y["time"]-x["time"]
                    predicted = .5*(a["time_gradients"][i]+b["time_gradients"][i])*(us[half+1]-us[half])
                    comparisons.append(dict(half=half,event_index=i,time_change=dt,predicted_change=predicted,prediction_residual=dt-predicted))
        max_time = max((abs(c["time_change"]) for c in comparisons),default=None)
        max_prediction = max((abs(c["prediction_residual"]) for c in comparisons),default=None)
        time_coherent = max_time is not None and max_time <= plan["thresholds"]["adjacent_time"] and max_prediction <= plan["thresholds"]["time_prediction"]
        rows.append(dict(method=method,input_sign_kept=bool(signs_kept),endpoint_output_slope_reversal=endpoints_reverse,
                         time_coherent=bool(time_coherent),maximum_time_change=max_time,maximum_prediction_residual=max_prediction,time_comparisons=comparisons))
    checks = dict(point_numerics=all(p["numeric_qualified"] for p in points),point_projection=all(p["projection_qualified"] for p in points),
                  input_sign=all(r["input_sign_kept"] for r in rows),time_coherence=all(r["time_coherent"] for r in rows))
    regular = all(checks.values())
    return dict(screened_regular=regular,status="screened-regular" if regular else "cut-required-or-unresolved",checks=checks,solvers=rows,
                sampled_output_turn=bool(regular and all(r["endpoint_output_slope_reversal"] for r in rows)))
