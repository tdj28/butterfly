import copy
import json

import numpy as np
import pytest

from scripts import run_exp488_event_accuracy as run


def fixture():
    plan = json.loads(run.PLAN.read_bytes())
    events = [dict(time=float(i+1), state=[-float(i+1), 0., .01], accepted=True, angle=1., residual=0.) for i in range(5)]
    rows = [dict(method=m, rtol=r, atol=a, ordinary=copy.deepcopy(events),
                 reconstructed=copy.deepcopy(events), uncertain_extrema=[])
            for m, _, r, a in run.profiles(plan)]
    selection = dict(case="synthetic", prior_fifth={"Radau":copy.deepcopy(events[4])})
    return rows, selection, plan


def test_complete_fine_pair_matrix_and_coarse_reference_not_truth():
    rows, s, p = fixture()
    s["prior_fifth"]["Radau"]["state"][2] += .001
    rows[0]["reconstructed"][0]["state"][2] += 1e-7
    result = run.compare(rows, s, p)
    assert result["passed"]
    assert len(result["fine_pairs"]) == 6
    assert result["profiles"][0]["reference_errors"][0]["state"] > 1e-6
    assert result["profiles"][0]["old_radau_fifth_error"][0]["state"] > .01


@pytest.mark.parametrize("failure", ["count", "uncertain", "state", "time", "angle", "nan"])
def test_failures_are_not_qualified(failure):
    rows, s, p = fixture()
    event = rows[1]["reconstructed"][0]
    if failure == "count":
        rows[0]["reconstructed"].pop()
    elif failure == "uncertain":
        rows[0]["uncertain_extrema"] = [dict(time=.5)]
    elif failure == "state":
        event["state"][2] += 2e-9
    elif failure == "time":
        event["time"] += 2e-9
    elif failure == "angle":
        event["angle"] = 0.
    else:
        event["state"][0] = np.nan
    assert not run.compare(rows, s, p)["passed"]


def test_duplicate_arm_rejected():
    rows, s, p = fixture()
    rows[-1] = rows[0]
    with pytest.raises(ValueError, match="matrix"):
        run.compare(rows, s, p)


def test_self_consistent_reduced_plan_rejected():
    _, _, p = fixture()
    run.validate_plan(p)
    p["cases"].pop()
    p["limits"]["target_integrations"] = 6
    with pytest.raises(ValueError, match="matrix"):
        run.validate_plan(p)


def test_nonlinear_rotation_analytic_control():
    _, _, p = fixture()
    t = 2*np.pi*np.arange(1,3)
    row = dict(reconstructed=[dict(time=float(x), state=[-4-.25*(1-np.exp(-.06*x)),0.,.5*np.exp(-.03*x)], accepted=True) for x in t], uncertain_extrema=[])
    assert run.control_verdict(row, p)["passed"]
    row["reconstructed"][1]["state"][2] += 1e-6
    assert not run.control_verdict(row, p)["passed"]
