"""Private-artifact-free input packaging and actual sealed-consumer tests."""
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys

import numpy as np
import pytest

from butterfly import paired_input_io as io
from butterfly import paired_input_package as package
from butterfly.paired_inputs import IDS, SOURCE, load_references
from scripts.build_paired_runtime import ROOT, build


def save_json(root, name, payload):
    path = root/name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True))
    return {"path": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def synthetic_inputs(root):
    root.mkdir()
    # Reuse the older independently specified raw/summary geometry control.
    fixture = runpy.run_path(str(ROOT/"tests/test_paired_capture_inputs.py"))["fixture"]
    raw, template, parameters = fixture()
    for section in ("historical-negative", "barrio-positive"):
        for name in ("angles", "signed_scaled_gate_distance", "gate_unresolved", "orientation_unresolved",
                     "extremum_times", "extremum_states", "extremum_plane_distance", "extremum_gate_accepted"):
            raw[section+"_"+name] = np.empty(0)
    raw.update(integration_times=np.empty(0), integration_states=np.empty((0, 3)))
    rows, raw_files = [], []
    inputs = {}
    for case in IDS:
        row = json.loads(json.dumps(template))
        path = root/f"capture/{case}.npz"
        path.parent.mkdir(exist_ok=True)
        np.savez(path, **raw)
        descriptor = {"path": path.name, "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        row.update(candidate_id=case, profile={"name": "dop853-refined"}, passed=True, raw=descriptor)
        rows.append(row)
        raw_files.append(descriptor)
        inputs["capture_"+case] = save_json(root, f"capture/{case}.json", row)
    outcomes = [{"candidate_id": case, "outcome": "qualified"} for case in IDS]
    inputs["capture_source_receipt"] = save_json(root, "capture/receipt.json", {"source": {"commit": SOURCE},
        "status": "completed", "passed": True, "case_outcomes": outcomes, "profiles": rows, "files": raw_files})
    inputs["event_qualification"] = save_json(root, "qualification.json", {"experiment_id": "EXP-480", "passed": True,
        "source_commit": SOURCE, "case_outcomes": outcomes, "raw_receipt_sha256": inputs["capture_source_receipt"]["sha256"]})
    inputs["nominations"] = save_json(root, "nominations.json", {"nomination_result": {"direct_candidate_ids": IDS}})
    inputs["candidates"] = save_json(root, "candidates.json", {"candidates": [
        {"id": case, "passed": True, "parameters": asdict(parameters)} for case in IDS]})
    plan = {"candidate_ids": IDS, "inputs": inputs}
    save_json(root, "proposal.json", plan)
    return plan


def test_exact_nine_file_package_replays_synthetic_reference_inputs(tmp_path):
    root = tmp_path/"source"
    plan = synthetic_inputs(root)
    output = tmp_path/"inputs"
    built = package.build_package(root/"proposal.json", root, output)
    assert built["file_count"] == 9 and not built["target_execution_authorized"]
    loaded = package.load_package(output, built["sha256"])
    assert loaded == plan and load_references(loaded, output) == load_references(plan, root)
    with pytest.raises(FileExistsError):
        package.build_package(root/"proposal.json", root, output)


@pytest.mark.parametrize("kind", ["digest", "changed", "extra", "missing", "symlink", "authorization", "role"])
def test_corrupt_or_substituted_package_cannot_pass(tmp_path, kind):
    root = tmp_path/"source"
    synthetic_inputs(root)
    output = tmp_path/"inputs"
    built = package.build_package(root/"proposal.json", root, output)
    digest = built["sha256"]
    if kind == "digest": digest = "0"*64
    elif kind == "changed": (output/"candidates.json").write_text("{}")
    elif kind == "extra": (output/"extra.json").write_text("{}")
    elif kind == "missing": (output/"candidates.json").rename(tmp_path/"withheld.json")
    elif kind == "symlink":
        (output/"candidates.json").rename(tmp_path/"withheld.json")
        (output/"candidates.json").symlink_to(tmp_path/"withheld.json")
    else:
        contract = json.loads((output/"input-contract.json").read_bytes())
        if kind == "authorization": contract["target_execution_authorized"] = True
        else: contract["plan"]["path"] = "candidates.json"
        (output/"input-contract.json").write_text(json.dumps(contract))
        digest = hashlib.sha256((output/"input-contract.json").read_bytes()).hexdigest()
    with pytest.raises((ValueError, OSError)):
        package.load_package(output, digest)


@pytest.mark.parametrize("relative", ["../file", "./file", "/file", "sub/../file", "", "sub//file"])
def test_input_paths_are_canonical_and_confined(tmp_path, relative):
    with pytest.raises(ValueError):
        io.confined_path(tmp_path, relative)


@pytest.mark.parametrize("kind", ["hash", "size", "oversize", "symlink", "directory", "basename"])
def test_bounded_input_io_rejects_invalid_files(tmp_path, monkeypatch, kind):
    path = tmp_path/"file"
    path.write_bytes(b"abc")
    row = {"path": "file", "sha256": hashlib.sha256(b"abc").hexdigest(), "bytes": 3}
    if kind == "hash": row["sha256"] = "0"*64
    elif kind == "size": row["bytes"] = 2
    elif kind == "oversize": monkeypatch.setattr(io, "MAXIMUM_INPUT_BYTES", 2)
    elif kind == "symlink":
        path.rename(tmp_path/"original")
        path.symlink_to(tmp_path/"original")
    elif kind == "directory":
        path.rename(tmp_path/"original")
        path.mkdir()
    else: row["path"] = "sub/file"
    with pytest.raises(ValueError):
        io.collection_file(tmp_path, row)


@pytest.mark.parametrize("kind", ["duplicate-candidate", "unqualified", "source", "raw-receipt"])
def test_coherently_rehashed_bad_source_metadata_still_fails_scientific_input_gate(tmp_path, kind):
    root = tmp_path/"source"
    plan = synthetic_inputs(root)
    key = "candidates" if kind == "duplicate-candidate" else "event_qualification"
    row = plan["inputs"][key]
    payload = json.loads((root/row["path"]).read_bytes())
    if kind == "duplicate-candidate": payload["candidates"].append(payload["candidates"][0])
    elif kind == "unqualified": payload["passed"] = False
    elif kind == "source": payload["source_commit"] = "0"*40
    else: payload["raw_receipt_sha256"] = "0"*64
    plan["inputs"][key] = save_json(root, row["path"], payload)
    with pytest.raises(ValueError):
        load_references(plan, root)


def test_actual_isolated_worker_audits_synthetic_package_without_old_scripts(tmp_path):
    if os.name != "posix":
        pytest.skip("isolated parent-guard worker requires POSIX")
    root = tmp_path/"source"
    plan = synthetic_inputs(root)
    input_root, bundle, output = tmp_path/"inputs", tmp_path/"bundle", tmp_path/"evidence"
    inputs = package.build_package(root/"proposal.json", root, input_root)
    runtime = build(bundle, startup_guard_seconds=30.)
    contract = json.loads((bundle/"runtime-contract.json").read_bytes())
    output.mkdir()
    command = [sys.executable, "-I", "-S", "-B", "-X", "utf8=1", str(bundle/"worker.py"),
        "--contract-sha256", runtime["sha256"], "--output-dir", str(output), "--mode", "audit-inputs",
        "--input-root", str(input_root), "--input-contract-sha256", inputs["sha256"]]
    with (tmp_path/"stdout").open("wb") as stdout, (tmp_path/"stderr").open("wb") as stderr:
        process = subprocess.Popen(command, cwd=tmp_path, env=contract["environment"], stdin=subprocess.PIPE,
            stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            code = process.wait(timeout=40)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            process.stdin.close()
    assert code == 0, (tmp_path/"stderr").read_text()
    actual = json.loads((output/"input-audit.json").read_bytes())
    assert actual["audit"] == load_references(plan, root)
    assert actual["input_contract_sha256"] == inputs["sha256"] and not actual["target_execution_authorized"]
    assert not any(n.startswith(("scripts.", "torch", "triton")) for n in actual["loaded_modules"])
    assert not list(bundle.rglob("*.pyc"))
