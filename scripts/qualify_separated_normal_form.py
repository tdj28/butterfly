#!/usr/bin/env python3
"""Qualify branch identity and pitchfork scaling at a separated surface event."""

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
    correct_periodic_orbit,
    flow_monodromy,
    rossler_rhs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from compare_periodic_orbit_identity import dense_orbit, phase_aligned_rms
from pseudo_arclength_periodic_b import correct_arclength, diagnose
from switch_periodic_branch import extended_shooting_jacobian


def correct_fixed_b(
    *,
    a: float,
    b: float,
    c: float,
    initial_state: np.ndarray,
    period_time: float,
    solver: SolverConfig,
    tolerance: float,
    max_evaluations: int,
) -> tuple[object, object]:
    parameters = RosslerParameters(a=a, b=b, c=c)
    correction = correct_periodic_orbit(
        parameters,
        initial_state,
        period_time,
        config=solver,
        tolerance=tolerance,
        max_evaluations=max_evaluations,
    )
    monodromy = flow_monodromy(
        parameters, correction.initial_state, correction.period_time, config=solver
    )
    return correction, monodromy


def interpolate_branch(rows: list[dict], target_b: float) -> tuple[np.ndarray, float]:
    ordered = sorted(rows, key=lambda row: float(row["b"]))
    b_values = np.asarray([row["b"] for row in ordered], dtype=float)
    if not b_values[0] <= target_b <= b_values[-1]:
        raise ValueError(f"target b={target_b} is outside switched branch")
    state = np.asarray(
        [
            np.interp(target_b, b_values, [row["initial_state"][index] for row in ordered])
            for index in range(3)
        ]
    )
    period_time = float(
        np.interp(target_b, b_values, [row["period_time"] for row in ordered])
    )
    return state, period_time


def nontrivial_modulus(monodromy: object) -> float:
    neutral_index = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
    return float(np.max(np.abs(np.delete(monodromy.multipliers, neutral_index))))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-surface", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.separated-normal-form-manifest.v1":
        raise SystemExit("unsupported separated normal-form manifest")
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
        raise SystemExit("separated normal-form qualification requires clean source")

    coordinate = manifest["event_coordinate"]
    a = float(coordinate["a"])
    c = float(coordinate["c"])
    event = next(
        row
        for row in surface["rows"]
        if abs(row["a"] - a) < 1e-12 and abs(row["c"] - c) < 1e-12
    )
    b_star = float(event["b"])
    event_state = np.asarray(event["initial_state"], dtype=float)
    event_period = float(event["period_time"])
    event_variables = np.concatenate((event_state, (event_period, b_star)))
    solver = SolverConfig(**manifest["solver"])
    corrector = manifest["corrector"]
    tolerance = float(corrector["tolerance"])
    max_evaluations = int(corrector["max_evaluations"])
    tangent_offset = float(manifest["primary_tangent_offset"])
    started = time.perf_counter()

    primary_minus = correct_fixed_b(
        a=a,
        b=b_star - tangent_offset,
        c=c,
        initial_state=event_state,
        period_time=event_period,
        solver=solver,
        tolerance=tolerance,
        max_evaluations=max_evaluations,
    )[0]
    primary_plus = correct_fixed_b(
        a=a,
        b=b_star + tangent_offset,
        c=c,
        initial_state=event_state,
        period_time=event_period,
        solver=solver,
        tolerance=tolerance,
        max_evaluations=max_evaluations,
    )[0]
    minus_variables = np.concatenate(
        (primary_minus.initial_state, (primary_minus.period_time, b_star - tangent_offset))
    )
    plus_variables = np.concatenate(
        (primary_plus.initial_state, (primary_plus.period_time, b_star + tangent_offset))
    )
    observed_primary = plus_variables - minus_variables
    observed_primary /= np.linalg.norm(observed_primary)
    parameters = RosslerParameters(a=a, b=b_star, c=c)
    phase_direction = rossler_rhs(0.0, event_state, parameters)
    phase_direction /= np.linalg.norm(phase_direction)
    shooting_jacobian = extended_shooting_jacobian(
        event_variables,
        a=a,
        c=c,
        phase_direction=phase_direction,
        solver=solver,
    )
    _, singular_values, right_vectors = np.linalg.svd(
        shooting_jacobian, full_matrices=True
    )
    null_basis = right_vectors[-2:].T
    primary_tangent = null_basis @ (null_basis.T @ observed_primary)
    primary_tangent /= np.linalg.norm(primary_tangent)
    secondary_tangent = null_basis[:, 0] - primary_tangent * float(
        np.dot(primary_tangent, null_basis[:, 0])
    )
    if np.linalg.norm(secondary_tangent) < 1e-8:
        secondary_tangent = null_basis[:, 1] - primary_tangent * float(
            np.dot(primary_tangent, null_basis[:, 1])
        )
    secondary_tangent /= np.linalg.norm(secondary_tangent)

    switched_branches = []
    for direction in (-1.0, 1.0):
        tangent = direction * secondary_tangent
        predictor = event_variables + float(manifest["switch"]["step_length"]) * tangent
        corrected, status = correct_arclength(
            predictor,
            tangent,
            event_state,
            b_star,
            a=a,
            c=c,
            solver=solver,
            tolerance=tolerance,
            max_evaluations=max_evaluations,
        )
        points = [event_variables]
        rows = []
        statuses = [{**status, "step_index": 0}]
        if status["success"]:
            points.append(corrected)
            rows.append(diagnose(corrected, a=a, c=c, solver=solver))
        for step_index in range(1, int(manifest["switch"]["steps_per_direction"])):
            if len(points) < 2:
                break
            tangent = points[-1] - points[-2]
            tangent /= np.linalg.norm(tangent)
            predictor = points[-1] + float(manifest["switch"]["step_length"]) * tangent
            corrected, status = correct_arclength(
                predictor,
                tangent,
                points[-1][:3],
                float(points[-1][4]),
                a=a,
                c=c,
                solver=solver,
                tolerance=tolerance,
                max_evaluations=max_evaluations,
            )
            statuses.append({**status, "step_index": step_index})
            if not status["success"]:
                break
            points.append(corrected)
            rows.append(diagnose(corrected, a=a, c=c, solver=solver))
        switched_branches.append(
            {"direction": int(direction), "rows": rows, "statuses": statuses}
        )

    comparison = manifest["comparison"]
    scaling_rows = []
    corrected_at_offset = []
    for mu in map(float, manifest["mu_offsets"]):
        target_b = b_star + mu
        primary_result = correct_fixed_b(
            a=a,
            b=target_b,
            c=c,
            initial_state=event_state,
            period_time=event_period,
            solver=solver,
            tolerance=tolerance,
            max_evaluations=max_evaluations,
        )
        secondary_results = []
        for branch in switched_branches:
            state, period_time = interpolate_branch(branch["rows"], target_b)
            secondary_results.append(
                correct_fixed_b(
                    a=a,
                    b=target_b,
                    c=c,
                    initial_state=state,
                    period_time=period_time,
                    solver=solver,
                    tolerance=tolerance,
                    max_evaluations=max_evaluations,
                )
            )
        primary_dense = dense_orbit(primary_result[0], RosslerParameters(a=a, b=target_b, c=c), solver)
        secondary_dense = dense_orbit(
            secondary_results[0][0], RosslerParameters(a=a, b=target_b, c=c), solver
        )
        separation = phase_aligned_rms(
            (primary_result[0], primary_dense),
            (secondary_results[0][0], secondary_dense),
            phase_samples=int(comparison["phase_samples"]),
            coarse_shifts=int(comparison["coarse_shifts"]),
            shift_tolerance=float(comparison["shift_tolerance"]),
        )
        primary_multiplier = nontrivial_modulus(primary_result[1])
        secondary_multiplier = nontrivial_modulus(secondary_results[0][1])
        scaling_rows.append(
            {
                "mu": mu,
                "b": target_b,
                "separation_rms": separation["rms"],
                "primary_period": primary_result[0].period_time,
                "secondary_period": secondary_results[0][0].period_time,
                "primary_closure_error": primary_result[0].closure_error,
                "secondary_closure_error": secondary_results[0][0].closure_error,
                "primary_multiplier_modulus": primary_multiplier,
                "secondary_multiplier_modulus": secondary_multiplier,
                "multiplier_deviation_ratio": (1.0 - secondary_multiplier)
                / (primary_multiplier - 1.0),
            }
        )
        corrected_at_offset.append((primary_result, secondary_results))

    final_primary, final_secondary = corrected_at_offset[-1]
    final_parameters = RosslerParameters(
        a=a, b=b_star + float(manifest["mu_offsets"][-1]), c=c
    )
    dense_minus = dense_orbit(final_secondary[0][0], final_parameters, solver)
    dense_plus = dense_orbit(final_secondary[1][0], final_parameters, solver)
    secondary_identity = phase_aligned_rms(
        (final_secondary[0][0], dense_minus),
        (final_secondary[1][0], dense_plus),
        phase_samples=int(comparison["phase_samples"]),
        coarse_shifts=int(comparison["coarse_shifts"]),
        shift_tolerance=float(comparison["shift_tolerance"]),
    )

    log_mu = np.log([row["mu"] for row in scaling_rows])
    log_separation = np.log([row["separation_rms"] for row in scaling_rows])
    exponent, intercept = np.polyfit(log_mu, log_separation, 1)
    predicted = exponent * log_mu + intercept
    r_squared = 1.0 - float(np.sum((log_separation - predicted) ** 2)) / float(
        np.sum((log_separation - np.mean(log_separation)) ** 2)
    )
    ratios = np.asarray([row["multiplier_deviation_ratio"] for row in scaling_rows])
    max_closure = max(
        max(row["primary_closure_error"], row["secondary_closure_error"])
        for row in scaling_rows
    )
    stability_exchange = all(
        row["primary_multiplier_modulus"] > 1.0
        and row["secondary_multiplier_modulus"] < 1.0
        for row in scaling_rows
    )
    acceptance = manifest["acceptance"]
    passed = bool(
        all(
            len(branch["rows"])
            >= int(acceptance["minimum_branch_points_per_direction"])
            for branch in switched_branches
        )
        and max_closure <= float(acceptance["max_closure_error"])
        and secondary_identity["rms"] <= float(acceptance["max_secondary_arm_rms"])
        and scaling_rows[-1]["separation_rms"]
        >= float(acceptance["minimum_primary_secondary_rms"])
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
        "schema": "butterfly.separated-normal-form-receipt.v1",
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
        "event": {"a": a, "b": b_star, "c": c},
        "shooting_singular_values": singular_values.tolist(),
        "primary_tangent": primary_tangent.tolist(),
        "secondary_tangent": secondary_tangent.tolist(),
        "absolute_tangent_dot": float(abs(np.dot(primary_tangent, secondary_tangent))),
        "switched_branches": switched_branches,
        "scaling_rows": scaling_rows,
        "secondary_arm_identity_at_maximum_offset": secondary_identity,
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
        "interpretation_limit": "A second qualified point supports local persistence but not a uniform surface-wide normal form or exact symmetry.",
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps({key: value for key, value in receipt.items() if key not in ("switched_branches", "scaling_rows")}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
