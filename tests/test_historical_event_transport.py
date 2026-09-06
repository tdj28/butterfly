"""Outcome-free EXP-480 controls. No nominated Rössler trajectory is integrated."""
from copy import deepcopy
import json

import numpy as np
import pytest

from butterfly import PoincareSection, SolverConfig
from butterfly.periodic import PeriodicOrbitCorrection
from scripts import check_historical_event_transport as run


@pytest.fixture
def plan():
    return json.loads(run.PLAN.read_bytes())


def harmonic_rhs(t, y):
    return np.asarray([-y[1], y[0], 0.0])


def harmonic_sections():
    return {"historical-negative": PoincareSection((0, 1, 0), 0, -1, 0, 0),
            "barrio-positive": PoincareSection((1, 0, 0), 0, 1)}


def harmonic_design(plan):
    design = deepcopy(plan["design"])
    design["expected_counts"] = {name: 1 for name in design["sections"]}
    return design


def test_draft_execution_is_locked_before_input_or_solver_calls(plan):
    with pytest.raises(ValueError, match="no target execution"):
        run.execution_gate(plan)


def test_real_execute_cli_refuses_draft_before_reading_targets(monkeypatch):
    monkeypatch.setattr("sys.argv", ["check", "--mode", "execute", "--source-commit", "a" * 40])
    monkeypatch.setattr(run, "prepare", lambda p: pytest.fail("must not open target inputs"))
    with pytest.raises(ValueError, match="no target execution"):
        run.main()


def test_review_must_bind_design_raw_review_and_runtime(plan, tmp_path):
    plan.update(status="reviewed-frozen", execution_authorized=True)
    raw = tmp_path / "review.json"
    raw.write_text('{"synthetic_review":true}')
    hashes = {}
    for name in run.REVIEW_RUNTIME_PATHS:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# synthetic reviewed runtime\n")
        hashes[name] = run.evidence.sha256_file(path)
    review = {"schema": "butterfly.design-review-adjudication.v1", "design_sha256": run.design_hash(plan),
              "approved_for_execution": True, "adjudication": [{"finding": "synthetic", "decision": "accepted"}],
              "review_receipt": {"path": "review.json", "sha256": run.evidence.sha256_file(raw)}, "runtime_files": hashes}
    path = tmp_path / "adjudication.json"
    path.write_text(json.dumps(review))
    plan["review"] = {"path": path.name, "sha256": run.evidence.sha256_file(path)}
    run.execution_gate(plan, tmp_path)
    (tmp_path / run.REVIEW_RUNTIME_PATHS[0]).write_text("# altered runtime\n")
    with pytest.raises(ValueError, match="runtime differs"):
        run.execution_gate(plan, tmp_path)
    plan["design"]["maximum_wall_seconds"] += 1
    with pytest.raises(ValueError, match="another design"):
        run.execution_gate(plan, tmp_path)


@pytest.mark.parametrize("change", ["empty", "drop_candidate", "wrong_section", "nan"])
def test_invalid_design_cannot_pass_vacuously(plan, change):
    design = plan["design"]
    if change == "empty":
        design["profiles"] = []
    elif change == "drop_candidate":
        design["candidate_ids"].pop()
    elif change == "wrong_section":
        design["expected_counts"]["historical-negative"] = 8
    else:
        design["state_scales"][0] = float("nan")
    with pytest.raises(ValueError):
        run.validate_design(design)


@pytest.mark.parametrize("method", ["DOP853", "Radau"])
def test_real_solvers_collect_ordered_analytic_plane_events(plan, method):
    design = harmonic_design(plan)
    raw, diagnostic = run.collect_events(harmonic_rhs, [1, 0, 0], 2*np.pi,
        harmonic_sections(), SolverConfig(method=method, max_step=0.02), design)
    assert diagnostic["integration_success"] and diagnostic["finite_raw_data"] and diagnostic["horizon_reached"]
    summaries = run.summarize_events(raw, 2*np.pi, design)
    assert all(row["passed"] for row in summaries.values())
    assert summaries["historical-negative"]["windows"][0]["phases"] == pytest.approx([0.25], abs=1e-9)
    assert summaries["barrio-positive"]["windows"][0]["phases"] == pytest.approx([0.5], abs=1e-9)
    assert len(raw["historical-negative_times"]) > raw["historical-negative_accepted"].sum()


def test_boundary_and_extremum_ambiguity_fail_without_moving_window(plan):
    design = harmonic_design(plan)
    raw, _ = run.collect_events(harmonic_rhs, [1, 0, 0], 2*np.pi, harmonic_sections(), SolverConfig(), design)
    design["acceptance"]["minimum_window_boundary_phase_distance"] = 0.3
    assert not run.summarize_events(raw, 2*np.pi, design)["historical-negative"]["passed"]
    design["acceptance"]["minimum_window_boundary_phase_distance"] = 1e-7
    raw["historical-negative_extremum_plane_distance"][:] = 0
    assert not run.summarize_events(raw, 2*np.pi, design)["historical-negative"]["passed"]


def test_ordered_comparison_does_not_search_cyclic_rotations(plan):
    left = {"states": [[1, 0, 0], [-1, 0, 0]], "phases": [0.1, 0.6]}
    right = {"states": [[-1, 0, 0], [1, 0, 0]], "phases": [0.1, 0.6]}
    assert not run.compare_windows(left, right, plan["design"])["passed"]


def setup_synthetic_execution(plan, monkeypatch):
    plan["design"] = harmonic_design(plan)
    plan["design"]["profiles"] = [plan["design"]["profiles"][0]]
    correction = PeriodicOrbitCorrection(np.array([1., 0, 0]), 2*np.pi, np.array([1., 0, 0]),
                                        0., 0., 0., 1, True, True, "synthetic")
    monkeypatch.setattr(run, "correct_periodic_orbit", lambda *a, **kw: correction)
    monkeypatch.setattr(run, "sections", lambda p: harmonic_sections())
    monkeypatch.setattr(run, "rossler_rhs", lambda t, y, p: harmonic_rhs(t, y))
    return [{"id": "synthetic", "parameters": {"a": .2, "b": .2, "c": 7},
             "correction": {"initial_state": [1, 0, 0], "period_time": 2*np.pi}}]


def test_execution_serializes_all_arrays_and_rechecks_files(plan, tmp_path, monkeypatch):
    candidates = setup_synthetic_execution(plan, monkeypatch)
    result = run.execute(plan, candidates, tmp_path / "output", {"mode": "synthetic"})
    assert result["passed"] and len(result["files"]) == 3
    for row in result["files"]:
        run.evidence.collection_file(tmp_path / "output", row)
    assert json.loads((tmp_path / "output/receipt.json").read_bytes())["passed"]


def test_solver_failure_retains_raw_and_rejects_pass(plan, tmp_path, monkeypatch):
    candidates = setup_synthetic_execution(plan, monkeypatch)
    original = run.collect_events
    def failed(*a, **kw):
        raw, diagnostics = original(*a, **kw)
        diagnostics["integration_success"] = False
        return raw, diagnostics
    monkeypatch.setattr(run, "collect_events", failed)
    result = run.execute(plan, candidates, tmp_path / "output", {})
    assert not result["passed"]
    assert (tmp_path / "output" / result["profiles"][0]["raw"]["path"]).exists()


def test_final_source_failure_preserves_outputs_and_fails(plan, tmp_path, monkeypatch):
    candidates = setup_synthetic_execution(plan, monkeypatch)
    def changed():
        raise ValueError("changed source")
    result = run.execute(plan, candidates, tmp_path / "output", {}, source_recheck=changed)
    assert result["status"] == "failed" and not result["passed"]
    assert len(result["files"]) == 3


def test_changed_raw_file_invalidates_final_result(plan, tmp_path, monkeypatch):
    candidates = setup_synthetic_execution(plan, monkeypatch)
    original = run.summarize_events
    def corrupt_after_recording(*a, **kw):
        result = original(*a, **kw)
        next((tmp_path / "output").glob("*.npz")).write_bytes(b"synthetic corruption")
        return result
    monkeypatch.setattr(run, "summarize_events", corrupt_after_recording)
    result = run.execute(plan, candidates, tmp_path / "output", {})
    assert result["status"] == "failed" and not result["passed"]
    assert "hash/size mismatch" in result["final_audit_failure"]["message"]


def test_interrupt_records_receipt_without_starting_another_profile(plan, tmp_path, monkeypatch):
    candidates = setup_synthetic_execution(plan, monkeypatch)
    plan["design"]["profiles"] *= 2
    def interrupted(*a, **kw):
        raise KeyboardInterrupt("synthetic interruption")
    monkeypatch.setattr(run, "correct_periodic_orbit", interrupted)
    result = run.execute(plan, candidates, tmp_path / "output", {})
    assert result["status"] == "interrupted" and len(result["profiles"]) == 1
    assert not result["passed"]
