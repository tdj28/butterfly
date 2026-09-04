#!/usr/bin/env python3
"""Naturally continue corrected periodic flow orbits in the Rössler b parameter."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy

from butterfly import (
    RosslerParameters,
    SolverConfig,
    classify_fundamental_period,
    collect_crossings,
    correct_periodic_orbit,
    flow_monodromy,
    legacy_rossler_section,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def orbit_row(parameters: RosslerParameters, corrected, solver: SolverConfig) -> dict:
    monodromy = flow_monodromy(
        parameters, corrected.initial_state, corrected.period_time, config=solver
    )
    neutral_index = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
    nontrivial = np.delete(monodromy.multipliers, neutral_index)
    maximum = float(np.max(np.abs(nontrivial)))
    return {
        "parameters": {"a": parameters.a, "b": parameters.b, "c": parameters.c},
        "initial_state": corrected.initial_state.tolist(),
        "period_time": corrected.period_time,
        "closure_error": corrected.closure_error,
        "phase_residual": corrected.phase_residual,
        "correction_norm": corrected.correction_norm,
        "corrector_evaluations": corrected.evaluations,
        "neutral_multiplier_error": float(abs(monodromy.multipliers[neutral_index] - 1.0)),
        "nontrivial_multipliers": [
            {"real": float(value.real), "imag": float(value.imag), "modulus": float(abs(value))}
            for value in nontrivial
        ],
        "max_nontrivial_multiplier_modulus": maximum,
        "stable": maximum < 1.0,
        "distance_to_plus_one": float(np.min(np.abs(nontrivial - 1.0))),
        "distance_to_minus_one": float(np.min(np.abs(nontrivial + 1.0))),
        "predicted_determinant": monodromy.predicted_determinant,
        "computed_determinant": monodromy.computed_determinant,
    }


def continue_direction(
    seed_row: dict,
    *,
    a: float,
    c: float,
    direction: int,
    limit: float,
    nominal_step: float,
    minimum_step: float,
    solver: SolverConfig,
    corrector_config: dict,
) -> tuple[list[dict], dict]:
    current_b = float(seed_row["parameters"]["b"])
    current_state = np.asarray(seed_row["initial_state"], dtype=float)
    current_period = float(seed_row["period_time"])
    step = nominal_step
    rows = []
    failures = []
    while direction * (limit - current_b) > 1e-14:
        trial_step = min(step, abs(limit - current_b))
        target_b = current_b + direction * trial_step
        parameters = RosslerParameters(a=a, b=target_b, c=c)
        try:
            corrected = correct_periodic_orbit(
                parameters,
                current_state,
                current_period,
                config=solver,
                max_evaluations=int(corrector_config["max_evaluations"]),
                tolerance=float(corrector_config["tolerance"]),
            )
        except (RuntimeError, ValueError) as error:
            corrected = None
            message = str(error)
        else:
            message = corrected.message
        if corrected is None or not corrected.success:
            failures.append(
                {
                    "from_b": current_b,
                    "target_b": target_b,
                    "step": trial_step,
                    "message": message,
                }
            )
            step = 0.5 * trial_step
            if step < minimum_step:
                break
            continue
        row = orbit_row(parameters, corrected, solver)
        row["accepted_step"] = trial_step
        rows.append(row)
        current_b = target_b
        current_state = corrected.initial_state
        current_period = corrected.period_time
        step = min(nominal_step, 1.5 * trial_step)
    return rows, {
        "direction": direction,
        "limit": limit,
        "reached_limit": bool(abs(current_b - limit) <= 1e-12),
        "last_b": current_b,
        "failures": failures,
    }


def candidate_crossings(rows: list[dict]) -> list[dict]:
    ordered = sorted(rows, key=lambda row: row["parameters"]["b"])
    candidates = []
    for left, right in zip(ordered, ordered[1:]):
        left_value = left["max_nontrivial_multiplier_modulus"] - 1.0
        right_value = right["max_nontrivial_multiplier_modulus"] - 1.0
        if left_value == 0.0 or left_value * right_value < 0.0:
            left_b = left["parameters"]["b"]
            right_b = right["parameters"]["b"]
            fraction = -left_value / (right_value - left_value)
            candidates.append(
                {
                    "type": "unit-modulus stability crossing",
                    "b_bracket": [left_b, right_b],
                    "linear_b_estimate": float(left_b + fraction * (right_b - left_b)),
                    "left_modulus": left["max_nontrivial_multiplier_modulus"],
                    "right_modulus": right["max_nontrivial_multiplier_modulus"],
                }
            )
    return candidates


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw_manifest = args.manifest.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get("schema") != "butterfly.periodic-b-continuation-manifest.v1":
        raise SystemExit("unsupported b-continuation manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("periodic continuation requires clean source")
    solver = SolverConfig(**manifest["solver"])
    crossings_config = manifest["crossings"]
    continuation = manifest["continuation"]
    started = time.perf_counter()
    families = []
    for family in manifest["families"]:
        start = family["start"]
        parameters = RosslerParameters(
            a=float(start["a"]), b=float(start["b"]), c=float(start["c"])
        )
        expected_period = int(family["period"])
        crossings = collect_crossings(
            parameters,
            tuple(map(float, crossings_config["initial_state"])),
            legacy_rossler_section(parameters),
            transient=float(crossings_config["transient"]),
            observation_horizon=float(crossings_config["observation_horizon"]),
            max_crossings=int(crossings_config["max_crossings"]),
            config=solver,
        )
        recurrence = classify_fundamental_period(
            crossings.states,
            max_period=int(crossings_config["max_period"]),
            required_repeats=int(crossings_config["required_repeats"]),
            atol=float(crossings_config["atol"]),
            rtol=float(crossings_config["rtol"]),
        )
        if recurrence.fundamental_period != expected_period:
            raise RuntimeError(f"{family['id']} start did not reproduce expected period")
        start_index = -expected_period - 1
        seed_state = crossings.states[start_index]
        seed_period = float(crossings.times[-1] - crossings.times[start_index])
        corrected = correct_periodic_orbit(
            parameters,
            seed_state,
            seed_period,
            config=solver,
            max_evaluations=int(manifest["corrector"]["max_evaluations"]),
            tolerance=float(manifest["corrector"]["tolerance"]),
        )
        if not corrected.success:
            raise RuntimeError(
                f"{family['id']} seed periodic correction failed: {corrected.message}"
            )
        seed_row = orbit_row(parameters, corrected, solver)
        downward, downward_status = continue_direction(
            seed_row,
            a=parameters.a,
            c=parameters.c,
            direction=-1,
            limit=float(continuation["b_min"]),
            nominal_step=float(continuation["nominal_step"]),
            minimum_step=float(continuation["minimum_step"]),
            solver=solver,
            corrector_config=manifest["corrector"],
        )
        upward, upward_status = continue_direction(
            seed_row,
            a=parameters.a,
            c=parameters.c,
            direction=1,
            limit=float(continuation["b_max"]),
            nominal_step=float(continuation["nominal_step"]),
            minimum_step=float(continuation["minimum_step"]),
            solver=solver,
            corrector_config=manifest["corrector"],
        )
        rows = list(reversed(downward)) + [seed_row] + upward
        closures = [row["closure_error"] for row in rows]
        families.append(
            {
                "id": family["id"],
                "period": expected_period,
                "fixed_a": parameters.a,
                "fixed_c": parameters.c,
                "rows": rows,
                "point_count": len(rows),
                "b_range": [rows[0]["parameters"]["b"], rows[-1]["parameters"]["b"]],
                "stable_point_count": sum(row["stable"] for row in rows),
                "max_closure_error": max(closures),
                "candidate_crossings": candidate_crossings(rows),
                "downward_status": downward_status,
                "upward_status": upward_status,
            }
        )
    acceptance = manifest["acceptance"]
    passed = all(
        family["point_count"] >= int(acceptance["minimum_points_per_family"])
        and family["max_closure_error"] <= float(acceptance["max_closure_error"])
        for family in families
    )
    receipt = {
        "schema": "butterfly.periodic-b-continuation-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(raw_manifest),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "families": families,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "interpretation_limit": (
            "Natural continuation in b at fixed (a,c) is not fold-safe. Candidate "
            "stability crossings require refined boundary solves and pseudo-arclength checks."
        ),
    }
    output_bytes = canonical_json(receipt)
    atomic_write(args.output, output_bytes)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": sha256_bytes(output_bytes),
                "passed": passed,
                "elapsed_seconds": receipt["elapsed_seconds"],
                "families": [
                    {
                        "id": family["id"],
                        "point_count": family["point_count"],
                        "b_range": family["b_range"],
                        "candidate_crossings": len(family["candidate_crossings"]),
                    }
                    for family in families
                ],
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
