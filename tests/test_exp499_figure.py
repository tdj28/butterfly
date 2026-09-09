"""Saved-result figure guards; never generate target trajectories."""
import json
import pytest
from scripts import plot_exp499_decimal_reference as plot


@pytest.mark.parametrize("value",[{},dict(experiment_id="EXP-499",passed=False),
    dict(experiment_id="EXP-499",passed=True,source_commit="incorrect")])
def test_incomplete_or_unbound_result_cannot_be_plotted(value):
    with pytest.raises(ValueError,match="audited"):
        plot.validate(value)


def test_public_all_input_reference_and_figure_replay_without_integration(monkeypatch):
    def forbidden(*args,**kwargs): pytest.fail("compact replay must not integrate")
    monkeypatch.setattr(plot.run.taylor,"integrate",forbidden)
    root = plot.run.ROOT
    result = json.loads((root/"docs/experiments/receipts/EXP-499-decimal-event-reference-result.json").read_bytes())
    p,old = plot.validate(result)
    rows = plot.values(result,p,old)
    assert len(rows) == 32
    assert sum(not r["original_pair_passed"] for r in rows) == 2
    assert result["target_ivps"] == 64 and result["root_evaluations"] == 480
    assert len(result["ledger"]) == 26
    assert result["reference_qualified"] is True
    assert sum(not r["methods"][0]["within_original_thresholds"] for r in rows) == 2
    assert sum(not r["methods"][1]["within_original_thresholds"] for r in rows) == 1
    assert result["repairs_exp498"] is False and result["symbolic_chains_verified"] is False
    assert plot.verify(root/"docs/figures")
