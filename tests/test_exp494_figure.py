"""Prospective synthetic checks that the figure cannot drop stopped arms."""
from copy import deepcopy

import pytest

from scripts import run_exp494_periodic_winding_transport as run
from scripts import plot_exp494_periodic_transport as plot
from test_exp494_transport import fake_profile, parents


def fixture():
    p = run.load_plan()
    def execute(spec,method,seed):
        r = fake_profile(method)
        r["correction_gate"] = dict(passed=True)
        for w in r["metric"]["windows"]:
            w["geometry"] = dict(midpoint_enriched=dict(cut_index=1))
            w["conditional_minimal_period"] = True
        if spec["arm"] == "a-" and spec["step"] == 2:
            r["qualified"] = False
        return r
    return dict(experiment_id="EXP-494",source_commit="4e5054955e8ddeb9db94e4702fe78d6232eda303",
        rows=run.campaign(p,parents(p),execute),saved_profiles=[{} for _ in range(8)],symbolic_chains_verified=False)


def test_full_grid_retains_every_failed_and_blocked_node():
    rows = plot.derive(fixture())
    assert len(rows) == 66
    assert sum(r["status"] == "unqualified" for r in rows) == 2
    assert sum(r["status"] == "not-run" for r in rows) == 12
    assert len([r for r in rows if r["spec"]["step"] > 0]) == 64


@pytest.mark.parametrize("change", ["missing", "duplicated", "false-pass", "claim", "source"])
def test_figure_rejects_incomplete_or_relabelled_evidence(change):
    s = fixture()
    if change == "missing":
        s["rows"].pop()
    elif change == "duplicated":
        s["rows"][1] = deepcopy(s["rows"][0])
    elif change == "false-pass":
        s["rows"][2]["status"] = "qualified"
    elif change == "claim":
        s["symbolic_chains_verified"] = True
    else:
        s["source_commit"] = "0"*40
    with pytest.raises(ValueError):
        plot.derive(s)
