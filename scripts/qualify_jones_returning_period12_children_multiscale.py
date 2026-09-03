#!/usr/bin/env python3
"""Re-correct returning flip events and probe period-12 children at fixed scales."""

from __future__ import annotations

import argparse
import copy
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from butterfly import SolverConfig
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.continue_jones_period6_flip_curve import _solve_event
from scripts.qualify_jones_period12_children import _qualify_target
from scripts.qualify_jones_returning_period12_children import parameter_side
from scripts.switch_jones_period6_flip_curve import _switch_event


SCHEMA = "butterfly.jones-returning-period12-child-multiscale-manifest.v1"


def _qualify_candidate(candidate, branch, switched, manifest, solvers):
    event_a = float(switched["event_a"])
    side = parameter_side(candidate["a"], event_a)
    expected_side = int(manifest["prediction"]["stable_child_parameter_side"])
    record = {
        "source_direction": int(branch["direction"]),
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
            solvers,
        )
    except Exception as error:
        record["qualification_error"] = f"{type(error).__name__}: {error}"
        record["qualified"] = None
        record["passed"] = False
    else:
        record["qualified"] = qualified
        record["passed"] = bool(record["expected_parameter_side"] and qualified["passed"])
    return record


def _event_result(source_row, manifest, switch_solver, event_solver, solvers):
    exact = _solve_event(float(source_row["c"]), source_row, manifest, event_solver)
    if not exact["passed"]:
        return {
            "c": float(source_row["c"]),
            "source_row": source_row,
            "exact_event": exact,
            "switches": [],
            "candidates": [],
            "candidate_count": 0,
            "qualified_expected_side_count": 0,
            "passed": False,
        }
    switches = []
    candidates = []
    for step_length in manifest["switch_step_lengths"]:
        local_manifest = copy.deepcopy(manifest)
        local_manifest["continuation"]["step_length"] = float(step_length)
        try:
            switched = _switch_event(exact, local_manifest, switch_solver)
        except Exception as error:
            switches.append(
                {
                    "step_length": float(step_length),
                    "error": f"{type(error).__name__}: {error}",
                    "switch": None,
                }
            )
            continue
        switch_record = {
            "step_length": float(step_length),
            "error": None,
            "switch": switched,
        }
        switches.append(switch_record)
        for branch in switched["branches"]:
            for row_index, candidate in enumerate(branch["rows"]):
                record = _qualify_candidate(
                    candidate, branch, switched, manifest, solvers
                )
                record["step_length"] = float(step_length)
                record["source_row_index"] = row_index
                candidates.append(record)
    passed_candidates = [candidate for candidate in candidates if candidate["passed"]]
    return {
        "c": float(source_row["c"]),
        "event_a": float(exact["a"]),
        "source_row": source_row,
        "exact_event": exact,
        "switches": switches,
        "candidates": candidates,
        "candidate_count": len(candidates),
        "qualified_expected_side_count": len(passed_candidates),
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
        raise SystemExit("unsupported multiscale returning-child manifest")
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
        raise SystemExit("multiscale returning-child qualification requires clean source")
    lookup = {float(row["c"]): row for row in source_receipt["rows"]}
    selected = [lookup[float(value)] for value in manifest["event_c_values"]]
    switch_solver = SolverConfig(**manifest["solver"])
    event_solver = SolverConfig(**manifest["event_solver"])
    solvers = (
        SolverConfig(**manifest["reference_solver"]),
        SolverConfig(**manifest["independent_solver"]),
    )
    started = time.perf_counter()
    events = [
        _event_result(row, manifest, switch_solver, event_solver, solvers)
        for row in selected
    ]
    passed = bool(
        len(events) == int(manifest["acceptance"]["required_events"])
        and all(event["passed"] for event in events)
    )
    output = {
        "schema": "butterfly.jones-returning-period12-child-multiscale-receipt.v1",
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
                "exact_event_passed": event["exact_event"]["passed"],
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
