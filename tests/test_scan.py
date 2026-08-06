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
