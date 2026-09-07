"""Exact local package of the declared plan and preserved reference inputs.

Packaging/audit permission is not target execution permission. The final
controller must independently authenticate the source, review and package hash.
"""
import hashlib
import json
from pathlib import Path

from . import paired_input_io as io
from ._paired_startup import inventory, write_json


SCHEMA = "butterfly.paired-input-package.v1"
CASES = ["local-a025-c083", "local-a027-c083"]
INPUT_KEYS = {"candidates", "nominations", "event_qualification", "capture_source_receipt", *["capture_"+c for c in CASES]}


def declared_files(plan, root):
    """Resolve exactly six JSON inputs and two receipt-bound raw NPZs."""
    if plan["candidate_ids"] != CASES or set(plan["inputs"]) != INPUT_KEYS:
        raise ValueError("exact declared two-case input set required")
    files = {}
    for key, row in plan["inputs"].items():
        raw = io.checked_input(root, row)
        if row["path"] in files or row["path"] in ("plan.json", "input-contract.json"):
            raise ValueError("input role paths must be distinct")
        files[row["path"]] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    receipt_row = plan["inputs"]["capture_source_receipt"]
    receipt = json.loads(io.checked_input(root, receipt_row))
    parent = Path(receipt_row["path"]).parent
    for case in CASES:
        selected = [r for r in receipt["profiles"] if r["candidate_id"] == case and r["profile"]["name"] == "dop853-refined"]
        if len(selected) != 1:
            raise ValueError("exact one refined raw reference per case required")
        row = selected[0]["raw"]
        path = io.collection_file(Path(root)/parent, row)
        relative = (parent/path.name).as_posix()
        if relative in files:
            raise ValueError("raw reference roles must have distinct paths")
        files[relative] = {"bytes": row["bytes"], "sha256": row["sha256"]}
    return files


def build_package(plan_path, root, output):
    """Copy only hash-verified declared bytes into a fresh local directory."""
    root = Path(root).resolve(strict=True)
    plan_path = Path(plan_path).resolve(strict=True)
    if plan_path.stat().st_size > io.MAXIMUM_INPUT_BYTES:
        raise ValueError("input plan exceeds fixed byte bound")
    raw = io.checked_input(root, {"path": plan_path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(plan_path.read_bytes()).hexdigest()})
    plan = json.loads(raw)
    files = declared_files(plan, root)
    output = Path(output).absolute()
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    with (output/"plan.json").open("xb") as stream:
        stream.write(raw)
    for name, row in files.items():
        content = io.checked_input(root, {"path": name, **row})
        path = output/name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(content)
    contract = {"schema": SCHEMA, "target_execution_authorized": False,
        "source_plan_path": plan_path.relative_to(root).as_posix(),
        "plan": {"path": "plan.json", "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()},
        "files": inventory(output), "scope": "declared preserved inputs only; not reviewed execution authority"}
    write_json(output/"input-contract.json", contract)
    digest = hashlib.sha256((output/"input-contract.json").read_bytes()).hexdigest()
    load_package(output, digest)
    return {"path": str(output/"input-contract.json"), "sha256": digest,
        "file_count": len(contract["files"]), "bytes": sum(r["bytes"] for r in contract["files"].values()),
        "plan_sha256": contract["plan"]["sha256"], "target_execution_authorized": False}


def load_package(root, expected_sha256):
    """Validate external digest, exact package contents and declared input roles."""
    root = Path(root).resolve(strict=True)
    contract = json.loads(io.checked_input(root, {"path": "input-contract.json", "sha256": expected_sha256}))
    if (contract["schema"] != SCHEMA or contract["target_execution_authorized"] is not False
            or contract["plan"]["path"] != "plan.json" or len(contract["files"]) != 9):
        raise ValueError("invalid nine-file input-only contract")
    if inventory(root, omit=("input-contract.json",)) != contract["files"]:
        raise ValueError("input package contains missing, extra or changed files")
    plan = json.loads(io.checked_input(root, contract["plan"]))
    expected = {"plan.json": {k: contract["plan"][k] for k in ("bytes", "sha256")}, **declared_files(plan, root)}
    if expected != contract["files"]:
        raise ValueError("input package differs from full declared role set")
    return plan
