"""Post-freeze visualization controls; no target integrations."""
import json
import sys
import pytest
from scripts import plot_exp498_boundary_transport as plot


@pytest.mark.parametrize("value",[{},dict(experiment_id="EXP-498",passed=False),
    dict(experiment_id="EXP-498",passed=True,source_commit="wrong-source")])
def test_incomplete_or_unbound_result_cannot_be_plotted(value):
    with pytest.raises(ValueError,match="audited"):
        plot.validate(value)


def test_plotted_rows_keep_failures_and_all_event_indices():
    data = dict(rows=[dict(id="empty",predecessors=[],geometry=dict(analysis=None)),
        dict(id="failed",geometry=dict(analysis=dict(qualified=False)),predecessors=[
            dict(eligible=True,event=dict(state=[1.,2.,3.]),windows=[dict(state_distances=[1.,2.,3.,4.,5.,6.]),
                dict(state_distances=[6.,5.,4.,3.,2.,1.])])])])
    assert plot.plot_rows(data) == [dict(id="empty",qualified=False,states=[],worst_distances=None),
        dict(id="failed",qualified=False,states=[[1.,2.,3.]],worst_distances=[6.,5.,4.,4.,5.,6.])]


def test_public_result_replays_without_integrating(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("saved-result replay must not integrate")

    for module in list(sys.modules.values()):
        if module is not None and "solve_ivp" in vars(module):
            monkeypatch.setattr(module, "solve_ivp", forbidden)
    result = json.loads((plot.run.ROOT / "docs/experiments/receipts/EXP-498-boundary-transport-result.json").read_bytes())
    plot.validate(result)
    assert plot.verify(plot.run.ROOT / "docs/figures")
    assert len(result["ledger"]) == 26
    assert len(result["rows"]) == 8
    assert result["target_ivps"] == 136
    assert result["diagnostic"]["predecessors"] == 64
    assert result["diagnostic"]["comparison_cells"] == 768
    assert sum(row["qualified"] for row in plot.plot_rows(result)) == 6
    assert result["symbolic_chains_verified"] is False
    assert result["diagnostic"]["ordering"] == "unresolved"
    old_failures = [r for r in result["rows"] if not r["parent_qualified"]]
    assert len(old_failures) == 1
    assert old_failures[0]["geometry"]["analysis"]["qualified"] is False
