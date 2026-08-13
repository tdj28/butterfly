#!/usr/bin/env python3
"""Bridge the first returning-arm child interval with frozen fine substeps."""

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
from scripts.continue_jones_returning_period12_child import (
    _continue_row,
    select_seed,
)
from scripts.qualify_jones_period12_children import _qualify_target


SCHEMA = "butterfly.jones-returning-period12-child-bridge-manifest.v1"


def interpolate_event(left, right, fraction):
    """Linearly interpolate a phase-aligned event seed in parameter arclength."""

    fraction = float(fraction)
    return {
        "a": (1.0 - fraction) * float(left["a"]) + fraction * float(right["a"]),
        "b": (1.0 - fraction) * float(left["b"]) + fraction * float(right["b"]),
        "c": (1.0 - fraction) * float(left["c"]) + fraction * float(right["c"]),
        "initial_state": (
            (1.0 - fraction) * np.asarray(left["initial_state"], dtype=float)
            + fraction * np.asarray(right["initial_state"], dtype=float)
        ).tolist(),
        "period_time": (1.0 - fraction) * float(left["period_time"])
        + fraction * float(right["period_time"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event-receipt", type=Path, required=True)
    parser.add_argument("--seed-receipt", type=Path, required=True)
    parser.add_argument("--failure-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported returning-child bridge manifest")
    input_paths = {
        "event": args.event_receipt,
        "seed": args.seed_receipt,
        "failure": args.failure_receipt,
    }
    input_bytes = {name: path.read_bytes() for name, path in input_paths.items()}
    for name, data in input_bytes.items():
        if sha256_bytes(data) != manifest[f"{name}_receipt_sha256"]:
            raise SystemExit(f"{name} receipt hash mismatch")
    events_receipt = json.loads(input_bytes["event"])
    seed_receipt = json.loads(input_bytes["seed"])
    failure_receipt = json.loads(input_bytes["failure"])
    if not events_receipt.get("passed") or failure_receipt.get("passed"):
        raise SystemExit("bridge requires the passed arm and failed coarse continuation")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("returning-child bridge requires clean source")

    seed_event, seed_candidate = select_seed(seed_receipt, manifest["seed_selector"])
    seed_child = seed_candidate["qualified"]["independent_radau"]["child"]
    delta_a = float(seed_candidate["candidate_a"]) - float(seed_event["event_a"])
    lookup = {float(row["c"]): row for row in events_receipt["rows"]}
    left = lookup[float(manifest["bridge"]["left_c"])]
    right = lookup[float(manifest["bridge"]["right_c"])]
    fractions = np.linspace(
        0.0, 1.0, int(manifest["bridge"]["subinterval_count"]) + 1
    )
    interpolated_events = [interpolate_event(left, right, value) for value in fractions]
    solver = SolverConfig(**manifest["solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    rows = []
    failure = None
    current_child = seed_child
    started = time.perf_counter()
    for index, event in enumerate(interpolated_events):
        try:
            row = _continue_row(event, current_child, delta_a, manifest, solver)
        except Exception as error:
            failure = {
                "index": index,
                "fraction": float(fractions[index]),
                "c": float(event["c"]),
                "error": f"{type(error).__name__}: {error}",
            }
            break
        if not row["passed"]:
            failure = {
                "index": index,
                "fraction": float(fractions[index]),
                "c": float(event["c"]),
                "error": "bridge row failed identity or stability checks",
                "checks": row["checks"],
                "row": row,
            }
            break
        rows.append(row)
        current_child = row["child"]
    controls = []
    if rows:
        for index in manifest["independent_control_indices"]:
            if int(index) >= len(rows):
                continue
            event = interpolated_events[int(index)]
            row = rows[int(index)]
            qualified = _qualify_target(
                {
                    "c": row["c"],
                    "candidate_a": row["a"],
                    "source_direction": -1,
                },
                {
                    "c": row["c"],
                    "event_a": event["a"],
                    "event_variables": [
                        *event["initial_state"],
                        2.0 * float(event["period_time"]),
                        float(event["a"]),
                    ],
                },
                {
                    "initial_state": row["child"]["initial_state"],
                    "period_time": row["child"]["period_time"],
                },
                manifest,
                (solver, independent_solver),
            )
            controls.append({"index": int(index), **qualified})
    adjacent_state = [
        float(
            np.linalg.norm(
                np.asarray(right_row["child"]["initial_state"])
                - np.asarray(left_row["child"]["initial_state"])
            )
        )
        for left_row, right_row in zip(rows[:-1], rows[1:], strict=True)
    ]
    acceptance = manifest["acceptance"]
    passed = bool(
        len(rows) == len(interpolated_events)
        and failure is None
        and max(adjacent_state, default=0.0)
        <= float(acceptance["maximum_adjacent_child_state_distance"])
        and len(controls) == len(manifest["independent_control_indices"])
        and all(control["passed"] for control in controls)
    )
    output = {
        "schema": "butterfly.jones-returning-period12-child-bridge-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        **{
            f"{name}_receipt_sha256": sha256_bytes(data)
            for name, data in input_bytes.items()
        },
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "delta_a": delta_a,
        "fractions": fractions.tolist(),
        "rows": rows,
        "failure": failure,
        "maximum_adjacent_child_state_distance": max(adjacent_state, default=0.0),
        "independent_controls": controls,
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
        "point_count": len(rows),
        "target_point_count": len(interpolated_events),
        "c_range": [rows[0]["c"], rows[-1]["c"]] if rows else [None, None],
        "failure": failure,
    }, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
