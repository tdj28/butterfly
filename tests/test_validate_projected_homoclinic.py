import json
import hashlib
from pathlib import Path
import time

import numpy as np
import pytest

from butterfly.homoclinic_bvp import HomoclinicModel, duffing_homoclinic
from scripts.validate_projected_homoclinic import analytic_controls, main, reconstruct_seed, validate_manifest


MANIFEST = Path(__file__).resolve().parents[1] / "experiments/manifests/EXP-475-independent-projected-homoclinic-pilot.json"


def test_frozen_protocol_validates_and_analytic_controls_pass():
    manifest = json.loads(MANIFEST.read_text())
    validate_manifest(manifest)
    controls = analytic_controls(manifest["analytic_controls"])
    assert controls["passed"]
    assert not controls["negative_control"]["passed_numerical_gates"]
    assert len(controls["positive_controls"]) == 3


def test_pilot_does_not_allow_nonshrinking_endpoint_sequence():
    manifest = json.loads(MANIFEST.read_text())
    manifest["cases"][1]["radius"] = manifest["cases"][0]["radius"]
    with pytest.raises(ValueError, match="radii must shrink"):
        validate_manifest(manifest)


def test_seed_reconstruction_trims_and_extends_analytic_three_state_orbit():
    # Synthetic Duffing plus a decoupled stable coordinate exercises the seed
    # preparation path without integrating any Rössler target.
    def field(values, _parameter):
        x, y, z = values
        return np.vstack((y, x - x**3, -2.0 * z))

    model = HomoclinicModel("duffing-plus-stable", 3, field, None, None, lambda _p: np.zeros(3))
    duration = 16.5
    samples = np.arange(1, 33) * duration / 32 - 12.0
    exact = np.vstack((duffing_homoclinic(samples), np.zeros(len(samples)))).T
    source = {
        "final_variables": {"a": 0.0, "total_flight_time": duration},
        "segment_count": 32, "final_nodes": exact[:-1].tolist(),
        "final_endpoint": exact[-1].tolist(),
    }
    mesh, states, flight_time, diagnostics = reconstruct_seed(
        source, model, 0.01, {"maximum_seed_step": 0.03, "maximum_state_norm": 10.0},
        time.monotonic() + 10.0,
    )
    assert mesh[0] == 0.0 and mesh[-1] == 1.0 and np.all(np.diff(mesh) > 0.0)
    assert states.shape == (3, len(mesh))
    np.testing.assert_allclose(np.linalg.norm(states[:, [0, -1]], axis=0), 0.01, atol=1e-10)
    assert 10.0 < flight_time < 13.0
    assert diagnostics["maximum_seed_arc_defect"] < 1e-8
    assert diagnostics["trimmed_departure_time"] > 5.0
    assert diagnostics["appended_arrival_time"] > 1.0


def test_seed_construction_respects_expired_budget():
    manifest = json.loads(MANIFEST.read_text())
    model = HomoclinicModel("synthetic", 3, None, None, None, lambda _p: np.zeros(3))
    source = {
        "final_variables": {"a": 0.0, "total_flight_time": 2.0},
        "segment_count": 3, "final_nodes": [[0.001, 0, 0], [1.0, 0, 0]],
        "final_endpoint": [0.02, 0, 0],
    }
    with pytest.raises(TimeoutError, match="budget exhausted"):
        reconstruct_seed(source, model, 0.01, manifest["budget"], time.monotonic() - 1.0)


def test_target_execution_rejects_dirty_source_before_controls(monkeypatch, tmp_path):
    monkeypatch.setattr("scripts.validate_projected_homoclinic.git_value", lambda *args: "dirty-or-commit")
    monkeypatch.setattr("scripts.validate_projected_homoclinic.analytic_controls", lambda _configuration: pytest.fail("target with dirty source must not start"))
    with pytest.raises(SystemExit, match="committed protocol and a clean source tree"):
        main(["--manifest", str(MANIFEST), "--output", str(tmp_path / "receipt.json")])


def test_seed_failure_receipt_identifies_failed_and_skipped_cases(monkeypatch, tmp_path):
    manifest = json.loads(MANIFEST.read_text())
    source_path = tmp_path / "source.json"
    source = {"experiment_id": "EXP-342", "passed": True, "fixed_parameters": manifest["fixed_parameters"]}
    raw = json.dumps(source).encode()
    source_path.write_bytes(raw)
    manifest["source_receipt"].update({"path": str(source_path), "sha256": hashlib.sha256(raw).hexdigest()})
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))
    monkeypatch.setattr("scripts.validate_projected_homoclinic.git_value", lambda *args: "" if args[0] == "status" else "test-commit")
    monkeypatch.setattr("scripts.validate_projected_homoclinic.analytic_controls", lambda _configuration: {"passed": True})

    def reject_seed(*args, **kwargs):
        raise ValueError("synthetic seed failure")

    monkeypatch.setattr("scripts.validate_projected_homoclinic.reconstruct_seed", reject_seed)
    output = tmp_path / "receipt.json"
    assert main(["--manifest", str(manifest_path), "--output", str(output)]) == 2
    receipt = json.loads(output.read_text())
    assert receipt["complete"] and not receipt["passed"]
    assert receipt["cases"][0]["status"] == "failed"
    assert "synthetic seed failure" in receipt["cases"][0]["failure"]
    assert [row["status"] for row in receipt["cases"][1:]] == ["skipped"] * 3
