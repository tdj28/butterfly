"""Prospective screening controls; no new target trajectories in unit tests."""
import json

import numpy as np
import pytest

from butterfly.event_sheet_probe import interval, pair, profile
from butterfly.poincare import PoincareSection
from butterfly.projected_fold_qualification import image_from_census
from scripts import run_exp491_event_sheet_probe as run


@pytest.fixture
def plan():
    return json.loads(run.PLAN.read_bytes())


def sampled(plan, *, jump=False, turn=False, mismatch=None):
    points = []
    for i,u in enumerate((0.,.1,.2)):
        rows = []
        for method in ("DOP853","Radau"):
            t = 1+u*u+(1.01 if jump and i else 0.)
            rows.append(dict(method=method,status="returned",
                events=[dict(time=t,state=[u,0.,0.],tangent=[1.,0.,0.])],
                time_gradients=[2*u],observation=dict(valid=True,
                    input_x_tangent=-1. if turn and i == 1 else 1.,x_graph_slope=u-.1)))
        if mismatch and i == 1:
            if mismatch == "gradient":
                rows[1]["time_gradients"][0] += .01
            else:
                field = {"state":"state","time":"time","tangent":"tangent"}[mismatch]
                if field == "time":
                    rows[1]["events"][0][field] += .01
                else:
                    rows[1]["events"][0][field][0] += .01
        points.append(pair(rows,plan))
    return points


def test_complete_historical_matrix(plan):
    candidates,previous = run.load(plan)
    assert len(candidates) == len(previous["candidates"]) == 26
    assert len({c["family_id"] for c in candidates}) == 16
    assert sum(len(run.sample_values(c))*len(plan["solvers"]) for c in candidates) == 156
    assert all(np.all(np.diff(run.sample_values(c))>0) for c in candidates)


@pytest.mark.parametrize("field",["threshold","hash","method","count"])
def test_manifest_tampering_fails(plan,field):
    if field == "threshold":
        plan["thresholds"]["time_prediction"] = 10.
    elif field == "hash":
        plan["candidates_sha256"] = "0"*64
    elif field == "method":
        plan["solvers"].reverse()
    else:
        plan["limits"]["target_trajectories"] -= 1
    with pytest.raises(ValueError):
        run.load(plan)


def test_nonlinear_time_prediction_and_sampled_turn(plan):
    result = interval(sampled(plan),[0.,.1,.2],plan)
    assert result["screened_regular"] and result["sampled_output_turn"]
    assert max(r["maximum_prediction_residual"] for r in result["solvers"]) < 1e-15


@pytest.mark.parametrize("kind",["jump","turn"])
def test_endpoint_turn_does_not_rescue_cut(plan,kind):
    result = interval(sampled(plan,**{kind:True}),[0.,.1,.2],plan)
    assert result["checks"]["point_numerics"]
    assert all(r["endpoint_output_slope_reversal"] for r in result["solvers"])
    assert not result["screened_regular"] and not result["sampled_output_turn"]
    assert not result["checks"]["time_coherence" if kind == "jump" else "input_sign"]


@pytest.mark.parametrize("field",["state","time","tangent","gradient"])
def test_full_solver_comparison_fails_closed(plan,field):
    points = sampled(plan,mismatch=field)
    assert not points[1]["numeric_qualified"]
    assert not interval(points,[0.,.1,.2],plan)["screened_regular"]


@pytest.mark.parametrize("us",[[0.,.2,.1],[0.,.1,.1],[0.,.1,float("nan")],[0.,.1]])
def test_bad_sample_matrix(plan,us):
    with pytest.raises(ValueError):
        interval(sampled(plan),us,plan)


def test_bad_solver_matrix(plan):
    rows = sampled(plan)[0]["profiles"]
    for bad in (rows[:1],rows[::-1],[rows[0],rows[0]]):
        with pytest.raises(ValueError):
            pair(bad,plan)


def test_uncertainty_just_after_selected_crossing(plan):
    section = PoincareSection((0.,1.,0.),0.,-1)
    rhs = lambda t,q:np.array([0.,-1.,0.])
    events = [dict(time=t,state=[1.,0.,0.],raw_tangent=[1.,0.,0.],
                   accepted=True,angle=1.,residual=0.,bracket=bracket)
              for t,bracket in ((1.,[.5,1.5]),(2.9999,[2.9,3.]))]
    report = dict(method="DOP853",reconstructed=events,ordinary=events,
                  uncertain_extrema=[dict(time=3.)])
    assert image_from_census(report,2,rhs,section,plan["thresholds"])["status"] == "returned"
    result = profile(report,dict(count=2),rhs,section,plan)
    assert result["adjacent_uncertainty"] and result["status"] == "unresolved"
    assert result["time_gradients"] is None
    report["uncertain_extrema"] = []
    assert profile(report,dict(count=2),rhs,section,plan)["status"] == "returned"


def test_missing_event_fails(plan):
    report = dict(method="DOP853",reconstructed=[],ordinary=[],uncertain_extrema=[])
    result = profile(report,dict(count=2),lambda t,q:np.array([0.,-1.,0.]),PoincareSection((0.,1.,0.),0.,-1),plan)
    assert result["status"] == "unresolved"
    assert not pair([result,dict(result,method="Radau")],plan)["numeric_qualified"]


def test_grazing_field_jacobian_and_exact_time_sensitivity():
    rhs,jac = run.grazing_field()
    for z in (.7,2.4,3.,4.8):
        q = np.array([-.0001,2.,z])
        h = 1e-5
        fd = np.column_stack([(rhs(0.,q+h*e)-rhs(0.,q-h*e))/(2*h) for e in np.eye(3)])
        np.testing.assert_allclose(jac(0.,q),fd,rtol=1e-7,atol=2e-7)
    u = -.0001
    t = 3-np.sqrt(-u)
    b = (t-1)*(t-2)*(t-4)*(t-5)
    assert -b/rhs(t,np.array([u,0.,t]))[1] == pytest.approx(1/(2*np.sqrt(-u)),rel=1e-10)


def test_control_matrix_and_exact_tangency_not_assumed_counted():
    specs = run.control_specs()
    assert len(specs) == 8 and sum(len(s["us"])*2 for s in specs) == 48
    assert [s["kind"] for s in specs].count("input-turn") == 2
    assert specs[-1]["us"][1] == 0.
