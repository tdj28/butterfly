"""Synthetic complete-matrix figure tests; no target access or integration."""
from copy import deepcopy
import json

import pytest

from butterfly.event_sheet_probe import interval,pair
from scripts import plot_exp491_event_sheets as figure


def synthetic():
    plan = json.loads(figure.run.PLAN.read_bytes())
    candidates,previous = figure.run.load(plan)
    rows = []
    for c,old in zip(candidates,previous["candidates"],strict=True):
        us = figure.run.sample_values(c)
        points = []
        for u in us:
            profiles = [dict(method=method,status="returned",reason=None,
                events=[dict(time=float(i+1)+u*u,state=[-3+u,0.,.01],tangent=[1.,0.,0.]) for i in range(c["count"])],
                time_gradients=[2*u]*c["count"],observation=dict(valid=True,input_x_tangent=1.,x_graph_slope=u))
                for method in plan["solvers"]]
            points.append(pair(profiles,plan))
        rows.append(dict(id=c["id"],us=us,points=points,analysis=interval(points,us,plan),prior_fold_qualified=old["qualified"]))
    return dict(experiment_id="EXP-491",status="completed-audited",target_trajectories=156,candidates=rows)


def test_all_samples_families_and_solvers_retained():
    rows = figure.derive(synthetic())
    assert len(rows) == 26 and len({r["family_id"] for r in rows}) == 16
    assert sum(len(r["samples"]) for r in rows) == 156
    assert all([s["method"] for s in r["samples"]] == ["DOP853","Radau"]*3 for r in rows)


@pytest.mark.parametrize("change",["missing","duplicate","solver","paired","interval","coordinate"])
def test_incomplete_or_altered_results_fail(change):
    result = synthetic()
    row = result["candidates"][0]
    if change == "missing":
        result["candidates"].pop()
    elif change == "duplicate":
        result["candidates"][-1] = deepcopy(row)
    elif change == "solver":
        row["points"][0]["profiles"][1]["method"] = "DOP853"
    elif change == "paired":
        row["points"][0]["numeric_qualified"] = False
    elif change == "interval":
        row["analysis"]["screened_regular"] = False
    else:
        row["points"][0]["profiles"][0]["events"][-1]["state"][0] = float("nan")
    with pytest.raises(ValueError):
        figure.derive(result)


def test_unresolved_profiles_have_explicit_unavailable_coordinates():
    result = synthetic()
    plan = json.loads(figure.run.PLAN.read_bytes())
    row = result["candidates"][0]
    for p in row["points"][0]["profiles"]:
        p.update(status="unresolved",events=[],time_gradients=None,observation=dict(valid=False),reason="synthetic gap")
    row["points"][0] = pair(row["points"][0]["profiles"],plan)
    row["analysis"] = interval(row["points"],row["us"],plan)
    rows = figure.derive(result)
    assert len(rows[0]["samples"]) == 6
    assert [s["xy"] for s in rows[0]["samples"][:2]] == [None,None]
    assert not rows[0]["analysis"]["screened_regular"]
