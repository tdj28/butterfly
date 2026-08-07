#!/usr/bin/env python3
"""Trace fold-safe fixed-c slices of the double-covered flip surface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy

from butterfly import SolverConfig
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from pseudo_arclength_unit_event import correct_event_arclength, source_variables


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-surface", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.flip-surface-slices-manifest.v1":
        raise SystemExit("unsupported flip-surface slices manifest")
    surface_bytes = args.source_surface.read_bytes()
    if sha256_bytes(surface_bytes) != manifest["source_surface_receipt_sha256"]:
        raise SystemExit("source surface receipt hash does not match manifest")
    surface = json.loads(surface_bytes)
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("flip-surface slice tracing requires clean source")

    solver = SolverConfig(**manifest["solver"])
    continuation = manifest["continuation"]
    corrector = manifest["corrector"]
    acceptance = manifest["acceptance"]
    requested_c = list(map(float, manifest["c_values"]))
    seed_a_values = list(map(float, manifest["seed_a_values"]))
    source_rows = [row for row in surface["rows"] if row["solver_success"]]
    started = time.perf_counter()
    slices = []

    for c in requested_c:
        seeds = []
        for target_a in seed_a_values:
            candidates = [
                row
                for row in source_rows
                if abs(float(row["c"]) - c) < 1e-12
                and abs(float(row["a"]) - target_a) < 1e-12
            ]
            if len(candidates) != 1:
                raise SystemExit(f"missing unique source seed at a={target_a}, c={c}")
            seeds.append(source_variables(candidates[0]))
        if np.dot(seeds[0][6:9], seeds[1][6:9]) < 0.0:
            seeds[1][6:9] *= -1.0
        points = [seeds[0], seeds[1]]
        step_length = float(continuation["step_scale"]) * np.linalg.norm(
            seeds[1] - seeds[0]
        )
        rows = []
        statuses = []
        for step_index in range(int(continuation["steps"])):
            tangent = points[-1] - points[-2]
            tangent /= np.linalg.norm(tangent)
            predictor = points[-1] + step_length * tangent
            corrected, status = correct_event_arclength(
                predictor,
                tangent,
                points[-1],
                c=c,
                solver=solver,
                tolerance=float(corrector["tolerance"]),
                max_evaluations=int(corrector["max_evaluations"]),
            )
            status["step_index"] = step_index
            statuses.append(status)
            if not status["success"]:
                break
            if np.dot(corrected[6:9], points[-1][6:9]) < 0.0:
                corrected[6:9] *= -1.0
            points.append(corrected)
            rows.append(
                {
                    "initial_state": corrected[:3].tolist(),
                    "period_time": float(corrected[3]),
                    "a": float(corrected[4]),
                    "b": float(corrected[5]),
                    "c": c,
                    "event_eigenvector": corrected[6:9].tolist(),
                    **status,
                }
            )
            a_guard = list(map(float, continuation["a_guard"]))
            b_guard = list(map(float, continuation["b_guard"]))
            if not (
                a_guard[0] <= corrected[4] <= a_guard[1]
                and b_guard[0] <= corrected[5] <= b_guard[1]
            ):
                break

        combined_a = np.asarray([seed[4] for seed in seeds] + [row["a"] for row in rows])
        combined_b = np.asarray([seed[5] for seed in seeds] + [row["b"] for row in rows])
        a_differences = np.diff(combined_a)
        b_differences = np.diff(combined_b)
        max_closure = max((row["closure_error"] for row in rows), default=float("inf"))
        max_eigen = max((row["eigen_residual"] for row in rows), default=float("inf"))
        max_orthogonality = max(
            (row["flow_orthogonality_residual"] for row in rows), default=float("inf")
        )
        max_arclength = max(
            (row["arclength_residual"] for row in rows), default=float("inf")
        )
        slice_result = {
            "c": c,
            "step_length": step_length,
            "seed_variables": [seed.tolist() for seed in seeds],
            "rows": rows,
            "statuses": statuses,
            "corrected_point_count": len(rows),
            "a_range": [float(np.min(combined_a)), float(np.max(combined_a))],
            "b_range": [float(np.min(combined_b)), float(np.max(combined_b))],
            "direction_reversals_in_a": int(
                np.sum(a_differences[:-1] * a_differences[1:] < 0.0)
            ),
            "direction_reversals_in_b": int(
                np.sum(b_differences[:-1] * b_differences[1:] < 0.0)
            ),
            "max_closure_error": max_closure,
            "max_eigen_residual": max_eigen,
            "max_flow_orthogonality_residual": max_orthogonality,
            "max_arclength_residual": max_arclength,
        }
        slice_result["passed"] = bool(
            len(rows) >= int(acceptance["minimum_points_per_slice"])
            and slice_result["a_range"][0] <= float(acceptance["required_maximum_min_a"])
            and max_closure <= float(acceptance["max_closure_error"])
            and max_eigen <= float(acceptance["max_eigen_residual"])
            and max_orthogonality
            <= float(acceptance["max_flow_orthogonality_residual"])
            and max_arclength <= float(acceptance["max_arclength_residual"])
        )
        slices.append(slice_result)

    reversal_slices = sum(
        result["direction_reversals_in_b"] >= 1 for result in slices
    )
    receipt = {
        "schema": "butterfly.flip-surface-slices-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_surface_receipt_sha256": sha256_bytes(surface_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "slices": slices,
        "slice_count": len(slices),
        "passed_slice_count": sum(result["passed"] for result in slices),
        "slices_with_b_reversal": reversal_slices,
        "passed": bool(
            all(result["passed"] for result in slices)
            and reversal_slices
            >= int(acceptance["minimum_slices_with_b_reversal"])
        ),
        "elapsed_seconds": time.perf_counter() - started,
        "interpretation_limit": "Five fixed-c fold-safe traces establish a local strip of a flip surface, not its global connectivity or alignment with every atlas window.",
    }
    atomic_write(args.output, canonical_json(receipt))
    summary = {key: value for key, value in receipt.items() if key != "slices"}
    summary["slice_summaries"] = [
        {key: value for key, value in result.items() if key not in ("rows", "statuses", "seed_variables")}
        for result in slices
    ]
    print(json.dumps(summary, sort_keys=True))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
