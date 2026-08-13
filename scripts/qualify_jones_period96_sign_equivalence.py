#!/usr/bin/env python3
"""Qualify both period-96 switch signs as one phase-shifted stable orbit."""

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
from qualify_jones_period24_near_event import corrected_family
from validate_multiple_shooting_switch import half_closure


SCHEMA = "butterfly.jones-period96-sign-equivalence-manifest.v1"


def phase_aligned_identity(left, right, comparison: dict) -> dict:
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

    shifts = np.linspace(
        0.0, 1.0, int(comparison["coarse_shifts"]), endpoint=False
    )
    values = np.asarray([rms(float(shift)) for shift in shifts])
    best = int(np.argmin(values))
    center = float(shifts[best])
    half_width = 1.0 / int(comparison["coarse_shifts"])
    history = []
    for stage in range(int(comparison["refinement_stages"])):
        stage_shifts = center + np.linspace(
            -half_width,
            half_width,
            int(comparison["refinement_points"]),
        )
        stage_values = np.asarray(
            [rms(float(shift % 1.0)) for shift in stage_shifts]
        )
        stage_best = int(np.argmin(stage_values))
        center = float(stage_shifts[stage_best])
        spacing = 2.0 * half_width / (len(stage_shifts) - 1)
        history.append(
            {
                "stage": stage + 1,
                "phase_shift": float(center % 1.0),
                "rms": float(stage_values[stage_best]),
                "grid_spacing": spacing,
            }
        )
        half_width = spacing
    return {
        "phase_shift": float(center % 1.0),
        "rms": rms(center % 1.0),
        "coarse_phase_shift": float(shifts[best]),
        "coarse_rms": float(values[best]),
        "refinement_history": history,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--switch", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported period-96 sign-equivalence manifest")
    switch_bytes = args.switch.read_bytes()
    if sha256_bytes(switch_bytes) != manifest["switch_receipt_sha256"]:
        raise SystemExit("switch receipt hash mismatch")
    switch = json.loads(switch_bytes)
    if not switch.get("passed"):
        raise SystemExit("a passed switch receipt is required")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    source_rows = [
        row
        for row in switch["accepted_candidates"]
        if float(row["step_length"]) == float(manifest["source_step_length"])
    ]
    if {int(row["direction"]) for row in source_rows} != {-1, 1}:
        raise SystemExit("switch receipt lacks both frozen tangent signs")
    source_rows.sort(key=lambda row: int(row["direction"]))
    target_a = float(manifest["target_a"])
    fixed_b = float(manifest["fixed_b"])
    fixed_c = float(manifest["fixed_c"])
    parameters = RosslerParameters(a=target_a, b=fixed_b, c=fixed_c)
    solvers = {
        name: SolverConfig(**profile) for name, profile in manifest["solvers"].items()
    }
    started = time.perf_counter()
    results = {}
    evaluators = {}
    endpoint_errors = {}
    for solver_name, solver in solvers.items():
        results[solver_name] = {}
        evaluators[solver_name] = {}
        endpoint_errors[solver_name] = {}
        for seed in source_rows:
            direction = str(int(seed["direction"]))
            corrected = corrected_family(
                seed,
                int(switch["segment_count"]),
                parameters,
                solver,
                manifest,
            )
            nodes = np.asarray(corrected["nodes"], dtype=float)
            corrected["half_period_closure"] = half_closure(
                nodes[0], corrected["period_time"], parameters, solver
            )
            evaluate, endpoint_error = segmented_dense(
                nodes, corrected["period_time"], parameters, solver
            )
            evaluators[solver_name][direction] = evaluate
            endpoint_errors[solver_name][direction] = endpoint_error
            corrected["nodes"] = nodes.tolist()
            results[solver_name][direction] = corrected

    comparison = manifest["comparison"]
    sign_identities = {
        solver_name: phase_aligned_identity(
            evaluators[solver_name]["-1"],
            evaluators[solver_name]["1"],
            comparison,
        )
        for solver_name in solvers
    }
    solver_identities = {
        direction: phase_aligned_identity(
            evaluators[manifest["reference_solver"]][direction],
            evaluators[manifest["independent_solver"]][direction],
            comparison,
        )
        for direction in ("-1", "1")
    }
    periods = [
        row[direction]["period_time"]
        for row in results.values()
        for direction in ("-1", "1")
    ]
    moduli = [
        row[direction]["dominant_modulus"]
        for row in results.values()
        for direction in ("-1", "1")
    ]
    families = [
        row[direction]
        for row in results.values()
        for direction in ("-1", "1")
    ]
    acceptance = manifest["acceptance"]
    checks = {
        "all_corrections": all(row["status"]["success"] for row in families),
        "matching": max(row["status"]["matching_residual"] for row in families)
        <= float(acceptance["maximum_matching_residual"]),
        "phase": max(row["status"]["phase_residual"] for row in families)
        <= float(acceptance["maximum_phase_residual"]),
        "sign_identity": max(row["rms"] for row in sign_identities.values())
        <= float(acceptance["maximum_sign_identity_rms"]),
        "solver_identity": max(row["rms"] for row in solver_identities.values())
        <= float(acceptance["maximum_solver_identity_rms"]),
        "segment_endpoints": max(
            value for row in endpoint_errors.values() for value in row.values()
        )
        <= float(acceptance["maximum_segment_endpoint_error"]),
        "period_agreement": max(periods) - min(periods)
        <= float(acceptance["maximum_period_spread"]),
        "modulus_agreement": max(moduli) - min(moduli)
        <= float(acceptance["maximum_modulus_spread"]),
        "stable": max(moduli) <= float(acceptance["maximum_stable_modulus"]),
        "primitive": min(row["half_period_closure"] for row in families)
        >= float(acceptance["minimum_half_period_closure"]),
    }
    output = {
        "schema": "butterfly.jones-period96-sign-equivalence-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "switch_receipt_sha256": sha256_bytes(switch_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "target_a": target_a,
        "fixed_b": fixed_b,
        "fixed_c": fixed_c,
        "results": results,
        "sign_identities": sign_identities,
        "solver_identities": solver_identities,
        "segment_endpoint_errors": endpoint_errors,
        "period_spread": max(periods) - min(periods),
        "modulus_spread": max(moduli) - min(moduli),
        "checks": checks,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(checks.values()),
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    printed = {**output, "results": {}}
    for solver_name, solver_rows in results.items():
        printed["results"][solver_name] = {
            direction: {
                key: value
                for key, value in row.items()
                if key not in {"nodes", "block_floquet"}
            }
            for direction, row in solver_rows.items()
        }
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
