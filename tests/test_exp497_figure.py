"""Post-freeze visualization guards; no target trajectories."""
import json
import pytest
from scripts import plot_exp497_contact_localization as plot


def test_wrong_figure_input_anchor_precedes_output(tmp_path):
    source = tmp_path/"input.json"
    source.write_text("{}")
    output = tmp_path/"out"
    with pytest.raises(ValueError,match="anchor"):
        plot.build(source,"0"*64,output)
    assert not output.exists()


def test_unqualified_summary_never_becomes_success_figure():
    with pytest.raises(ValueError,match="audited"):
        plot.validate(dict(passed=False))


def test_missing_full_parent_ledger_rejected():
    with pytest.raises(ValueError,match="ledger"):
        plot.validate(dict(passed=True,experiment_id="EXP-497",parent_ledger=[]))


def test_published_localization_replays_without_integrators(monkeypatch):
    def forbidden(*args,**kwargs):
        pytest.fail("saved-result replay attempted a new integration")
    monkeypatch.setattr(plot.run.cycles_run.periodic,"solve_ivp",forbidden)
    monkeypatch.setattr(plot.run.cycles_run.geometry,"solve_ivp",forbidden)
    path = plot.run.ROOT/"docs/experiments/receipts/EXP-497-contact-localization-result.json"
    result = json.loads(path.read_bytes())
    plot.validate(result)
    assert [r["status"] for r in result["rows"]] == ["replace-high","replace-high","proximate","not-run","not-run","not-run"]
    assert result["target_ivps"] == 179
    measured = result["rows"][:3]
    assert sum(len(c["variants"])*6 for r in measured for c in r["result"]["contact"]["rows"]) == 288
    assert result["rows"][2]["result"]["contact"]["envelope"]["pair_state_distance"][3] < 1e-4
    assert not result["symbolic_chains_verified"]
