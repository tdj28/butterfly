#!/usr/bin/env python3
"""Test phase-invariant branch and multiplier scaling near a +1 event."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from compare_periodic_orbit_identity import (
    corrected_from_rows,
    dense_orbit,
    phase_aligned_rms,
)


def nontrivial_modulus(monodromy: object) -> float:
    neutral_index = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
    return float(np.max(np.abs(np.delete(monodromy.multipliers, neutral_index))))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event-receipt", type=Path, required=True)
    parser.add_argument("--branch-receipt", type=Path, required=True)
    parser.add_argument("--primary-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.periodic-normal-form-scaling-manifest.v1":
        raise SystemExit("unsupported normal-form scaling manifest")
    inputs = {
        "event": args.event_receipt.read_bytes(),
        "branch": args.branch_receipt.read_bytes(),
        "primary": args.primary_receipt.read_bytes(),
    }
    for name in inputs:
        if sha256_bytes(inputs[name]) != manifest[f"{name}_receipt_sha256"]:
            raise SystemExit(f"{name} receipt hash does not match manifest")
    event = json.loads(inputs["event"])
    branches = json.loads(inputs["branch"])
    primary = json.loads(inputs["primary"])
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("normal-form scaling requires clean source")
    secondary = next(
        branch
        for branch in branches["branches"]
        if branch["direction"] == int(manifest["secondary_direction"])
    )
    solver = SolverConfig(**manifest["solver"])
    corrector = manifest["corrector"]
    comparison = manifest["comparison"]
    b_star = float(event["corrected_b"])
    started = time.perf_counter()
    rows = []
    for mu in map(float, manifest["mu_offsets"]):
        b = b_star + mu
        parameters = RosslerParameters(
            a=float(event["fixed_a"]), b=b, c=float(event["fixed_c"])
        )
        primary_result = corrected_from_rows(
            primary["rows"],
            target_b=b,
            parameters=parameters,
            solver=solver,
            tolerance=float(corrector["tolerance"]),
            max_evaluations=int(corrector["max_evaluations"]),
        )
        secondary_result = corrected_from_rows(
            secondary["rows"],
            target_b=b,
            parameters=parameters,
            solver=solver,
            tolerance=float(corrector["tolerance"]),
            max_evaluations=int(corrector["max_evaluations"]),
        )
        primary_dense = dense_orbit(primary_result[0], parameters, solver)
        secondary_dense = dense_orbit(secondary_result[0], parameters, solver)
        identity = phase_aligned_rms(
            (primary_result[0], primary_dense),
            (secondary_result[0], secondary_dense),
            phase_samples=int(comparison["phase_samples"]),
            coarse_shifts=int(comparison["coarse_shifts"]),
            shift_tolerance=float(comparison["shift_tolerance"]),
        )
        primary_multiplier = nontrivial_modulus(primary_result[1])
        secondary_multiplier = nontrivial_modulus(secondary_result[1])
        rows.append(
            {
                "mu": mu,
                "b": b,
                "separation_rms": identity["rms"],
                "phase_shift": identity["phase_shift"],
                "primary_period": primary_result[0].period_time,
                "secondary_period": secondary_result[0].period_time,
                "primary_closure_error": primary_result[0].closure_error,
                "secondary_closure_error": secondary_result[0].closure_error,
                "primary_multiplier_modulus": primary_multiplier,
                "secondary_multiplier_modulus": secondary_multiplier,
                "multiplier_deviation_ratio": (1.0 - secondary_multiplier)
                / (primary_multiplier - 1.0),
            }
        )

    log_mu = np.log([row["mu"] for row in rows])
    log_separation = np.log([row["separation_rms"] for row in rows])
    exponent, intercept = np.polyfit(log_mu, log_separation, 1)
    predicted = exponent * log_mu + intercept
    residual_sum = float(np.sum((log_separation - predicted) ** 2))
    total_sum = float(np.sum((log_separation - np.mean(log_separation)) ** 2))
    r_squared = 1.0 - residual_sum / total_sum
    ratios = np.asarray([row["multiplier_deviation_ratio"] for row in rows])
    max_closure = max(
        max(row["primary_closure_error"], row["secondary_closure_error"])
        for row in rows
    )
    acceptance = manifest["acceptance"]
    stability_exchange = all(
        row["primary_multiplier_modulus"] > 1.0
        and row["secondary_multiplier_modulus"] < 1.0
        for row in rows
    )
    passed = bool(
        max_closure <= float(acceptance["max_closure_error"])
        and float(acceptance["separation_exponent_min"])
        <= exponent
        <= float(acceptance["separation_exponent_max"])
        and r_squared >= float(acceptance["minimum_separation_r_squared"])
        and float(acceptance["multiplier_ratio_median_min"])
        <= float(np.median(ratios))
        <= float(acceptance["multiplier_ratio_median_max"])
        and (
            not acceptance["require_stability_exchange_at_all_points"]
            or stability_exchange
        )
    )
    receipt = {
        "schema": "butterfly.periodic-normal-form-scaling-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(inputs["event"]),
        "branch_receipt_sha256": sha256_bytes(inputs["branch"]),
        "primary_receipt_sha256": sha256_bytes(inputs["primary"]),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "b_star": b_star,
        "rows": rows,
        "separation_power_law": {
            "exponent": float(exponent),
            "intercept": float(intercept),
            "r_squared": r_squared,
        },
        "multiplier_ratio_median": float(np.median(ratios)),
        "multiplier_ratio_range": [float(np.min(ratios)), float(np.max(ratios))],
        "max_closure_error": max_closure,
        "stability_exchange_at_all_points": stability_exchange,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "interpretation_limit": "Finite-range scaling supports a supercritical pitchfork normal form in the flow-phase quotient; it is not a symmetry proof or validated local reduction.",
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps(receipt, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
