#!/usr/bin/env python3
"""Reaudit EXP-254 sign identity with continuous phase minimization."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from compare_segmented_orbit_identity import segmented_dense


SCHEMA = "butterfly.jones-period96-sign-phase-resolution-audit-manifest.v1"


def continuous_phase_identity(left, right, comparison: dict) -> dict:
    phases = np.linspace(
        0.0, 1.0, int(comparison["phase_samples"]), endpoint=False
    )
    left_states = left(phases)

    def rms(shift: float) -> float:
        return float(
            np.sqrt(
                np.mean((left_states - right((phases + shift) % 1.0)) ** 2)
            )
        )

    center = float(comparison["expected_phase_shift"])
    half_width = float(comparison["search_half_width"])
    lower = center - half_width
    upper = center + half_width
    inverse_phi = (np.sqrt(5.0) - 1.0) / 2.0
    interior_left = upper - inverse_phi * (upper - lower)
    interior_right = lower + inverse_phi * (upper - lower)
    left_value = rms(interior_left)
    right_value = rms(interior_right)
    evaluations = 2
    iterations = 0
    while (
        upper - lower > float(comparison["phase_tolerance"])
        and iterations < int(comparison["maximum_iterations"])
    ):
        if left_value <= right_value:
            upper = interior_right
            interior_right = interior_left
            right_value = left_value
            interior_left = upper - inverse_phi * (upper - lower)
            left_value = rms(interior_left)
        else:
            lower = interior_left
            interior_left = interior_right
            left_value = right_value
            interior_right = lower + inverse_phi * (upper - lower)
            right_value = rms(interior_right)
        evaluations += 1
        iterations += 1
    candidates = (
        (interior_left, left_value),
        (interior_right, right_value),
        ((lower + upper) / 2.0, rms((lower + upper) / 2.0)),
    )
    evaluations += 1
    best_shift, best_value = min(candidates, key=lambda row: row[1])
    success = bool(upper - lower <= float(comparison["phase_tolerance"]))
    return {
        "success": success,
        "message": "declared phase width reached" if success else "iteration ceiling reached",
        "evaluations": evaluations,
        "iterations": iterations,
        "phase_shift": float(best_shift % 1.0),
        "rms": float(best_value),
        "expected_shift_residual": float(abs(best_shift - center)),
        "final_bracket": [lower, upper],
        "final_bracket_width": upper - lower,
        "bounds": [center - half_width, center + half_width],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported sign phase-resolution audit manifest")
    source_bytes = args.source.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash mismatch")
    source_receipt = json.loads(source_bytes)
    if (
        source_receipt.get("schema") != manifest["source_schema"]
        or source_receipt.get("passed")
    ):
        raise SystemExit("bound source must be the failed EXP-254 receipt")
    expected_checks = {
        key: key != "sign_identity" for key in source_receipt["checks"]
    }
    if source_receipt["checks"] != expected_checks:
        raise SystemExit("source failure is not isolated to sign identity")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    parameters = RosslerParameters(
        a=float(source_receipt["target_a"]),
        b=float(source_receipt["fixed_b"]),
        c=float(source_receipt["fixed_c"]),
    )
    started = time.perf_counter()
    identities = {}
    endpoint_errors = {}
    for solver_name, solver_profile in manifest["solvers"].items():
        solver = SolverConfig(**solver_profile)
        evaluators = {}
        endpoint_errors[solver_name] = {}
        for direction in ("-1", "1"):
            row = source_receipt["results"][solver_name][direction]
            evaluate, endpoint_error = segmented_dense(
                np.asarray(row["nodes"], dtype=float),
                float(row["period_time"]),
                parameters,
                solver,
            )
            evaluators[direction] = evaluate
            endpoint_errors[solver_name][direction] = endpoint_error
        identities[solver_name] = continuous_phase_identity(
            evaluators["-1"], evaluators["1"], manifest["comparison"]
        )

    acceptance = manifest["acceptance"]
    checks = {
        "source_failure_isolated": True,
        "optimizer_success": all(row["success"] for row in identities.values()),
        "sign_identity": max(row["rms"] for row in identities.values())
        <= float(acceptance["maximum_sign_identity_rms"]),
        "half_period_shift": max(
            row["expected_shift_residual"] for row in identities.values()
        )
        <= float(acceptance["maximum_half_period_shift_residual"]),
        "segment_endpoints": max(
            value for row in endpoint_errors.values() for value in row.values()
        )
        <= float(acceptance["maximum_segment_endpoint_error"]),
        "solver_rms_agreement": abs(
            identities[manifest["reference_solver"]]["rms"]
            - identities[manifest["independent_solver"]]["rms"]
        )
        <= float(acceptance["maximum_solver_rms_difference"]),
    }
    output = {
        "schema": "butterfly.jones-period96-sign-phase-resolution-audit-receipt.v1",
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
        "target_a": source_receipt["target_a"],
        "fixed_b": source_receipt["fixed_b"],
        "fixed_c": source_receipt["fixed_c"],
        "source_checks": source_receipt["checks"],
        "continuous_sign_identities": identities,
        "segment_endpoint_errors": endpoint_errors,
        "checks": checks,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(checks.values()),
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    print(json.dumps(output, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
