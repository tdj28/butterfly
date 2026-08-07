#!/usr/bin/env python3
"""Continue a coupled periodic-orbit unit-multiplier event across a values."""

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


def result_row(a: float, result: object) -> dict:
    return {
        "a": a,
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
    if manifest.get("schema") != "butterfly.unit-event-curve-manifest.v1":
        raise SystemExit("unsupported unit-event curve manifest")
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
        raise SystemExit("unit-event continuation requires clean source")

    a_values = sorted(map(float, manifest["a_values"]))
    center_a = float(event["fixed_a"])
    if center_a not in a_values:
        raise SystemExit("source event a must be included in a_values")
    center_row = {
        "a": center_a,
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
    rows_by_a = {center_a: center_row}
    direction_status = {}
    for direction, targets in (
        ("down", sorted((a for a in a_values if a < center_a), reverse=True)),
        ("up", sorted(a for a in a_values if a > center_a)),
    ):
        previous = center_row
        completed = True
        message = "completed"
        for target_a in targets:
            try:
                result = correct_unit_multiplier_orbit(
                    a=target_a,
                    c=float(manifest["fixed_c"]),
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
            row = result_row(target_a, result)
            rows_by_a[target_a] = row
            previous = row
            if not result.success:
                completed = False
                message = result.message
                break
        direction_status[direction] = {"completed": completed, "message": message}

    rows = [rows_by_a[a] for a in a_values if a in rows_by_a]
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
        "schema": "butterfly.unit-event-curve-receipt.v1",
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
        "fixed_c": float(manifest["fixed_c"]),
        "rows": rows,
        "point_count": len(rows),
        "direction_status": direction_status,
        "a_range": [min(row["a"] for row in rows), max(row["a"] for row in rows)],
        "b_range": [min(row["b"] for row in rows), max(row["b"] for row in rows)],
        "max_adjacent_b_jump": max(adjacent_b_jumps, default=0.0),
        "max_closure_error": max_closure,
        "max_eigen_residual": max_eigen,
        "max_flow_orthogonality_residual": max_orthogonality,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "interpretation_limit": "A fixed-c event curve is not yet a three-parameter surface or evidence that the same local normal form persists along it.",
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps({key: value for key, value in receipt.items() if key != "rows"}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
