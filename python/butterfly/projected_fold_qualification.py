"""Event-ordinal and finite-difference qualification of direct fold shootings."""
import numpy as np

from .return_geometry import event_corrected_tangent
from .return_image_curve import observe_curve


def image_from_census(report, count, rhs, section, thresholds):
    selected = [e for e in report["reconstructed"] if e["accepted"]][:count]
    if len(selected) != count or any(e["time"] <= selected[-1]["time"] for e in report["uncertain_extrema"]):
        return dict(status="unresolved",events=[],reason="missing event or uncertain preceding extremum")
    events = []
    for e in selected:
        if e["angle"] < thresholds["angle"] or abs(e["residual"]) > thresholds["plane"]:
            return dict(status="unresolved",events=events,reason="invalid transverse section event")
        corrected,_ = event_corrected_tangent(np.asarray(e["raw_tangent"])[:,None],rhs(e["time"],np.asarray(e["state"])),section.normal,minimum_angle=thresholds["angle"])
        events.append(dict(time=e["time"],state=e["state"],tangent=corrected[:,0].tolist()))
    return dict(status="returned",events=events)


def qualify(shooting, censuses, candidate, rhs, section, plan):
    if not shooting["converged"]:
        return dict(qualified=False,reason=shooting["reason"])
    root = shooting["trace"][-1]
    if len(censuses) != 3:
        return dict(qualified=False,reason="missing prescribed censuses")
    eps = candidate["epsilon"]
    if [c["offset"] for c in censuses] != [-eps,0.,eps]:
        raise ValueError("census displacement matrix differs")
    th = plan["thresholds"]
    images = [image_from_census(c["report"],candidate["count"],rhs,section,th) for c in censuses]
    observations = [observe_curve(r,minimum_gain=th["minimum_gain"],minimum_x_component=th["minimum_x_component"]) for r in images]
    if any(not o["valid"] for o in observations) or "event_second_derivative" not in root:
        return dict(qualified=False,reason="invalid event/input projection",observations=observations)
    center = images[1]["events"][-1]
    state_error = float(np.max(np.abs((np.asarray(center["state"])-root["state"])/plan["scales"])))
    time_error = abs(center["time"]-root["time"])
    curvature = root["event_second_derivative"]
    fd = (images[2]["events"][-1]["tangent"][0]-images[0]["events"][-1]["tangent"][0])/(2*eps)
    fd_error = abs(fd-curvature)/max(1.,abs(curvature))
    input_dx = images[1]["events"][-2]["tangent"][0]
    scaled_curvature = 15*curvature/input_dx**2
    sign_kept = len({np.sign(o["input_x_tangent"]) for o in observations}) == 1
    opposite = observations[0]["x_graph_slope"]*observations[2]["x_graph_slope"] < 0
    checks = dict(event_state=state_error <= th["state"],event_time=time_error <= th["time"],
                  fixed_input_projection=bool(sign_kept),opposite_slopes=bool(opposite),
                  center_derivative=abs(observations[1]["normalized_output_derivative"]) <= th["root_derivative"],
                  finite_difference=fd_error <= th["curvature_relative_error"],
                  nondegenerate=abs(scaled_curvature) >= th["minimum_scaled_curvature"])
    return dict(qualified=bool(all(checks.values())),checks=checks,observations=observations,
                root=root,event_state_error=state_error,event_time_error=time_error,
                event_second_derivative=curvature,finite_difference_second_derivative=fd,
                finite_difference_relative_error=fd_error,scaled_curvature=scaled_curvature,
                center_event_times=[e["time"] for e in images[1]["events"][-2:]],
                in_region=bool(candidate["old_x_interval"][0] <= observations[1]["image_state"][0] <= candidate["old_x_interval"][1]))


def compare(candidate, rows, plan):
    if len(rows) != 2 or [r["method"] for r in rows] != ["DOP853","Radau"]:
        raise ValueError("complete two-solver matrix required")
    agreement = None
    if all(r["qualification"]["qualified"] for r in rows):
        a,b = [r["qualification"] for r in rows]
        states = [float(np.max(np.abs((np.asarray(a["observations"][1][k])-b["observations"][1][k])/plan["scales"]))) for k in ("image_state","next_state")]
        times = [abs(x-y) for x,y in zip(a["center_event_times"],b["center_event_times"],strict=True)]
        agreement = dict(u=abs(a["root"]["u"]-b["root"]["u"]),states=states,times=times)
    passed = agreement is not None and agreement["u"] <= plan["thresholds"]["solver_u"] and max(agreement["states"]) <= plan["thresholds"]["state"] and max(agreement["times"]) <= plan["thresholds"]["time"]
    return dict(id=candidate["id"],family_id=candidate["family_id"],case=candidate["case"],region=candidate["region"],
                qualified=bool(passed),qualified_in_region=bool(passed and all(r["qualification"]["in_region"] for r in rows)),
                agreement=agreement,solvers=[dict(method=r["method"],**r["qualification"]) for r in rows])
