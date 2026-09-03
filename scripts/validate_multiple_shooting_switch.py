#!/usr/bin/env python3
"""Validate multiple-shooting switching against a known doubled child."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from compare_periodic_orbit_identity import dense_orbit, phase_aligned_rms
from multiple_shooting_core import base_system, correct_arclength, seed_variables
from qualify_separated_normal_form import correct_fixed_b, interpolate_branch


def half_closure(state, duration, parameters, solver):
    result = solve_ivp(
        lambda t, x: rossler_rhs(t, x, parameters),
        (0.0, 0.5 * duration),
        state,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
    )
    return float(np.linalg.norm(result.y[:, -1] - state))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--known-child", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    inputs = {
        "event": args.event.read_bytes(),
        "parent": args.parent.read_bytes(),
        "known_child": args.known_child.read_bytes(),
    }
    for key, data in inputs.items():
        if sha256_bytes(data) != manifest[f"{key}_receipt_sha256"]:
            raise SystemExit(f"{key} receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["dirty"]:
        raise SystemExit("clean source required")
    event = json.loads(inputs["event"])
    parent_receipt = json.loads(inputs["parent"])
    child_receipt = json.loads(inputs["known_child"])
    parent_rows = next(
        branch["rows"]
        for branch in parent_receipt["branches"]
        if branch["direction"] == manifest["parent_branch_direction"]
    )
    child_rows = next(
        branch["rows"]
        for branch in child_receipt["branches"]
        if branch["direction"] == manifest["known_child_direction"]
    )
    best = event["best_evaluation"]
    a = manifest["fixed_a"]
    c = manifest["fixed_c"]
    b_star = event["b_estimate"]
    segment_count = manifest["segment_count"]
    solver = SolverConfig(**manifest["solver"])
    event_variables = seed_variables(
        best["initial_state"],
        2.0 * best["period_time"],
        b_star,
        segment_count=segment_count,
        a=a,
        c=c,
        solver=solver,
    )
    parameters = RosslerParameters(a=a, b=b_star, c=c)
    phase = rossler_rhs(0.0, event_variables[:3], parameters)
    phase /= np.linalg.norm(phase)
    _, event_jacobian = base_system(
        event_variables,
        segment_count=segment_count,
        a=a,
        c=c,
        phase=phase,
        phase_reference=event_variables[:3],
        solver=solver,
    )
    _, singular_values, right_vectors = np.linalg.svd(event_jacobian, full_matrices=True)
    null_basis = right_vectors[-2:].T
    below = max((row for row in parent_rows if row["b"] < b_star), key=lambda row: row["b"])
    above = min((row for row in parent_rows if row["b"] > b_star), key=lambda row: row["b"])
    primary_vectors = []
    for row in (below, above):
        primary_vectors.append(
            seed_variables(
                row["initial_state"],
                2.0 * row["period_time"],
                row["b"],
                segment_count=segment_count,
                a=a,
                c=c,
                solver=solver,
            )
        )
    observed_primary = primary_vectors[1] - primary_vectors[0]
    observed_primary /= np.linalg.norm(observed_primary)
    primary_tangent = null_basis @ (null_basis.T @ observed_primary)
    primary_tangent /= np.linalg.norm(primary_tangent)
    secondary_tangent = null_basis[:, 0] - primary_tangent * np.dot(
        primary_tangent, null_basis[:, 0]
    )
    if np.linalg.norm(secondary_tangent) < 1e-8:
        secondary_tangent = null_basis[:, 1] - primary_tangent * np.dot(
            primary_tangent, null_basis[:, 1]
        )
    secondary_tangent /= np.linalg.norm(secondary_tangent)
    attempts = []
    qualifying = []
    for step in manifest["step_lengths"]:
        for direction in (-1, 1):
            tangent = direction * secondary_tangent
            predictor = event_variables + step * tangent
            corrected, status = correct_arclength(
                predictor,
                tangent,
                segment_count=segment_count,
                a=a,
                c=c,
                phase=phase,
                phase_reference=event_variables[:3],
                solver=solver,
                tolerance=manifest["corrector"]["tolerance"],
                max_evaluations=manifest["corrector"]["max_evaluations"],
            )
            row = {"step_length": step, "direction": direction, "status": status}
            if status["success"]:
                state = corrected[:3]
                duration = corrected[3 * segment_count]
                b = corrected[3 * segment_count + 1]
                row.update({"b": b, "period_time": duration})
                current_parameters = RosslerParameters(a=a, b=b, c=c)
                row["half_period_closure"] = half_closure(
                    state, duration, current_parameters, solver
                )
                if min(item["b"] for item in child_rows) <= b <= max(
                    item["b"] for item in child_rows
                ):
                    known_seed = interpolate_branch(child_rows, b)
                    known = correct_fixed_b(
                        a=a,
                        b=b,
                        c=c,
                        initial_state=known_seed[0],
                        period_time=known_seed[1],
                        solver=solver,
                        tolerance=manifest["corrector"]["tolerance"],
                        max_evaluations=manifest["corrector"]["max_evaluations"],
                    )[0]
                    candidate = correct_fixed_b(
                        a=a,
                        b=b,
                        c=c,
                        initial_state=state,
                        period_time=duration,
                        solver=solver,
                        tolerance=manifest["corrector"]["tolerance"],
                        max_evaluations=manifest["corrector"]["max_evaluations"],
                    )[0]
                    identity = phase_aligned_rms(
                        (candidate, dense_orbit(candidate, current_parameters, solver)),
                        (known, dense_orbit(known, current_parameters, solver)),
                        phase_samples=manifest["comparison"]["phase_samples"],
                        coarse_shifts=manifest["comparison"]["coarse_shifts"],
                        shift_tolerance=manifest["comparison"]["shift_tolerance"],
                    )
                    row["single_shooting_closure"] = candidate.closure_error
                    row["known_child_identity"] = identity
                    qualifying.append(row)
            attempts.append(row)
    acceptance = manifest["acceptance"]
    accepted = [
        row
        for row in qualifying
        if row["status"]["matching_residual"] <= acceptance["max_matching_residual"]
        and row["half_period_closure"] >= acceptance["minimum_half_period_closure"]
        and row["single_shooting_closure"] <= acceptance["max_closure_error"]
        and row["known_child_identity"]["rms"] <= acceptance["max_identity_rms"]
    ]
    output = {
        "schema": "butterfly.multiple-shooting-switch-validation.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "segment_count": segment_count,
        "event_smallest_singular_value": float(singular_values[-1]),
        "absolute_tangent_dot": abs(float(np.dot(primary_tangent, secondary_tangent))),
        "attempts": attempts,
        "accepted_candidates": accepted,
        "passed": bool(len(accepted) >= acceptance["minimum_accepted_candidates"]),
    }
    atomic_write(args.output, canonical_json(output))
    print(json.dumps({**output, "attempts": len(attempts)}, sort_keys=True))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
