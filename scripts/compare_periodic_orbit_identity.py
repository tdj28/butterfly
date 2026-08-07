#!/usr/bin/env python3
"""Compare corrected periodic cycles with a phase-invariant trajectory metric."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar

from butterfly import (
    RosslerParameters,
    SolverConfig,
    correct_periodic_orbit,
    flow_monodromy,
    rossler_rhs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def corrected_from_rows(
    rows: list[dict],
    *,
    target_b: float,
    parameters: RosslerParameters,
    solver: SolverConfig,
    tolerance: float,
    max_evaluations: int,
) -> tuple[object, object]:
    ordered = sorted(rows, key=lambda row: float(row["b"]))
    b_values = np.asarray([row["b"] for row in ordered], dtype=float)
    if not b_values[0] <= target_b <= b_values[-1]:
        raise ValueError("target b lies outside a source branch")
    state = np.asarray(
        [
            np.interp(
                target_b, b_values, [row["initial_state"][index] for row in ordered]
            )
            for index in range(3)
        ]
    )
    period_time = float(
        np.interp(target_b, b_values, [row["period_time"] for row in ordered])
    )
    correction = correct_periodic_orbit(
        parameters,
        state,
        period_time,
        config=solver,
        tolerance=tolerance,
        max_evaluations=max_evaluations,
    )
    monodromy = flow_monodromy(
        parameters, correction.initial_state, correction.period_time, config=solver
    )
    return correction, monodromy


def dense_orbit(correction: object, parameters: RosslerParameters, solver: SolverConfig):
    integration = solve_ivp(
        lambda time, state: rossler_rhs(time, state, parameters),
        (0.0, correction.period_time),
        correction.initial_state,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
        dense_output=True,
    )
    if not integration.success:
        raise RuntimeError(f"identity integration failed: {integration.message}")
    return integration.sol


def phase_aligned_rms(
    left: tuple[object, object],
    right: tuple[object, object],
    *,
    phase_samples: int,
    coarse_shifts: int,
    shift_tolerance: float,
) -> dict:
    left_correction, left_dense = left
    right_correction, right_dense = right
    phases = np.linspace(0.0, 1.0, phase_samples, endpoint=False)
    left_states = left_dense(phases * left_correction.period_time)

    def rms(shift: float) -> float:
        right_phases = (phases + shift) % 1.0
        right_states = right_dense(right_phases * right_correction.period_time)
        return float(np.sqrt(np.mean((left_states - right_states) ** 2)))

    shifts = np.linspace(0.0, 1.0, coarse_shifts, endpoint=False)
    values = np.asarray([rms(shift) for shift in shifts])
    best = int(np.argmin(values))
    spacing = 1.0 / coarse_shifts
    refinement = minimize_scalar(
        lambda shift: rms(shift % 1.0),
        bounds=(float(shifts[best] - spacing), float(shifts[best] + spacing)),
        method="bounded",
        options={"xatol": shift_tolerance},
    )
    return {"rms": float(refinement.fun), "phase_shift": float(refinement.x % 1.0)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--branch-receipt", type=Path, required=True)
    parser.add_argument("--primary-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.periodic-orbit-identity-manifest.v1":
        raise SystemExit("unsupported orbit-identity manifest")
    branch_bytes = args.branch_receipt.read_bytes()
    primary_bytes = args.primary_receipt.read_bytes()
    if sha256_bytes(branch_bytes) != manifest["branch_receipt_sha256"]:
        raise SystemExit("branch receipt hash does not match manifest")
    if sha256_bytes(primary_bytes) != manifest["primary_receipt_sha256"]:
        raise SystemExit("primary receipt hash does not match manifest")
    branches = json.loads(branch_bytes)
    primary = json.loads(primary_bytes)
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("orbit-identity comparison requires clean source")

    started = time.perf_counter()
    target_b = float(manifest["target_b"])
    parameters = RosslerParameters(
        a=float(manifest["fixed_a"]), b=target_b, c=float(manifest["fixed_c"])
    )
    solver = SolverConfig(**manifest["solver"])
    corrector = manifest["corrector"]
    corrected = [
        corrected_from_rows(
            primary["rows"],
            target_b=target_b,
            parameters=parameters,
            solver=solver,
            tolerance=float(corrector["tolerance"]),
            max_evaluations=int(corrector["max_evaluations"]),
        )
    ]
    corrected.extend(
        corrected_from_rows(
            branch["rows"],
            target_b=target_b,
            parameters=parameters,
            solver=solver,
            tolerance=float(corrector["tolerance"]),
            max_evaluations=int(corrector["max_evaluations"]),
        )
        for branch in branches["branches"]
    )
    dense = [dense_orbit(item[0], parameters, solver) for item in corrected]
    comparison = manifest["comparison"]
    pairs = {}
    for name, left, right in (
        ("secondary_minus_vs_plus", 1, 2),
        ("primary_vs_secondary_minus", 0, 1),
        ("primary_vs_secondary_plus", 0, 2),
    ):
        pairs[name] = phase_aligned_rms(
            (corrected[left][0], dense[left]),
            (corrected[right][0], dense[right]),
            phase_samples=int(comparison["phase_samples"]),
            coarse_shifts=int(comparison["coarse_shifts"]),
            shift_tolerance=float(comparison["shift_tolerance"]),
        )

    orbit_rows = []
    for name, (correction, monodromy) in zip(
        ("primary", "secondary_minus", "secondary_plus"), corrected, strict=True
    ):
        neutral_index = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
        nontrivial = np.delete(monodromy.multipliers, neutral_index)
        orbit_rows.append(
            {
                "name": name,
                "initial_state": correction.initial_state.tolist(),
                "period_time": correction.period_time,
                "closure_error": correction.closure_error,
                "max_nontrivial_multiplier_modulus": float(np.max(np.abs(nontrivial))),
                "stable": bool(np.max(np.abs(nontrivial)) < 1.0),
            }
        )
    acceptance = manifest["acceptance"]
    period_gaps = [
        abs(orbit_rows[0]["period_time"] - orbit_rows[index]["period_time"])
        for index in (1, 2)
    ]
    passed = bool(
        max(row["closure_error"] for row in orbit_rows)
        <= float(acceptance["max_closure_error"])
        and pairs["secondary_minus_vs_plus"]["rms"]
        <= float(acceptance["max_secondary_arm_rms"])
        and min(
            pairs["primary_vs_secondary_minus"]["rms"],
            pairs["primary_vs_secondary_plus"]["rms"],
        )
        >= float(acceptance["minimum_primary_secondary_rms"])
        and min(period_gaps)
        >= float(acceptance["minimum_primary_secondary_period_gap"])
        and (not acceptance["require_primary_unstable"] or not orbit_rows[0]["stable"])
        and (
            not acceptance["require_secondary_stable"]
            or all(orbit_rows[index]["stable"] for index in (1, 2))
        )
    )
    receipt = {
        "schema": "butterfly.periodic-orbit-identity-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "branch_receipt_sha256": sha256_bytes(branch_bytes),
        "primary_receipt_sha256": sha256_bytes(primary_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "parameters": {"a": parameters.a, "b": parameters.b, "c": parameters.c},
        "orbits": orbit_rows,
        "pairwise_phase_aligned": pairs,
        "primary_secondary_period_gaps": period_gaps,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "interpretation_limit": "Two invariant cycles and a stability exchange support but do not prove a generic pitchfork-like normal form.",
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps(receipt, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
