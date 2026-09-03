#!/usr/bin/env python3
"""Select candidates with a frozen cross-step oracle-vote pattern."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from butterfly.scan import atomic_write, canonical_json, sha256_bytes


SCHEMA = "butterfly.smoothing-sensitive-candidate-selection-manifest.v1"


def matching_ids(receipt: dict, selection: dict) -> list[str]:
    """Return IDs matching the declared variant-count pattern at every step."""

    baseline = tuple(int(value) for value in selection["baseline_variant_indices"])
    smoothing_index = int(selection["smoothing_variant_index"])
    baseline_count = int(selection["baseline_branch_count"])
    smoothing_count = int(selection["smoothing_branch_count"])
    profiles = [{row["id"]: row for row in profile["rows"]} for profile in receipt["profiles"]]
    common_ids = set(profiles[0])
    for profile in profiles[1:]:
        common_ids &= set(profile)
    selected = []
    for identifier in sorted(common_ids):
        votes = [profile[identifier]["robust_partition"]["variant_counts"] for profile in profiles]
        if all(
            all(vote[index] == baseline_count for index in baseline)
            and vote[smoothing_index] == smoothing_count
            for vote in votes
        ):
            selected.append(identifier)
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported smoothing-sensitive selection manifest")
    receipt_bytes = Path(manifest["receipt"]["path"]).read_bytes()
    candidate_bytes = Path(manifest["candidate_input"]["path"]).read_bytes()
    if sha256_bytes(receipt_bytes) != manifest["receipt"]["sha256"]:
        raise SystemExit("receipt hash mismatch")
    if sha256_bytes(candidate_bytes) != manifest["candidate_input"]["sha256"]:
        raise SystemExit("candidate input hash mismatch")
    receipt = json.loads(receipt_bytes)
    source = json.loads(candidate_bytes)
    ids = matching_ids(receipt, manifest["selection"])
    lookup = {row["id"]: row for row in source["candidates"]}
    candidates = [lookup[identifier] for identifier in ids]
    if any(not row.get("passed") for row in candidates):
        raise SystemExit("selection contains an unqualified source candidate")
    if len(candidates) != int(manifest["expected_candidate_count"]):
        raise SystemExit(
            f"selected {len(candidates)} candidates; expected {manifest['expected_candidate_count']}"
        )
    output = {
        "schema": "butterfly.smoothing-sensitive-candidate-selection.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "receipt_sha256": sha256_bytes(receipt_bytes),
        "candidate_input_sha256": sha256_bytes(candidate_bytes),
        "selection": manifest["selection"],
        "candidate_count": len(candidates),
        "candidates": candidates,
        "scientific_data_changed": False,
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "output_bytes": len(output_bytes),
                "sha256": sha256_bytes(output_bytes),
                "candidate_count": len(candidates),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
