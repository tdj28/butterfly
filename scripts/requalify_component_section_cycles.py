#!/usr/bin/env python3
"""Requalify corrected candidates for a frozen target-section phase count."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from butterfly.scan import atomic_write, canonical_json, sha256_bytes


SCHEMA = "butterfly.component-section-cycle-requalification-manifest.v1"


def requalify_candidate(candidate: dict, *, expected_count: int, section_kind: str) -> dict:
    """Apply a declared section-count correction without changing orbit data."""

    output = dict(candidate)
    original_checks = candidate.get("checks")
    states = np.asarray(candidate.get("section_states", ()), dtype=float)
    if not isinstance(original_checks, dict):
        output["passed"] = False
        output["requalification"] = {"reason": "original orbit checks are absent"}
        return output
    checks = dict(original_checks)
    checks["barrio_crossing_count"] = bool(
        candidate.get("section", {}).get("kind") == section_kind
        and candidate.get("section", {}).get("crossing_count") == expected_count
        and states.shape == (expected_count, 3)
        and np.all(np.isfinite(states))
    )
    output["checks"] = checks
    output["passed"] = all(checks.values())
    output["requalification"] = {
        "original_passed": bool(candidate.get("passed")),
        "expected_section_kind": section_kind,
        "expected_section_crossing_count": expected_count,
        "changed_check": "barrio_crossing_count",
        "orbit_data_changed": False,
    }
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported section-cycle requalification manifest")
    for evidence in manifest.get("evidence", ()):
        raw = Path(evidence["path"]).read_bytes()
        if sha256_bytes(raw) != evidence["sha256"]:
            raise SystemExit(f"evidence hash mismatch: {evidence['path']}")
    input_path = Path(manifest["input"]["path"])
    input_bytes = input_path.read_bytes()
    if sha256_bytes(input_bytes) != manifest["input"]["sha256"]:
        raise SystemExit("input candidate hash mismatch")
    original = json.loads(input_bytes)
    expected_count = int(manifest["section"]["expected_crossing_count"])
    section_name = str(manifest["section"]["kind"])
    candidates = [
        requalify_candidate(
            candidate,
            expected_count=expected_count,
            section_kind=section_name,
        )
        for candidate in original["candidates"]
    ]
    passed_count = sum(candidate["passed"] for candidate in candidates)
    output = {
        "schema": "butterfly.component-section-cycle-requalification.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "input_sha256": sha256_bytes(input_bytes),
        "section": manifest["section"],
        "original_candidate_count": len(candidates),
        "passed_candidate_count": passed_count,
        "candidates": candidates,
        "passed": passed_count
        >= int(manifest["acceptance"]["minimum_passed_candidates"]),
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": sha256_bytes(output_bytes),
                "passed": output["passed"],
                "passed_candidate_count": passed_count,
            },
            sort_keys=True,
        )
    )
    return 0 if output["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
