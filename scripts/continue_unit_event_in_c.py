#!/usr/bin/env python3
"""Continue a coupled periodic unit-multiplier event across c values."""

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


def result_row(c: float, result: object) -> dict:
    return {
        "c": c,
        "b": result.b,
        "initial_state": result.initial_state.tolist(),
        "period_time": result.period_time,
        "event_eigenvector": result.eigenvector.tolist(),
        "closure_error": result.closure_error,
        "phase_residual": result.phase_residual,
        "eigen_residual": result.eigen_residual,
        "normalization_residual": result.normalization_residual,
        "flow_orthogonality_residual": result.flow_orthogonality_residual,
        "multipliers": [
            {"real": float(value.real), "imag": float(value.imag), "modulus": float(abs(value))}
            for value in result.multipliers
        ],
        "evaluations": result.evaluations,
        "solver_success": result.success,
        "message": result.message,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-event", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.unit-event-c-spine-manifest.v1":
        raise SystemExit("unsupported unit-event c-spine manifest")
    event_bytes = args.source_event.read_bytes()
    if sha256_bytes(event_bytes) != manifest["source_event_receipt_sha256"]:
        raise SystemExit("source event receipt hash does not match manifest")
    event = json.loads(event_bytes)
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("unit-event c continuation requires clean source")

    c_values = sorted(map(float, manifest["c_values"]))
    center_c = float(event["fixed_c"])
    if center_c not in c_values:
        raise SystemExit("source event c must be included in c_values")
    center_row = {
        "c": center_c,
        "b": float(event["corrected_b"]),
        "initial_state": event["initial_state"],
        "period_time": float(event["period_time"]),
        "event_eigenvector": event["event_eigenvector"],
        "closure_error": float(event["closure_error"]),
        "phase_residual": float(event["phase_residual"]),
        "eigen_residual": float(event["eigen_residual"]),
        "normalization_residual": float(event["normalization_residual"]),
        "flow_orthogonality_residual": float(event["flow_orthogonality_residual"]),
        "multipliers": event["multipliers"],
        "evaluations": int(event["evaluations"]),
        "solver_success": bool(event["solver_success"]),
        "message": "source event",
    }
    solver = SolverConfig(**manifest["solver"])
    corrector = manifest["corrector"]
    started = time.perf_counter()
    rows_by_c = {center_c: center_row}
    direction_status = {}
    for direction, targets in (
        ("down", sorted((c for c in c_values if c < center_c), reverse=True)),
        ("up", sorted(c for c in c_values if c > center_c)),
    ):
        previous = center_row
        completed = True
        message = "completed"
        for target_c in targets:
            try:
                result = correct_unit_multiplier_orbit(
                    a=float(manifest["fixed_a"]),
                    c=target_c,
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
            row = result_row(target_c, result)
            rows_by_c[target_c] = row
            previous = row
            if not result.success:
                completed = False
                message = result.message
                break
        direction_status[direction] = {"completed": completed, "message": message}

    rows = [rows_by_c[c] for c in c_values if c in rows_by_c]
    adjacent_b_jumps = [
        abs(float(right["b"]) - float(left["b"]))
        for left, right in zip(rows[:-1], rows[1:], strict=True)
    ]
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
        and max(adjacent_b_jumps, default=0.0)
        <= float(acceptance["max_adjacent_b_jump"])
    )
    receipt = {
        "schema": "butterfly.unit-event-c-spine-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_event_receipt_sha256": sha256_bytes(event_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "fixed_a": float(manifest["fixed_a"]),
        "rows": rows,
        "point_count": len(rows),
        "direction_status": direction_status,
        "c_range": [min(row["c"] for row in rows), max(row["c"] for row in rows)],
        "b_range": [min(row["b"] for row in rows), max(row["b"] for row in rows)],
        "max_adjacent_b_jump": max(adjacent_b_jumps, default=0.0),
        "max_closure_error": max_closure,
        "max_eigen_residual": max_eigen,
        "max_flow_orthogonality_residual": max_orthogonality,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "interpretation_limit": "A one-dimensional c-spine is not yet the full event surface or evidence of uniform normal form.",
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps({key: value for key, value in receipt.items() if key != "rows"}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
