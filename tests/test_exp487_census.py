import copy
import json

import pytest

from scripts import run_exp487_section_census as run


def fixture():
    plan = json.loads(run.PLAN.read_bytes())
    events = [dict(time=float(i+1), state=[-float(i+1), 0., 0.], accepted=True, angle=1., residual=0.) for i in range(5)]
    rows = [dict(method=m, max_step=h, ordinary=copy.deepcopy(events[:4]),
                 reconstructed=copy.deepcopy(events), uncertain_extrema=[])
            for m in plan["solvers"] for h in plan["max_steps"]]
    selection = dict(case="synthetic", prior_fifth={"Radau": copy.deepcopy(events[-1])})
    return rows, selection, plan


def test_missing_ordinary_event_recovered_without_discarding_profiles():
    rows, selection, plan = fixture()
    result = run.compare(rows, selection, plan)
    assert result["passed"]
    assert len(result["comparisons"]) == 6
    assert all(r["missing_ordinary_indices"] == [4] for r in result["comparisons"])


@pytest.mark.parametrize("failure", ["missing", "extra", "uncertain", "state", "witness"])
def test_failure_remains_unqualified(failure):
    rows, selection, plan = fixture()
    if failure == "missing":
        rows[0]["reconstructed"].pop()
    elif failure == "extra":
        rows[0]["reconstructed"].append(dict(rows[0]["reconstructed"][-1], time=6.))
    elif failure == "uncertain":
        rows[0]["uncertain_extrema"] = [dict(time=.5)]
    elif failure == "state":
        rows[0]["reconstructed"][0]["state"][0] += .001
    else:
        selection["prior_fifth"]["Radau"]["time"] += 1.
    assert not run.compare(rows, selection, plan)["passed"]


def test_profile_matrix_cannot_shrink_or_duplicate():
    rows, selection, plan = fixture()
    rows[-1] = rows[0]
    with pytest.raises(ValueError, match="matrix"):
        run.compare(rows, selection, plan)
