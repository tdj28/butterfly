"""Synthetic whole-matrix figure tests; no real target access or integration."""
from copy import deepcopy
import json

import numpy as np
import pytest

from butterfly.event_boundary_shooting import assess
from scripts import plot_exp492_event_boundaries as figure


def synthetic():
    p = json.loads(figure.run.PLAN.read_bytes())
    table,_ = figure.run.load(p)
    rows = []
    for c in table["intervals"]:
        a = None
        if c["status"] == "nominated":
            t,u = c["seed_time"],c["seed_u"]
            root = dict(u=u,time=t,state=[0.,0.,t],residual=[0.,0.],jacobian=[[2.,0.],[0.,-2.]])
            roots = [dict(method=m,shooting=dict(converged=True,trace=[deepcopy(root)])) for m in p["solvers"]]
            sides = []
            for dose in c["doses"]:
                initial = u+dose
                effective = initial-u
                events = [dict(time=.1*(j+1),accepted=True,state=[0.,0.,.1*(j+1)],residual=0.,angle=.1,bracket=[.1*j,.1*(j+2)]) for j in range(c["accepted_prefix"])]
                if effective > 0:
                    dt = np.sqrt(2*effective)
                    events += [dict(time=t+sign*dt,accepted=sign == 1,state=[0.,0.,t+sign*dt],residual=0.,angle=.1,bracket=[t-.1,t+.1]) for sign in (-1,1)]
                sides.append(dict(dose=dose,u=initial,reports=[dict(method=m,reconstructed=deepcopy(events),uncertain_extrema=[]) for m in p["solvers"]]))
            a = assess(roots,sides,c,p)
            assert a["qualified"]
        rows.append(dict(id=c["id"],family_id=c["family_id"],case=c["case"],region=c["region"],selection_status=c["status"],analysis=a))
    return dict(experiment_id="EXP-492",status="completed-audited",target_integrations=160,intervals=rows)


def test_all_nominated_conditions_and_solvers_retained():
    rows = figure.derive(synthetic())
    assert len(rows) == 16 and len({r["family_id"] for r in rows}) == 10
    assert sum(len(r["samples"]) for r in rows) == 128
    assert all(r["qualified"] for r in rows)


@pytest.mark.parametrize("change",["missing","duplicate","unselected","solver","dose","event","verdict","ratio","paired"])
def test_missing_or_changed_figure_evidence_rejected(change):
    result = synthetic()
    r = next(r for r in result["intervals"] if r["analysis"] is not None)
    if change == "missing":
        result["intervals"].pop()
    elif change == "duplicate":
        result["intervals"][-1] = deepcopy(r)
    elif change == "unselected":
        next(v for v in result["intervals"] if v["analysis"] is None)["analysis"] = deepcopy(r["analysis"])
    elif change == "solver":
        r["analysis"]["solvers"].pop()
    elif change == "dose":
        r["analysis"]["solvers"][0]["sides"].pop()
    elif change == "event":
        r["analysis"]["solvers"][0]["sides"][-1]["local_roots"][0]["time"] += .001
    elif change == "verdict":
        r["analysis"]["qualified"] = False
    elif change == "ratio":
        r["analysis"]["solvers"][0]["square_root_ratio"] = 100.
    else:
        r["analysis"]["paired_sides"][0]["passed"] = False
    with pytest.raises(ValueError):
        figure.derive(result)


def test_failed_root_panel_is_retained():
    result = synthetic()
    r = next(r for r in result["intervals"] if r["analysis"] is not None)
    r["analysis"] = dict(qualified=False,roots=dict(eligible=False),solvers=[],paired_sides=[])
    rows = figure.derive(result)
    assert len(rows) == 16 and rows[0]["samples"] == [] and rows[0]["reference"] is None


def test_failed_side_points_are_retained():
    result = synthetic()
    a = next(r["analysis"] for r in result["intervals"] if r["analysis"] is not None)
    s = a["solvers"][0]
    v = s["sides"][-1]
    v["prefix_uncertainty"] = [dict(time=.01)]
    v["passed"] = s["passed"] = a["qualified"] = False
    rows = figure.derive(result)
    assert not rows[0]["qualified"] and len(rows[0]["samples"]) == 8
    assert sum(not s["side_passed"] for s in rows[0]["samples"]) == 2
