#!/usr/bin/env python3
"""Analyze verified flip spacings and freeze the next cascade prediction."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np

from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if len(args.event) != len(manifest["events"]):
        raise SystemExit("event count does not match manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["dirty"]:
        raise SystemExit("clean source required")
    rows = []
    for specification, path in zip(manifest["events"], args.event):
        receipt_bytes = path.read_bytes()
        if sha256_bytes(receipt_bytes) != specification["receipt_sha256"]:
            raise SystemExit(f"receipt hash mismatch for {specification['experiment_id']}")
        receipt = json.loads(receipt_bytes)
        rows.append(
            {
                "experiment_id": specification["experiment_id"],
                "parent_period": specification["parent_period"],
                "child_period": specification["child_period"],
                "b": float(receipt["b_estimate"]),
                "receipt_sha256": specification["receipt_sha256"],
            }
        )
    b_values = np.asarray([row["b"] for row in rows])
    spacings = b_values[:-1] - b_values[1:]
    ratios = spacings[:-1] / spacings[1:]
    reference = float(manifest["reference_delta"])
    predicted_spacing = float(spacings[-1] / reference)
    predicted_next_b = float(b_values[-1] - predicted_spacing)
    predicted_accumulation_b = float(b_values[-1] - spacings[-1] / (reference - 1.0))
    acceptance = manifest["acceptance"]
    output = {
        "schema": "butterfly.cascade-scaling-analysis.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "events": rows,
        "spacings": spacings.tolist(),
        "spacing_ratios": ratios.tolist(),
        "reference_delta": reference,
        "absolute_ratio_errors": np.abs(ratios - reference).tolist(),
        "prospective_prediction": {
            "next_parent_period": rows[-1]["child_period"],
            "next_child_period": 2 * rows[-1]["child_period"],
            "next_spacing": predicted_spacing,
            "next_b": predicted_next_b,
            "accumulation_b": predicted_accumulation_b,
            "prediction_basis": "last verified spacing divided by frozen reference delta",
        },
        "interpretation_limit": (
            "Two spacing ratios are descriptive and prospective; they do not establish "
            "asymptotic convergence or Feigenbaum universality."
        ),
    }
    output["passed"] = (
        np.all(np.diff(b_values) < 0.0)
        and np.all(np.diff(spacings) < 0.0)
        and np.all(ratios >= acceptance["minimum_spacing_ratio"])
        and np.all(ratios <= acceptance["maximum_spacing_ratio"])
        and abs(ratios[-1] - reference) < abs(ratios[0] - reference)
    )
    atomic_write(args.output, canonical_json(output))
    print(json.dumps(output, sort_keys=True))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
