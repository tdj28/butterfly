#!/usr/bin/env python3
"""Switch and qualify period-12 children on the returning period-6 flip arm."""

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
from scripts.qualify_jones_period12_children import _qualify_target
from scripts.switch_jones_period6_flip_curve import _switch_event


SCHEMA = "butterfly.jones-returning-period12-child-qualification-manifest.v1"


def parameter_side(candidate_a, event_a, tolerance=1e-12):
    """Classify a candidate relative to its parent flip event."""

    difference = float(candidate_a) - float(event_a)
    if abs(difference) <= float(tolerance):
        return 0
    return 1 if difference > 0.0 else -1


def _event_result(source_row, manifest, switch_solver, qualification_solvers):
    switched = _switch_event(source_row, manifest, switch_solver)
    event_a = float(switched["event_a"])
    expected_side = int(manifest["prediction"]["stable_child_parameter_side"])
    candidates = []
    for branch in switched["branches"]:
        for row_index, candidate in enumerate(branch["rows"]):
            side = parameter_side(candidate["a"], event_a)
            record = {
                "source_direction": int(branch["direction"]),
                "source_row_index": row_index,
                "candidate_a": float(candidate["a"]),
                "parameter_side": side,
                "expected_parameter_side": side == expected_side,
                "switch_candidate": candidate,
            }
            try:
                qualified = _qualify_target(
                    {
                        "c": switched["c"],
                        "candidate_a": candidate["a"],
                        "source_direction": branch["direction"],
                    },
                    switched,
                    candidate,
                    manifest,
                    qualification_solvers,
                )
            except Exception as error:
                record["qualification_error"] = f"{type(error).__name__}: {error}"
                record["qualified"] = None
                record["passed"] = False
            else:
                record["qualified"] = qualified
                record["passed"] = bool(
                    record["expected_parameter_side"] and qualified["passed"]
                )
            candidates.append(record)
    passed_candidates = [candidate for candidate in candidates if candidate["passed"]]
    return {
        "c": float(switched["c"]),
        "event_a": event_a,
        "source_row": source_row,
        "switch": switched,
        "candidate_count": len(candidates),
        "qualified_expected_side_count": len(passed_candidates),
        "candidates": candidates,
        "passed": len(passed_candidates)
        >= int(manifest["acceptance"]["minimum_children_per_event"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported returning-arm child manifest")
    source_bytes = args.source_receipt.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash mismatch")
    source_receipt = json.loads(source_bytes)
    if not source_receipt.get("passed"):
        raise SystemExit("returning-arm source receipt must have passed")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("returning-arm child qualification requires clean source")

    lookup = {float(row["c"]): row for row in source_receipt["rows"]}
    selected = [lookup[float(value)] for value in manifest["event_c_values"]]
    switch_solver = SolverConfig(**manifest["solver"])
    qualification_solvers = (
        SolverConfig(**manifest["reference_solver"]),
        SolverConfig(**manifest["independent_solver"]),
    )
    started = time.perf_counter()
    events = [
        _event_result(row, manifest, switch_solver, qualification_solvers)
        for row in selected
    ]
    passed = bool(
        len(events) == int(manifest["acceptance"]["required_events"])
        and all(event["passed"] for event in events)
    )
    output = {
        "schema": "butterfly.jones-returning-period12-child-qualification-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_receipt_sha256": sha256_bytes(source_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "prediction": manifest["prediction"],
        "events": events,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    print(json.dumps({
        "output": str(args.output),
        "sha256": sha256_bytes(output_bytes),
        "passed": passed,
        "events": [
            {
                "c": event["c"],
                "event_a": event["event_a"],
                "candidate_count": event["candidate_count"],
                "qualified_expected_side_count": event[
                    "qualified_expected_side_count"
                ],
                "passed": event["passed"],
            }
            for event in events
        ],
    }, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
