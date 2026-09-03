#!/usr/bin/env python3
"""Switch and continue a secondary periodic-orbit branch at a +1 event."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from butterfly import RosslerParameters, SolverConfig, rossler_jacobian, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from pseudo_arclength_periodic_b import correct_arclength, diagnose


def extended_shooting_jacobian(
    variables: np.ndarray,
    *,
    a: float,
    c: float,
    phase_direction: np.ndarray,
    solver: SolverConfig,
) -> np.ndarray:
    state = variables[:3]
    duration = float(variables[3])
    b = float(variables[4])
    parameters = RosslerParameters(a=a, b=b, c=c)
    initial = np.concatenate(
        (state, np.eye(3, dtype=np.float64).ravel(), np.zeros(3, dtype=np.float64))
    )

    def augmented_rhs(time: float, augmented: np.ndarray) -> np.ndarray:
        current = augmented[:3]
        jacobian = rossler_jacobian(current, parameters)
        transition = augmented[3:12].reshape(3, 3)
        sensitivity = augmented[12:15]
        return np.concatenate(
            (
                rossler_rhs(time, current, parameters),
                (jacobian @ transition).ravel(),
                jacobian @ sensitivity + np.asarray((0.0, 0.0, 1.0)),
            )
        )

    integration = solve_ivp(
        augmented_rhs,
        (0.0, duration),
        initial,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
    )
    if not integration.success:
        raise RuntimeError(f"extended Jacobian integration failed: {integration.message}")
    final = np.asarray(integration.y[:, -1], dtype=np.float64)
    final_state = final[:3]
    transition = final[3:12].reshape(3, 3)
    sensitivity = final[12:15]
    jacobian = np.empty((4, 5), dtype=np.float64)
    jacobian[:3, :3] = transition - np.eye(3)
    jacobian[:3, 3] = rossler_rhs(duration, final_state, parameters)
    jacobian[:3, 4] = sensitivity
    jacobian[3, :3] = phase_direction
    jacobian[3, 3:] = 0.0
    return jacobian


def interpolated_primary_distance(variables: np.ndarray, rows: list[dict]) -> float:
    ordered = sorted(rows, key=lambda row: float(row["b"]))
    b_values = np.asarray([row["b"] for row in ordered], dtype=float)
    primary = np.empty(5, dtype=float)
    for index in range(3):
        primary[index] = np.interp(
            variables[4], b_values, [row["initial_state"][index] for row in ordered]
        )
    primary[3] = np.interp(
        variables[4], b_values, [row["period_time"] for row in ordered]
    )
    primary[4] = variables[4]
    return float(np.linalg.norm(variables - primary))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event-receipt", type=Path, required=True)
    parser.add_argument("--primary-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.periodic-branch-switch-manifest.v1":
        raise SystemExit("unsupported branch-switch manifest")
    event_bytes = args.event_receipt.read_bytes()
    primary_bytes = args.primary_receipt.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash does not match manifest")
    if sha256_bytes(primary_bytes) != manifest["primary_receipt_sha256"]:
        raise SystemExit("primary receipt hash does not match manifest")
    event = json.loads(event_bytes)
    primary = json.loads(primary_bytes)
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("branch switching requires clean source")

    a = float(event["fixed_a"])
    c = float(event["fixed_c"])
    event_variables = np.concatenate(
        (
            np.asarray(event["initial_state"], dtype=float),
            (float(event["period_time"]), float(event["corrected_b"])),
        )
    )
    event_parameters = RosslerParameters(a=a, b=event_variables[4], c=c)
    phase_direction = rossler_rhs(0.0, event_variables[:3], event_parameters)
    phase_direction /= np.linalg.norm(phase_direction)
    solver = SolverConfig(**manifest["solver"])
    jacobian = extended_shooting_jacobian(
        event_variables,
        a=a,
        c=c,
        phase_direction=phase_direction,
        solver=solver,
    )
    _, singular_values, right_vectors = np.linalg.svd(jacobian, full_matrices=True)
    null_basis = right_vectors[-2:].T

    source_rows = primary["rows"]
    below = max(
        (row for row in source_rows if float(row["b"]) < event_variables[4]),
        key=lambda row: float(row["b"]),
    )
    above = min(
        (row for row in source_rows if float(row["b"]) > event_variables[4]),
        key=lambda row: float(row["b"]),
    )
    below_variables = np.concatenate(
        (np.asarray(below["initial_state"]), (below["period_time"], below["b"]))
    )
    above_variables = np.concatenate(
        (np.asarray(above["initial_state"]), (above["period_time"], above["b"]))
    )
    observed_primary = above_variables - below_variables
    observed_primary /= np.linalg.norm(observed_primary)
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

    started = time.perf_counter()
    continuation = manifest["continuation"]
    step_length = float(continuation["step_length"])
    branch_results = []
    for direction in (-1.0, 1.0):
        tangent = direction * secondary_tangent
        predictor = event_variables + step_length * tangent
        corrected, status = correct_arclength(
            predictor,
            tangent,
            event_variables[:3],
            float(event_variables[4]),
            a=a,
            c=c,
            solver=solver,
            tolerance=float(manifest["corrector"]["tolerance"]),
            max_evaluations=int(manifest["corrector"]["max_evaluations"]),
        )
        points = [event_variables]
        rows = []
        statuses = [{**status, "step_index": 0}]
        if status["success"]:
            points.append(corrected)
            rows.append(diagnose(corrected, a=a, c=c, solver=solver))
        for step_index in range(1, int(continuation["steps_per_direction"])):
            if len(points) < 2:
                break
            tangent = points[-1] - points[-2]
            tangent /= np.linalg.norm(tangent)
            predictor = points[-1] + step_length * tangent
            corrected, status = correct_arclength(
                predictor,
                tangent,
                points[-1][:3],
                float(points[-1][4]),
                a=a,
                c=c,
                solver=solver,
                tolerance=float(manifest["corrector"]["tolerance"]),
                max_evaluations=int(manifest["corrector"]["max_evaluations"]),
            )
            statuses.append({**status, "step_index": step_index})
            if not status["success"]:
                break
            points.append(corrected)
            rows.append(diagnose(corrected, a=a, c=c, solver=solver))
            if not (
                float(continuation["b_guard_min"])
                <= corrected[4]
                <= float(continuation["b_guard_max"])
            ):
                break
        endpoint_distance = (
            interpolated_primary_distance(points[-1], source_rows)
            if len(points) > 1
            else 0.0
        )
        branch_results.append(
            {
                "direction": int(direction),
                "point_count": len(rows),
                "rows": rows,
                "statuses": statuses,
                "endpoint_distance_from_primary": endpoint_distance,
            }
        )

    acceptance = manifest["acceptance"]
    tangent_dot = float(abs(np.dot(primary_tangent, secondary_tangent)))
    all_rows = [row for branch in branch_results for row in branch["rows"]]
    max_closure = max((row["closure_error"] for row in all_rows), default=float("inf"))
    passed = bool(
        singular_values[-1] <= float(acceptance["max_second_smallest_singular_value"])
        and tangent_dot <= float(acceptance["max_branch_tangent_dot"])
        and max_closure <= float(acceptance["max_closure_error"])
        and all(
            branch["point_count"] >= int(acceptance["minimum_points_per_direction"])
            and branch["endpoint_distance_from_primary"]
            >= float(acceptance["minimum_endpoint_distance_from_primary"])
            for branch in branch_results
        )
    )
    receipt = {
        "schema": "butterfly.periodic-branch-switch-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "primary_receipt_sha256": sha256_bytes(primary_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "event_variables": event_variables.tolist(),
        "shooting_singular_values": singular_values.tolist(),
        "primary_tangent": primary_tangent.tolist(),
        "secondary_tangent": secondary_tangent.tolist(),
        "absolute_tangent_dot": tangent_dot,
        "branches": branch_results,
        "max_closure_error": max_closure,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "interpretation_limit": "Distinct local branch correction does not classify the generic branch point without branch identity, symmetry, and local normal-form tests.",
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps({key: value for key, value in receipt.items() if key != "branches"}, sort_keys=True))
    print(json.dumps({"branch_summaries": [{key: value for key, value in branch.items() if key not in ("rows", "statuses")} for branch in branch_results]}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
