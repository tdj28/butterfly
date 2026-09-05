"""Public-summary figure checks; no target orbit data or integration required."""

from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

import pytest

from scripts import plot_homoclinic_refinement_grid as plot


SUMMARY = Path(__file__).resolve().parents[1] / "docs/experiments/receipts/EXP-476.json"


@pytest.fixture
def summary():
    return json.loads(SUMMARY.read_text())


def test_checked_in_summary_retains_failure_and_only_one_qualified_radius(summary):
    before = deepcopy(summary)
    cases, qualified = plot.validate_summary(summary)
    assert summary == before
    assert len(cases) == 9
    assert [row["status"] for row in cases] == ["passed"] * 5 + ["failed"] + ["skipped"] * 3
    assert qualified["radius"] == 0.01
    assert qualified["D1"] == 4.886673454773671e-9
    assert qualified["D2"] == 3.926102498663653e-10
    assert all(row["classification"] == "unavailable" for row in summary["sensitivity"]["endpoint_comparisons"])


@pytest.mark.parametrize("key", [
    "passed", "technical_passed", "discretization_passed", "nine_case_qualification_complete", "source_dirty",
])
def test_top_level_false_status_must_remain_false(summary, key):
    summary[key] = True
    with pytest.raises(ValueError, match="failed, incomplete"):
        plot.validate_summary(summary)


@pytest.mark.parametrize("key", list(plot.FROZEN_BINDINGS))
def test_summary_identifies_exact_frozen_source_and_raw_receipt(summary, key):
    summary[key] = "wrong binding"
    with pytest.raises(ValueError, match="frozen EXP-476 source"):
        plot.validate_summary(summary)


@pytest.mark.parametrize("key", [
    "maximum_total_seconds", "maximum_trial_seconds", "maximum_nodes", "maximum_seed_step", "maximum_state_norm",
])
def test_budget_labels_cannot_silently_describe_changed_protocol(summary, key):
    summary["budget"][key] *= 2
    with pytest.raises(ValueError, match="budget and stop-rule"):
        plot.validate_summary(summary)


def test_stop_rule_cannot_change_while_plot_still_claims_frozen_stop(summary):
    summary["budget"]["stop_on_first_failed_case"] = False
    with pytest.raises(ValueError, match="budget and stop-rule"):
        plot.validate_summary(summary)


@pytest.mark.parametrize("key", list(plot.FROZEN_REFINEMENT))
def test_hardcoded_axes_and_gates_are_bound_to_frozen_refinement(summary, key):
    if isinstance(summary["refinement"][key], list):
        summary["refinement"][key][0] *= 2
    else:
        summary["refinement"][key] *= 2
    with pytest.raises(ValueError, match="grid labels and sensitivity gates"):
        plot.validate_summary(summary)


@pytest.mark.parametrize("key", ["passed", "complete", "negative_control_rejection_qualified", "shrinking_truncation_error"])
def test_control_subtitle_requires_completed_qualified_controls(summary, key):
    summary["controls"][key] = False
    with pytest.raises(ValueError, match="completed, passed analytic controls"):
        plot.validate_summary(summary)


@pytest.mark.parametrize("change, message", [
    (lambda controls: controls.update(collocation_tolerance=1e-7), "control tolerances"),
    (lambda controls: controls["positive_controls"].pop(), "three frozen"),
    (lambda controls: controls["positive_controls"][0].update(passed=False), "positive control diagnostics"),
    (lambda controls: controls["positive_controls"][0].update(maximum_analytic_state_error=1.0), "positive control diagnostics"),
    (lambda controls: controls["positive_controls"][1].update(maximum_analytic_state_error=5e-5), "shrinking gate"),
    (lambda controls: controls["positive_controls"][0]["replay"].update(success=False), "positive control diagnostics"),
    (lambda controls: controls["negative_control"].update(solver_status=1), "negative control"),
    (lambda controls: controls["negative_control"].update(passed_numerical_gates=True), "negative control"),
])
def test_analytic_control_diagnostics_cannot_contradict_subtitle(summary, change, message):
    change(summary["controls"])
    with pytest.raises(ValueError, match=message):
        plot.validate_summary(summary)


@pytest.mark.parametrize("key, value", [
    ("solver_success", False),
    ("passed_numerical_gates", False),
    ("solver_status", 1),
    ("nodes", 48001),
    ("maximum_scaled_boundary_residual", 1e-4),
    ("maximum_collocation_relative_rms", 1e-4),
    ("minimum_parameter_box_margin", 0.0),
    ("maximum_excursion", 0.0),
    ("source_a_difference", 1e-4),
    ("replay_acceptance_limit", 1e-3),
])
def test_passed_case_must_support_all_gates_label(summary, key, value):
    summary["cases"][0][key] = value
    with pytest.raises(ValueError, match="all-gates"):
        plot.validate_summary(summary)


@pytest.mark.parametrize("change, message", [
    (lambda cases: cases[0]["replay"].update(success=False), "all-gates"),
    (lambda cases: cases[0]["replay"].update(maximum_state_defect=1e-3), "all-gates"),
    (lambda cases: cases[5].update(solver_status=2), "node-cap failure"),
    (lambda cases: cases[5].update(solver_success=True), "node-cap failure"),
    (lambda cases: cases[6].update(reason="not the frozen stop rule"), "skipped targets"),
    (lambda cases: cases[6].update(a=0.18), "skipped targets"),
    (lambda cases: cases[5].update(passed=True), "qualification flags"),
])
def test_failed_and_skipped_evidence_cannot_be_reclassified(summary, change, message):
    change(summary["cases"])
    with pytest.raises(ValueError, match=message):
        plot.validate_summary(summary)


@pytest.mark.parametrize("change", [
    lambda summary: summary["cases"][0].update(a=0.18264359),
    lambda summary: summary["sensitivity"]["endpoint_comparisons"][0].update(classification="resolved"),
    lambda summary: summary["sensitivity"]["radius_refinements"][1].update(technical_passed=True),
])
def test_sensitivity_is_recomputed_instead_of_trusting_edited_claims(summary, change):
    change(summary)
    with pytest.raises(ValueError, match="sensitivity disagrees"):
        plot.validate_summary(summary)


@pytest.mark.parametrize("change", [
    lambda summary: summary["cases"].pop(),
    lambda summary: summary["cases"].append(deepcopy(summary["cases"][0])),
    lambda summary: summary["cases"].__setitem__(1, deepcopy(summary["cases"][0])),
    lambda summary: summary["cases"].reverse(),
])
def test_plot_rejects_malformed_or_reordered_frozen_grid(summary, change):
    change(summary)
    with pytest.raises(ValueError):
        plot.validate_summary(summary)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_any_nonfinite_diagnostic_blocks_figure(summary, value):
    summary["cases"][0]["replay"]["maximum_state_defect"] = value
    with pytest.raises(ValueError, match="nonfinite"):
        plot.validate_summary(summary)


@pytest.mark.parametrize("value", [None, [], "summary"])
def test_nonmapping_summary_fails_cleanly(value):
    with pytest.raises(ValueError, match="compact grid summary"):
        plot.validate_summary(value)


def test_figure_renders_from_public_summary_without_orbit_integration(summary, monkeypatch, tmp_path):
    def no_integration(*args, **kwargs):
        pytest.fail("summary-only figure must not integrate or solve a target")

    monkeypatch.setattr("scipy.integrate.solve_ivp", no_integration)
    monkeypatch.setattr("scipy.integrate.solve_bvp", no_integration)
    monkeypatch.setattr(plot, "git_value", lambda *args: "" if args[0] == "status" else "test-commit")
    output, receipt_path = tmp_path / "figure.png", tmp_path / "figure-receipt.json"
    assert plot.main(["--summary", str(SUMMARY), "--output", str(output), "--receipt", str(receipt_path), "--dpi", "48"]) == 0
    receipt = json.loads(receipt_path.read_text())
    assert output.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert receipt["figure_sha256"] == hashlib.sha256(output.read_bytes()).hexdigest()
    assert receipt["summary_sha256"] == hashlib.sha256(SUMMARY.read_bytes()).hexdigest()
    assert receipt["case_counts"] == {"passed": 5, "failed": 1, "skipped": 3}
    assert receipt["qualified_radius"] == 0.01
    assert receipt["raw_artifact_required_to_regenerate_figure"] is False
    assert receipt["failed_estimates_plotted_as_qualified"] is False
    assert receipt["endpoint_comparisons_qualified"] is False


def test_invalid_summary_does_not_create_figure(summary, tmp_path):
    summary["controls"]["passed"] = False
    input_path, output, receipt = tmp_path / "invalid.json", tmp_path / "figure.png", tmp_path / "receipt.json"
    input_path.write_text(json.dumps(summary))
    with pytest.raises(SystemExit, match="invalid compact summary"):
        plot.main(["--summary", str(input_path), "--output", str(output), "--receipt", str(receipt)])
    assert not output.exists() and not receipt.exists()
