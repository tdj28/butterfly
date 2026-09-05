"""Fail-closed v2 orchestration tests; no Rössler target is integrated here."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import numpy as np
import pytest

from butterfly.homoclinic_bvp import duffing_homoclinic
from scripts import validate_projected_homoclinic as runner


MANIFEST = Path(__file__).resolve().parents[1] / "experiments/manifests/EXP-476-homoclinic-radius-tolerance-grid.json"


def read_strict_json(path):
    def reject_constant(value):
        raise AssertionError(f"nonstandard JSON numeric constant: {value}")

    return json.loads(path.read_text(), parse_constant=reject_constant)


@pytest.fixture
def protocol():
    return json.loads(MANIFEST.read_text())


@pytest.fixture
def harness(monkeypatch, tmp_path, protocol):
    """Replace every target computation, but exercise the real v2 runner."""
    manifest = deepcopy(protocol)
    source = {
        "experiment_id": manifest["source_receipt"]["experiment_id"],
        "passed": True,
        "fixed_parameters": manifest["fixed_parameters"],
    }
    source_path = tmp_path / "source.json"
    source_bytes = json.dumps(source).encode()
    source_path.write_bytes(source_bytes)
    manifest["source_receipt"].update({
        "path": str(source_path), "sha256": hashlib.sha256(source_bytes).hexdigest(),
    })
    manifest_path, output = tmp_path / "manifest.json", tmp_path / "receipt.json"
    clock = SimpleNamespace(now=100.0)
    calls = {name: [] for name in ("controls", "seed", "solve", "replay")}
    parameter = sum(manifest["physical_bounds"]["a"]) / 2.0
    mesh = np.asarray((0.0, 0.5, 1.0))
    states = np.asarray(((0.01, 8.0, 0.01), (0.0, -4.0, 0.0), (0.0, 2.0, 0.0)))

    def controls(_configuration, **kwargs):
        calls["controls"].append(kwargs)
        return {"passed": True, "positive_controls": [], "negative_control_rejection_qualified": True}

    def seed(_source, _model, _radius, _budget, deadline):
        calls["seed"].append({"deadline": deadline})
        return mesh.copy(), states.copy(), 100.0, {"source_parameter": parameter}

    def solve(_model, _mesh, _states, **kwargs):
        calls["solve"].append(kwargs)
        result = SimpleNamespace(x=mesh.copy(), y=states.copy())
        summary = {
            "passed_numerical_gates": True, "solver_success": True, "solver_status": 0,
            "parameter": parameter, "flight_time": 100.0, "nodes": 3,
            "maximum_excursion": 8.0, "minimum_parameter_box_margin": 0.2,
            "maximum_scaled_boundary_residual": 1e-12,
            "maximum_collocation_relative_rms": kwargs["tolerance"] / 2.0,
        }
        return result, summary

    def replay(_model, _solution, _parameter, _duration, **kwargs):
        calls["replay"].append(kwargs)
        return {"success": True, "maximum_state_defect": 1e-10, "rms_state_defect": 1e-11}

    monkeypatch.setattr(runner.time, "monotonic", lambda: clock.now)
    monkeypatch.setattr(runner, "git_value", lambda *args: "" if args[0] == "status" else "test-commit")
    monkeypatch.setattr(runner, "committed_manifest_binding", lambda *_args, **_kwargs: {"matches_HEAD": True})
    monkeypatch.setattr(runner, "analytic_controls", controls)
    monkeypatch.setattr(runner, "reconstruct_seed", seed)
    monkeypatch.setattr(runner, "solve_projected_homoclinic", solve)
    monkeypatch.setattr(runner, "local_replay_defects", replay)

    def run():
        manifest_path.write_text(json.dumps(manifest))
        code = runner.main(["--manifest", str(manifest_path), "--output", str(output)])
        return code, read_strict_json(output)

    return SimpleNamespace(
        manifest=manifest, manifest_path=manifest_path, source_path=source_path,
        output=output, clock=clock, calls=calls, run=run, controls=controls,
        seed=seed, solve=solve, replay=replay, mesh=mesh, states=states,
    )


def assert_failed_first_and_skipped_rest(receipt):
    assert receipt["complete"] and not receipt["passed"]
    assert not receipt["technical_passed"]
    assert len(receipt["cases"]) == 9
    assert receipt["cases"][0]["status"] == "failed"
    assert receipt["cases"][0]["passed"] is False
    assert all(row["status"] == "skipped" and row["passed"] is False for row in receipt["cases"][1:])


def test_v2_frozen_manifest_and_mocked_complete_grid(harness):
    runner.validate_manifest(harness.manifest)
    code, receipt = harness.run()
    assert code == 0 and receipt["passed"]
    assert receipt["technical_passed"] and receipt["discretization_passed"]
    assert receipt["committed_manifest"]["matches_HEAD"]
    assert len(harness.calls["seed"]) == len(harness.calls["solve"]) == len(harness.calls["replay"]) == 9
    assert harness.calls["controls"][0]["deadline"] == 100.0 + harness.manifest["budget"]["maximum_total_seconds"]
    for row in receipt["cases"]:
        assert row["replay_acceptance_limit"] == row["case"]["tolerance"]
    assert all(row["classification"] == "below_declared_empirical_resolution" for row in receipt["sensitivity"]["endpoint_comparisons"])


def test_git_status_read_failure_rejects_before_controls(harness, monkeypatch):
    monkeypatch.setattr(runner, "git_value", lambda *args: None if args[0] == "status" else "test-commit")
    with pytest.raises(SystemExit, match="clean source tree"):
        harness.run()
    assert not harness.calls["controls"]
    assert not harness.output.exists()


@pytest.fixture
def committed_protocol_repo(tmp_path):
    root = tmp_path / "source-repository"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    (root / "protocol.json").write_bytes(b'{"frozen":true}\n')
    (root / ".gitignore").write_text("ignored-protocol.json\n")
    subprocess.run(["git", "add", "protocol.json", ".gitignore"], cwd=root, check=True)
    subprocess.run([
        "git", "-c", "user.name=Protocol test", "-c", "user.email=protocol-test@example.invalid",
        "-c", "commit.gpgsign=false", "commit", "-qm", "Freeze synthetic protocol",
    ], cwd=root, check=True)
    return root


def test_committed_manifest_binding_records_exact_head_blob(committed_protocol_repo):
    path = committed_protocol_repo / "protocol.json"
    content = path.read_bytes()
    binding = runner.committed_manifest_binding(path, content, root=committed_protocol_repo)
    assert binding["matches_HEAD"] and binding["path"] == "protocol.json"
    assert binding["sha256"] == hashlib.sha256(content).hexdigest()
    assert len(binding["git_blob"]) in (40, 64)


@pytest.mark.parametrize("kind", ("missing", "untracked", "ignored", "outside", "modified"))
def test_committed_manifest_binding_rejects_unfrozen_protocol(committed_protocol_repo, tmp_path, kind):
    root = committed_protocol_repo
    content = b'{"frozen":false}\n'
    if kind == "outside":
        path = tmp_path / "external-protocol.json"
    elif kind == "modified":
        path = root / "protocol.json"
    elif kind == "ignored":
        path = root / "ignored-protocol.json"
    else:
        path = root / f"{kind}-protocol.json"
    if kind != "missing":
        path.write_bytes(content)
    message = "bytes differ" if kind == "modified" else "tracked file"
    with pytest.raises(ValueError, match=message):
        runner.committed_manifest_binding(path, content, root=root)


def test_binding_failure_prevents_controls_and_target(harness, monkeypatch):
    def reject(*_args, **_kwargs):
        raise ValueError("target manifest bytes differ from the committed HEAD protocol")

    monkeypatch.setattr(runner, "committed_manifest_binding", reject)
    with pytest.raises(ValueError, match="bytes differ"):
        harness.run()
    assert not harness.calls["controls"] and not harness.calls["seed"]


@pytest.mark.parametrize("stage", ("seed", "solve", "replay", "postreplay"))
def test_case_deadline_covers_every_stage_and_never_accepts_late_result(harness, monkeypatch, stage):
    cap = harness.manifest["budget"]["maximum_trial_seconds"]
    stage_function = {"seed": "reconstruct_seed", "solve": "solve_projected_homoclinic", "replay": "local_replay_defects", "postreplay": "local_replay_defects"}[stage]
    original = getattr(harness, "replay" if stage == "postreplay" else stage)

    def expire(*args, **kwargs):
        result = original(*args, **kwargs)
        harness.clock.now += cap
        if stage == "replay":
            runner.check_deadline(kwargs["deadline"], "mock replay")
        return result

    monkeypatch.setattr(runner, stage_function, expire)
    code, receipt = harness.run()
    assert code == 2
    assert_failed_first_and_skipped_rest(receipt)
    assert "budget exhausted" in receipt["failure"]
    if stage == "seed":
        assert not harness.calls["solve"]
    else:
        assert receipt["cases"][0]["normalized_mesh"] == harness.mesh.tolist()
        assert receipt["cases"][0]["states"] == harness.states.T.tolist()
    if stage == "solve":
        assert not harness.calls["replay"]


def test_case_budget_is_shared_not_restarted_between_stages(harness, monkeypatch):
    cap = harness.manifest["budget"]["maximum_trial_seconds"]

    def seed(*args, **kwargs):
        result = harness.seed(*args, **kwargs)
        harness.clock.now += 0.4 * cap
        return result

    def solve(*args, **kwargs):
        result = harness.solve(*args, **kwargs)
        harness.clock.now += 0.4 * cap
        return result

    def replay(*args, **kwargs):
        result = harness.replay(*args, **kwargs)
        harness.clock.now += 0.3 * cap
        return result

    monkeypatch.setattr(runner, "reconstruct_seed", seed)
    monkeypatch.setattr(runner, "solve_projected_homoclinic", solve)
    monkeypatch.setattr(runner, "local_replay_defects", replay)
    code, receipt = harness.run()
    assert code == 2
    assert_failed_first_and_skipped_rest(receipt)
    assert harness.calls["seed"][0]["deadline"] == 100.0 + cap
    assert harness.calls["solve"][0]["maximum_seconds"] == pytest.approx(0.6 * cap)
    assert harness.calls["replay"][0]["deadline"] == 100.0 + cap


def test_case_budget_is_clamped_to_remaining_total_budget(harness, monkeypatch):
    total = harness.manifest["budget"]["maximum_total_seconds"]
    remaining = harness.manifest["budget"]["maximum_trial_seconds"] / 3.0

    def controls(*args, **kwargs):
        result = harness.controls(*args, **kwargs)
        harness.clock.now += total - remaining
        return result

    monkeypatch.setattr(runner, "analytic_controls", controls)
    code, receipt = harness.run()
    assert code == 0 and receipt["passed"]
    assert harness.calls["seed"][0]["deadline"] == 100.0 + total
    assert harness.calls["solve"][0]["maximum_seconds"] == pytest.approx(remaining)
    assert harness.calls["replay"][0]["deadline"] == 100.0 + total


@pytest.mark.parametrize("failure", ("returned_failure", "exception"))
def test_replay_failure_retains_solved_path_and_skips_later_cases(harness, monkeypatch, failure):
    def replay(*args, **kwargs):
        harness.replay(*args, **kwargs)
        if failure == "exception":
            raise FloatingPointError("synthetic replay arithmetic failure")
        return {"success": False, "failed_segment": 4, "message": "synthetic replay failure"}

    monkeypatch.setattr(runner, "local_replay_defects", replay)
    code, receipt = harness.run()
    assert code == 2
    assert_failed_first_and_skipped_rest(receipt)
    first = receipt["cases"][0]
    assert first["normalized_mesh"] == harness.mesh.tolist()
    assert first["states"] == harness.states.T.tolist()
    assert first["collocation"]["passed_numerical_gates"]


def test_replay_limit_is_tied_to_case_tolerance_not_v1_absolute_gate(harness, monkeypatch):
    def replay(*args, **kwargs):
        result = harness.replay(*args, **kwargs)
        result["maximum_state_defect"] = 1.1 * harness.manifest["cases"][0]["tolerance"]
        return result

    monkeypatch.setattr(runner, "local_replay_defects", replay)
    code, receipt = harness.run()
    assert code == 2
    assert_failed_first_and_skipped_rest(receipt)
    assert receipt["cases"][0]["replay_acceptance_limit"] == harness.manifest["cases"][0]["tolerance"]


@pytest.mark.parametrize("field", ("parameter", "maximum_excursion", "maximum_collocation_relative_rms"))
@pytest.mark.parametrize("invalid", (float("nan"), float("inf")))
def test_nonfinite_collocation_row_is_failed_and_receipt_is_null_safe(harness, monkeypatch, field, invalid):
    def solve(*args, **kwargs):
        result, summary = harness.solve(*args, **kwargs)
        summary[field] = invalid
        return result, summary

    monkeypatch.setattr(runner, "solve_projected_homoclinic", solve)
    code, receipt = harness.run()
    assert code == 2
    assert_failed_first_and_skipped_rest(receipt)
    assert receipt["cases"][0]["collocation"][field] is None
    assert any(path.endswith(f".collocation.{field}") for path in receipt["nonfinite_fields_replaced_by_null"])
    assert receipt["sensitivity"]["evaluable"] is False


def test_source_input_oserror_produces_complete_skipped_receipt(harness):
    harness.manifest["source_receipt"]["path"] = str(harness.source_path.with_name("missing-source.json"))
    code, receipt = harness.run()
    assert code == 2
    assert receipt["complete"] and not receipt["passed"]
    assert "FileNotFoundError" in receipt["failure"]
    assert all(row["status"] == "skipped" for row in receipt["cases"])
    assert not harness.calls["seed"]


def test_controls_failure_prevents_target_and_retains_all_skipped_statuses(harness, monkeypatch):
    monkeypatch.setattr(runner, "analytic_controls", lambda *_args, **_kwargs: {"passed": False})
    code, receipt = harness.run()
    assert code == 2
    assert receipt["complete"] and not receipt["technical_passed"]
    assert not harness.calls["seed"]
    assert len(receipt["cases"]) == 9 and all(row["status"] == "skipped" for row in receipt["cases"])


def test_interrupted_controls_preserve_partial_progress_receipt(harness, monkeypatch):
    def controls(_configuration, *, deadline, progress):
        assert deadline == 100.0 + harness.manifest["budget"]["maximum_total_seconds"]
        progress({"passed": False, "complete": False, "positive_controls": [{"radius": 0.1, "passed": True}]})
        raise TimeoutError("synthetic interrupted second analytic control")

    monkeypatch.setattr(runner, "analytic_controls", controls)
    code, receipt = harness.run()
    assert code == 2
    assert receipt["complete"] and not receipt["passed"]
    assert receipt["controls"]["positive_controls"] == [{"radius": 0.1, "passed": True}]
    assert not receipt["controls"]["complete"]
    assert "interrupted second analytic control" in receipt["failure"]
    assert not harness.calls["seed"]
    assert all(row["status"] == "skipped" for row in receipt["cases"])


def test_nonfinite_control_diagnostic_cannot_return_success_with_failed_json(harness, monkeypatch):
    def controls(*args, **kwargs):
        result = harness.controls(*args, **kwargs)
        result["synthetic_diagnostic"] = float("nan")
        return result

    monkeypatch.setattr(runner, "analytic_controls", controls)
    code, receipt = harness.run()
    assert code == 2
    assert receipt["complete"] and receipt["passed"] is False
    assert receipt["controls"]["synthetic_diagnostic"] is None
    assert "receipt.controls.synthetic_diagnostic" in receipt["nonfinite_fields_replaced_by_null"]
    assert not harness.calls["seed"]


def test_refinement_failure_retains_all_technically_accepted_cases(harness, monkeypatch):
    def solve(*args, **kwargs):
        result, summary = harness.solve(*args, **kwargs)
        offset = {1e-6: 8e-8, 1e-7: 2e-9, 1e-8: 0.0}[kwargs["tolerance"]]
        summary["parameter"] += offset
        return result, summary

    monkeypatch.setattr(runner, "solve_projected_homoclinic", solve)
    code, receipt = harness.run()
    assert code == 2
    assert receipt["complete"] and receipt["technical_passed"]
    assert not receipt["passed"] and not receipt["discretization_passed"]
    assert all(row["passed"] and row["status"] == "passed" and row["states"] for row in receipt["cases"])
    assert "failure" not in receipt
    assert len(harness.calls["seed"]) == 9


@pytest.mark.parametrize("negative_failure", ("timeout", "node_cap", "numerical_rejection"))
def test_negative_control_requires_completed_numerical_rejection(protocol, monkeypatch, negative_failure):
    def solve(_model, _mesh, _states, **kwargs):
        if kwargs["parameter"] == 0.05:
            if negative_failure == "timeout":
                return None, {"passed_numerical_gates": False, "message": "TimeoutError: budget exhausted"}
            return SimpleNamespace(), {
                "passed_numerical_gates": False,
                "solver_status": 1 if negative_failure == "node_cap" else 2,
                "parameter": 0.03, "minimum_parameter_box_margin": 0.0,
            }
        duration = kwargs["flight_time"]
        solution = SimpleNamespace(sol=lambda mesh: duffing_homoclinic((mesh - 0.5) * duration))
        return solution, {
            "passed_numerical_gates": True, "parameter": 0.0,
            "flight_time": duration, "maximum_excursion": np.sqrt(2.0),
        }

    monkeypatch.setattr(runner, "solve_projected_homoclinic", solve)
    monkeypatch.setattr(runner, "local_replay_defects", lambda *_args, **_kwargs: {"success": True, "maximum_state_defect": 0.0})
    controls = runner.analytic_controls(protocol["analytic_controls"])
    expected = negative_failure == "numerical_rejection"
    assert controls["passed"] is expected
    assert controls["negative_control_rejection_qualified"] is expected
    assert all(row["passed"] for row in controls["positive_controls"])


def test_analytic_controls_reject_expired_total_deadline_before_solving(protocol, monkeypatch):
    monkeypatch.setattr(runner.time, "monotonic", lambda: 100.0)
    monkeypatch.setattr(runner, "solve_projected_homoclinic", lambda *_args, **_kwargs: pytest.fail("expired control must not solve"))
    with pytest.raises(TimeoutError, match="analytic controls"):
        runner.analytic_controls(protocol["analytic_controls"], deadline=100.0)
