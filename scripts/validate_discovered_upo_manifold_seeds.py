#!/usr/bin/env python3
"""Validate unstable-manifold seeds for dynamically discovered UPO families."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from butterfly import SolverConfig
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from validate_upo_manifold_seeds import _validate_instance


def _read_hashed(source):
    path = Path(source["path"])
    payload = path.read_bytes()
    digest = sha256_bytes(payload)
    if digest != source["sha256"]:
        raise SystemExit(f"source receipt hash mismatch: {path}")
    return json.loads(payload), digest


def _family_instances(discovery_receipt, identity_receipt, required_case_ids):
    discovery_cases = {row["id"]: row for row in discovery_receipt["cases"]}
    identity_cases = {row["id"]: row for row in identity_receipt["cases"]}
    instances = []
    for case_id in required_case_ids:
        if case_id not in discovery_cases or case_id not in identity_cases:
            raise ValueError(f"required case is absent: {case_id}")
        discovery = discovery_cases[case_id]
        identity = identity_cases[case_id]
        if discovery["parameters"] != identity["parameters"]:
            raise ValueError(f"case parameters disagree: {case_id}")
        audits = identity["audits"]
        recoveries = discovery["recoveries"]
        for family in identity["families"]:
            audit_index = int(family["representative_audit_index"])
            if audit_index < 0 or audit_index >= len(audits):
                raise ValueError(f"invalid representative audit index: {family['id']}")
            audit = audits[audit_index]
            recovery_index = int(audit["source_recovery_index"])
            if recovery_index < 0 or recovery_index >= len(recoveries):
                raise ValueError(f"invalid source recovery index: {family['id']}")
            recovery = recoveries[recovery_index]
            if not recovery["accepted"]:
                raise ValueError(f"family representative was not accepted: {family['id']}")
            instances.append(
                {
                    "case_id": case_id,
                    "family_id": family["id"],
                    "parameters": discovery["parameters"],
                    "fundamental_lag": int(family["fundamental_lag"]),
                    "fundamental_period_time": float(audit["fundamental_period_time"]),
                    "initial_state": recovery["correction"]["initial_state"],
                    "source_recovery_index": recovery_index,
                    "source_audit_index": audit_index,
                    "family_member_count": len(family["member_audit_indices"]),
                }
            )
    return instances


def _synthetic_validation_inputs(instance):
    branch_id = f"{instance['family_id']}-representative"
    receipt_id = "discovered-primitive-upos"
    parameters = instance["parameters"]
    row = {
        "a": float(parameters["a"]),
        "b": float(parameters["b"]),
        "c": float(parameters["c"]),
        "period_time": float(instance["fundamental_period_time"]),
        "initial_state": list(instance["initial_state"]),
        "audit": {"passed": True},
    }
    receipts = {receipt_id: {"branches": [{"id": branch_id, "rows": [row]}]}}
    family = {
        "id": instance["family_id"],
        "source_receipt_id": receipt_id,
        "source_branch_id": branch_id,
        "fundamental_lag": int(instance["fundamental_lag"]),
    }
    case = {"id": instance["case_id"], "a": float(parameters["a"])}
    return family, case, receipts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.discovered-upo-manifold-seed-manifest.v1":
        raise SystemExit("unsupported discovered-UPO manifold-seed manifest")
    discovery, discovery_hash = _read_hashed(manifest["source_discovery_receipt"])
    identity, identity_hash = _read_hashed(manifest["source_identity_receipt"])
    if identity["source_receipt_sha256"] != discovery_hash:
        raise SystemExit("identity receipt is not bound to the discovery receipt")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    instances = _family_instances(
        discovery, identity, manifest["required_case_ids"]
    )
    solver = SolverConfig(**manifest["reference_solver"])
    started = time.perf_counter()
    rows = []
    for instance in instances:
        family, case, receipts = _synthetic_validation_inputs(instance)
        row = _validate_instance(family, case, receipts, manifest, solver)
        row["source_recovery_index"] = instance["source_recovery_index"]
        row["source_audit_index"] = instance["source_audit_index"]
        row["family_member_count"] = instance["family_member_count"]
        rows.append(row)
        print(
            json.dumps(
                {
                    "case": row["case_id"],
                    "family": row["family_id"],
                    "lag": row["fundamental_lag"],
                    "passed": row["passed"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
    required = set(manifest["required_case_ids"])
    observed = {row["case_id"] for row in rows}
    receipt = {
        "schema": "butterfly.discovered-upo-manifold-seed-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_discovery_receipt_sha256": discovery_hash,
        "source_identity_receipt_sha256": identity_hash,
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "instances": rows,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": bool(rows and observed == required and all(row["passed"] for row in rows)),
        "scientific_scope": (
            "transverse-slice unstable-manifold seed validation, not lobe "
            "inclusion, a connection event, or a continuous topology surface"
        ),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(
        json.dumps(
            {key: value for key, value in receipt.items() if key != "instances"},
            sort_keys=True,
        )
    )
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
