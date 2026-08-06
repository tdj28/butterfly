import json
from pathlib import Path

from butterfly.scan import ScanManifest, execute_scan, sha256_bytes


def tiny_manifest() -> dict:
    return {
        "schema": "butterfly.scan-manifest.v1",
        "experiment_id": "TEST-SCAN",
        "grid": {
            "a": {"min": 0.1798, "max": 0.1798, "count": 1},
            "b": 0.2,
            "c": {"min": 10.3084, "max": 10.3084, "count": 1},
        },
        "integration": {
            "initial_state": [0.0, 4.0, 0.0],
            "transient": 5.0,
            "observation_horizon": 20.0,
            "max_crossings": 3,
            "solver": {
                "method": "DOP853",
                "rtol": 1e-9,
                "atol": 1e-11,
                "max_step": 0.1,
            },
        },
        "classifier": {
            "max_period": 2,
            "required_repeats": 2,
            "atol": 1e-6,
            "rtol": 1e-7,
        },
    }


def tiny_resolved_manifest() -> dict:
    manifest = tiny_manifest()
    manifest["schema"] = "butterfly.scan-manifest.v2"
    manifest["lyapunov"] = {
        "transient": 1.0,
        "duration": 2.0,
        "qr_interval": 0.5,
        "blocks": 2,
    }
    return manifest


def test_plan_hash_is_stable() -> None:
    first = ScanManifest.from_dict(tiny_manifest())
    second = ScanManifest.from_dict(json.loads(json.dumps(tiny_manifest())))
    assert first.plan_hash == second.plan_hash
    assert len(first.plan_hash) == 64


def test_execute_scan_writes_hash_verified_artifacts(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(tiny_manifest()) + "\n", encoding="utf-8")
    output = tmp_path / "output"
    receipt = execute_scan(manifest_path, output)
    result_bytes = (output / "result.json").read_bytes()
    result = json.loads(result_bytes)
    assert result["row_count"] == 1
    assert receipt["row_count"] == 1
    assert receipt["result_sha256"] == sha256_bytes(result_bytes)
    assert (output / "manifest.normalized.json").exists()
    assert (output / "receipt.json").exists()


def test_resolved_scan_records_lyapunov_evidence(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(tiny_resolved_manifest()) + "\n", encoding="utf-8"
    )
    output = tmp_path / "output"
    execute_scan(manifest_path, output)
    row = json.loads((output / "result.json").read_bytes())["rows"][0]
    assert row["lyapunov_success"] is True
    assert len(row["lyapunov_exponents"]) == 3
    assert len(row["lyapunov_block_standard_error"]) == 3
    assert row["classification_reason"]


def test_v2_manifest_requires_complete_lyapunov_configuration() -> None:
    manifest = tiny_manifest()
    manifest["schema"] = "butterfly.scan-manifest.v2"
    try:
        ScanManifest.from_dict(manifest)
    except ValueError as error:
        assert "require Lyapunov" in str(error)
    else:
        raise AssertionError("v2 manifest without Lyapunov configuration was accepted")
