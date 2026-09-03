#!/usr/bin/env python3
"""Select a frozen parameter rectangle from a qualified orbit artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from butterfly.scan import atomic_write, canonical_json, sha256_bytes


SCHEMA = "butterfly.local-barrio-candidate-selection-manifest.v1"


def select_candidates(rows: list[dict], selection: dict) -> list[dict]:
    """Return passed candidates inside the closed frozen parameter bounds."""

    a_lower, a_upper = map(float, selection["a_range"])
    c_lower, c_upper = map(float, selection["c_range"])
    b_value = float(selection["b"])
    if not a_lower < a_upper or not c_lower < c_upper:
        raise ValueError("selection ranges must be increasing")
    selected = [
        row
        for row in rows
        if row.get("passed")
        and a_lower <= float(row["parameters"]["a"]) <= a_upper
        and c_lower <= float(row["parameters"]["c"]) <= c_upper
        and abs(float(row["parameters"]["b"]) - b_value) <= 1e-14
    ]
    return sorted(selected, key=lambda row: (tuple(row["grid_index"]), row["id"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported candidate-selection manifest")
    input_declaration = manifest["input"]
    input_path = Path(input_declaration["path"])
    input_bytes = input_path.read_bytes()
    if sha256_bytes(input_bytes) != input_declaration["sha256"]:
        raise SystemExit("candidate input hash mismatch")
    document = json.loads(input_bytes)
    candidates = select_candidates(document["candidates"], manifest["selection"])
    if len(candidates) != int(manifest["expected_candidate_count"]):
        raise SystemExit(
            f"selected {len(candidates)} candidates; "
            f"expected {manifest['expected_candidate_count']}"
        )
    output = {
        "schema": "butterfly.local-barrio-candidate-selection.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "input_sha256": sha256_bytes(input_bytes),
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
