#!/usr/bin/env python3
"""Build a local (a,c)->b patch of coupled periodic unit events."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy

from butterfly import SolverConfig, correct_unit_multiplier_orbit
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def result_row(a: float, c: float, result: object, *, center: bool = False) -> dict:
    return {
        "a": a,
        "b": result.b,
        "c": c,
        "initial_state": result.initial_state.tolist(),
        "period_time": result.period_time,
        "event_eigenvector": result.eigenvector.tolist(),
        "closure_error": result.closure_error,
        "phase_residual": result.phase_residual,
        "eigen_residual": result.eigen_residual,
        "normalization_residual": result.normalization_residual,
        "flow_orthogonality_residual": result.flow_orthogonality_residual,
        "evaluations": result.evaluations,
        "solver_success": result.success,
        "message": result.message,
        "source_spine_center": center,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-spine", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.unit-event-surface-patch-manifest.v1":
        raise SystemExit("unsupported unit-event surface-patch manifest")
    spine_bytes = args.source_spine.read_bytes()
    if sha256_bytes(spine_bytes) != manifest["source_spine_receipt_sha256"]:
        raise SystemExit("source spine receipt hash does not match manifest")
    spine = json.loads(spine_bytes)
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("surface-patch construction requires clean source")

    a_values = sorted(map(float, manifest["a_values"]))
    c_values = sorted(map(float, manifest["c_values"]))
    center_a = float(spine["fixed_a"])
    if center_a not in a_values:
        raise SystemExit("source spine a must be included in patch")
    spine_by_c = {float(row["c"]): row for row in spine["rows"]}
    if any(c not in spine_by_c for c in c_values):
        raise SystemExit("a requested c value is missing from the source spine")
    solver = SolverConfig(**manifest["solver"])
    corrector = manifest["corrector"]
    started = time.perf_counter()
    rows = []
    slice_status = {}
    for c in c_values:
        source_row = spine_by_c[c]
        center = {
            "a": center_a,
            "b": float(source_row["b"]),
            "c": c,
            "initial_state": source_row["initial_state"],
            "period_time": float(source_row["period_time"]),
            "event_eigenvector": source_row["event_eigenvector"],
            "closure_error": float(source_row["closure_error"]),
            "phase_residual": float(source_row["phase_residual"]),
            "eigen_residual": float(source_row["eigen_residual"]),
            "normalization_residual": float(source_row["normalization_residual"]),
            "flow_orthogonality_residual": float(source_row["flow_orthogonality_residual"]),
            "evaluations": int(source_row["evaluations"]),
            "solver_success": bool(source_row["solver_success"]),
            "message": "source spine center",
            "source_spine_center": True,
        }
        slice_rows = {center_a: center}
        statuses = {}
        for direction, targets in (
            ("down", sorted((a for a in a_values if a < center_a), reverse=True)),
            ("up", sorted(a for a in a_values if a > center_a)),
        ):
            previous = center
            completed = True
            message = "completed"
            for a in targets:
                try:
                    result = correct_unit_multiplier_orbit(
                        a=a,
                        c=c,
                        initial_b=float(previous["b"]),
                        initial_state=previous["initial_state"],
                        period_time=float(previous["period_time"]),
                        config=solver,
                        max_evaluations=int(corrector["max_evaluations"]),
                        tolerance=float(corrector["tolerance"]),
                    )
                except Exception as error:
                    completed = False
                    message = f"{type(error).__name__}: {error}"
                    break
                row = result_row(a, c, result)
                slice_rows[a] = row
                previous = row
                if not result.success:
                    completed = False
                    message = result.message
                    break
            statuses[direction] = {"completed": completed, "message": message}
        rows.extend(slice_rows[a] for a in a_values if a in slice_rows)
        slice_status[str(c)] = statuses

    by_coordinate = {(row["a"], row["c"]): row for row in rows}
    adjacent_jumps = []
    for c in c_values:
        adjacent_jumps.extend(
            abs(by_coordinate[(right, c)]["b"] - by_coordinate[(left, c)]["b"])
            for left, right in zip(a_values[:-1], a_values[1:], strict=True)
            if (left, c) in by_coordinate and (right, c) in by_coordinate
        )
    for a in a_values:
        adjacent_jumps.extend(
            abs(by_coordinate[(a, right)]["b"] - by_coordinate[(a, left)]["b"])
            for left, right in zip(c_values[:-1], c_values[1:], strict=True)
            if (a, left) in by_coordinate and (a, right) in by_coordinate
        )
    max_closure = max(row["closure_error"] for row in rows)
    max_eigen = max(row["eigen_residual"] for row in rows)
    max_orthogonality = max(row["flow_orthogonality_residual"] for row in rows)
    b_guard = list(map(float, manifest["b_guard"]))
    acceptance = manifest["acceptance"]
    passed = bool(
        len(rows) == int(acceptance["required_points"])
        and all(row["solver_success"] for row in rows)
        and all(b_guard[0] <= row["b"] <= b_guard[1] for row in rows)
        and max_closure <= float(acceptance["max_closure_error"])
        and max_eigen <= float(acceptance["max_eigen_residual"])
        and max_orthogonality
        <= float(acceptance["max_flow_orthogonality_residual"])
        and max(adjacent_jumps, default=0.0)
        <= float(acceptance["max_adjacent_b_jump"])
    )
    receipt = {
        "schema": "butterfly.unit-event-surface-patch-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_spine_receipt_sha256": sha256_bytes(spine_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "a_values": a_values,
        "c_values": c_values,
        "rows": sorted(rows, key=lambda row: (row["c"], row["a"])),
        "point_count": len(rows),
        "slice_status": slice_status,
        "b_range": [min(row["b"] for row in rows), max(row["b"] for row in rows)],
        "max_adjacent_b_jump": max(adjacent_jumps, default=0.0),
        "max_closure_error": max_closure,
        "max_eigen_residual": max_eigen,
        "max_flow_orthogonality_residual": max_orthogonality,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "interpretation_limit": "A local graph patch is not a global fold-safe surface or evidence of uniform normal form/topology.",
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps({key: value for key, value in receipt.items() if key not in ("rows", "slice_status")}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
