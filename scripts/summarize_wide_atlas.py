#!/usr/bin/env python3
"""Summarize a verified tiled scan into periodic components and candidates."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from butterfly import periodic_components, ranked_recurrence_candidates
from butterfly.scan import atomic_write, canonical_json, sha256_bytes
from butterfly.tiles import verify_completed_aggregate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aggregate-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--candidate-limit", type=int, default=100)
    args = parser.parse_args()

    receipt = verify_completed_aggregate(args.aggregate_dir)
    result_path = args.aggregate_dir / "result.json"
    result_bytes = result_path.read_bytes()
    result = json.loads(result_bytes)
    components = periodic_components(result)
    candidates = ranked_recurrence_candidates(
        result, limit=args.candidate_limit, exclude_periodic=True
    )
    summary = {
        "schema": "butterfly.wide-atlas-summary.v1",
        "experiment_id": result["experiment_id"],
        "source_result_sha256": sha256_bytes(result_bytes),
        "source_plan_hash": result["plan_hash"],
        "source_aggregate_receipt_sha256": sha256_bytes(
            (args.aggregate_dir / "receipt.json").read_bytes()
        ),
        "shape": result["shape"],
        "component_count": len(components),
        "components": [asdict(component) for component in components],
        "ranked_unresolved_candidates": list(candidates),
        "interpretation_limit": (
            "Grid components and near-recurrences are discovery candidates, not "
            "evidence of continuous shrimp families or asymptotic classification."
        ),
        "verified_aggregate": {
            "row_count": receipt["row_count"],
            "result_sha256": receipt["result_sha256"],
        },
    }
    atomic_write(args.output, canonical_json(summary))
    print(
        json.dumps(
            {
                "output": str(args.output),
                "component_count": len(components),
                "candidate_count": len(candidates),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
