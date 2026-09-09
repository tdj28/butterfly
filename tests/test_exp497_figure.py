"""Post-freeze visualization guards; no target trajectories."""
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
