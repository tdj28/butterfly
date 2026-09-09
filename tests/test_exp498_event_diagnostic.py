"""Algebra controls and full public saved-event diagnostic replay."""
import json
import numpy as np
import pytest
from scripts import diagnose_exp498_event_disagreement as diagnostic


def test_exact_constant_velocity_phase_and_transverse_remainder():
    a = dict(time=2., state=[4., 6., 8.])
    b = dict(time=1., state=[2., 3., 4.])
    result = diagnostic.decompose(a, b, lambda q: [2., 3., 4.], np.ones(3))
    assert result["remainder"] == [0., 0., 0.]
    a["state"][0] += 1.
    result = diagnostic.decompose(a, b, lambda q: [2., 3., 4.], np.ones(3))
    assert result["remainder"] == [1., 0., 0.]
    assert result["scaled_remainder"] == 1.


def test_zero_normal_velocity_is_not_divided():
    event = dict(time=1., state=[1., 2., 3.])
    value = diagnostic.decompose(event, event, lambda q: [1., 0., 1.], np.ones(3))
    assert value["normal_to_z_amplification"] is None


def test_complete_saved_diagnostic_retains_two_failures(monkeypatch):
    from butterfly import event_boundary_shooting, section_census, section_grazing
    def forbidden(*args, **kwargs):
        pytest.fail("saved-event diagnostic must not integrate")
    for module in (event_boundary_shooting, section_census, section_grazing):
        monkeypatch.setattr(module, "solve_ivp", forbidden)
    root = diagnostic.plot.run.ROOT
    path = root / "docs/experiments/receipts/EXP-498-boundary-transport-result.json"
    source = json.loads(path.read_bytes())
    report = diagnostic.diagnose(source)
    published = json.loads((root / "docs/experiments/receipts/EXP-498-event-disagreement-diagnostic.json").read_bytes())
    assert report == published
    assert len(report["rows"]) == 32
    expected = sum(len([e for e in side["reports"][0]["reconstructed"] if e["accepted"]])
                   for row in source["rows"] for side in row["boundary"]["sides"])
    assert sum(len(row["pairs"]) for row in report["rows"]) == expected
    failures = [p for row in report["rows"] for p in row["pairs"] if not p["original_state_gate_passed"]]
    assert len(failures) == 2
    assert all(p["index"] == 8 and p["original_time_gate_passed"] for p in failures)
    assert all(p["scaled_remainder"] < p["scaled_state_difference"] / 100 for p in failures)
    assert report["changes_parent_decisions"] is False
    assert report["symbolic_chains_verified"] is False
