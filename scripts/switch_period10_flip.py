#!/usr/bin/env python3
"""Switch a verified period-10 flip to its doubled-period shooting branch."""
from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from pseudo_arclength_periodic_b import correct_arclength, diagnose
from switch_periodic_branch import extended_shooting_jacobian


def parent_variables(row):
    return np.r_[row["initial_state"], 2.0 * row["period_time"], row["b"]]


def parent_distance(point, rows):
    ordered = sorted(rows, key=lambda row: row["b"])
    b_values = np.asarray([row["b"] for row in ordered])
    parent = np.empty(5)
    for index in range(3):
        parent[index] = np.interp(
            point[4], b_values, [row["initial_state"][index] for row in ordered]
        )
    parent[3] = np.interp(
        point[4], b_values, [2.0 * row["period_time"] for row in ordered]
    )
    parent[4] = point[4]
    return float(np.linalg.norm(point - parent))


def half_period_closure(row, solver):
    parameters = RosslerParameters(a=row["a"], b=row["b"], c=row["c"])
    state = np.asarray(row["initial_state"])
    result = solve_ivp(
        lambda t, x: rossler_rhs(t, x, parameters),
        (0.0, 0.5 * row["period_time"]),
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
    parser.add_argument("--parent-branch", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    event_bytes = args.event.read_bytes()
    branch_bytes = args.parent_branch.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    if sha256_bytes(branch_bytes) != manifest["parent_branch_receipt_sha256"]:
        raise SystemExit("parent branch receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["dirty"]:
        raise SystemExit("clean source required")
    event_receipt = json.loads(event_bytes)
    branch_receipt = json.loads(branch_bytes)
    parent_rows = next(
        branch["rows"]
        for branch in branch_receipt["branches"]
        if branch["direction"] == manifest["parent_branch_direction"]
    )
    best = event_receipt["best_evaluation"]
    a = float(parent_rows[0]["a"])
    c = float(parent_rows[0]["c"])
    b = float(event_receipt["b_estimate"])
    event = np.r_[best["initial_state"], 2.0 * best["period_time"], b]
    solver = SolverConfig(**manifest["solver"])
    parameters = RosslerParameters(a=a, b=b, c=c)
    phase = rossler_rhs(0.0, event[:3], parameters)
    phase /= np.linalg.norm(phase)
    jacobian = extended_shooting_jacobian(
        event, a=a, c=c, phase_direction=phase, solver=solver
    )
    _, singular_values, right_vectors = np.linalg.svd(jacobian, full_matrices=True)
    null_basis = right_vectors[-2:].T
    below = max((row for row in parent_rows if row["b"] < b), key=lambda row: row["b"])
    above = min((row for row in parent_rows if row["b"] > b), key=lambda row: row["b"])
    observed_primary = parent_variables(above) - parent_variables(below)
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
    started = time.perf_counter()
    branches = []
    for direction in (-1, 1):
        tangent = direction * secondary_tangent
        predictor = event + manifest["continuation"]["step_length"] * tangent
        corrected, status = correct_arclength(
            predictor,
            tangent,
            event[:3],
            b,
            a=a,
            c=c,
            solver=solver,
            tolerance=manifest["corrector"]["tolerance"],
            max_evaluations=manifest["corrector"]["max_evaluations"],
        )
        points = [event]
        rows = []
        statuses = [status]
        if status["success"]:
            points.append(corrected)
            row = diagnose(corrected, a=a, c=c, solver=solver)
            row["half_period_closure"] = half_period_closure(row, solver)
            rows.append(row)
        for _ in range(1, manifest["continuation"]["steps_per_direction"]):
            if len(points) < 2:
                break
            tangent = points[-1] - points[-2]
            tangent /= np.linalg.norm(tangent)
            predictor = points[-1] + manifest["continuation"]["step_length"] * tangent
            corrected, status = correct_arclength(
                predictor,
                tangent,
                points[-1][:3],
                float(points[-1][4]),
                a=a,
                c=c,
                solver=solver,
                tolerance=manifest["corrector"]["tolerance"],
                max_evaluations=manifest["corrector"]["max_evaluations"],
            )
            statuses.append(status)
            if not status["success"]:
                break
            points.append(corrected)
            row = diagnose(corrected, a=a, c=c, solver=solver)
            row["half_period_closure"] = half_period_closure(row, solver)
            rows.append(row)
            if not (
                manifest["continuation"]["b_guard"][0]
                <= corrected[4]
                <= manifest["continuation"]["b_guard"][1]
            ):
                break
        branches.append(
            {
                "direction": direction,
                "rows": rows,
                "statuses": statuses,
                "point_count": len(rows),
                "endpoint_distance_from_doubled_parent": parent_distance(
                    points[-1], parent_rows
                ),
            }
        )
    all_rows = [row for branch in branches for row in branch["rows"]]
    acceptance = manifest["acceptance"]
    qualified_branches = [
        branch
        for branch in branches
        if branch["point_count"] >= acceptance["minimum_points_per_direction"]
        and branch["endpoint_distance_from_doubled_parent"]
        >= acceptance["minimum_endpoint_distance"]
        and branch["rows"][-1]["half_period_closure"]
        >= acceptance["minimum_endpoint_half_period_closure"]
    ]
    output = {
        "schema": manifest.get(
            "output_schema", "butterfly.period10-flip-branch-switch.v1"
        ),
        "experiment_id": manifest["experiment_id"],
        "parent_period_label": manifest.get("parent_period_label", 10),
        "child_period_label": manifest.get("child_period_label", 20),
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "parent_branch_receipt_sha256": sha256_bytes(branch_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "event_variables": event.tolist(),
        "shooting_singular_values": singular_values.tolist(),
        "primary_tangent": primary_tangent.tolist(),
        "secondary_tangent": secondary_tangent.tolist(),
        "absolute_tangent_dot": abs(float(np.dot(primary_tangent, secondary_tangent))),
        "branches": branches,
        "elapsed_seconds": time.perf_counter() - started,
    }
    output["passed"] = (
        singular_values[-1] <= acceptance["max_small_singular_value"]
        and output["absolute_tangent_dot"] <= acceptance["max_tangent_dot"]
        and len(qualified_branches) >= manifest.get("required_distinct_arms", 2)
        and all(row["closure_error"] <= acceptance["max_closure_error"] for row in all_rows)
    )
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {
                "passed": output["passed"],
                "singular_values": output["shooting_singular_values"],
                "absolute_tangent_dot": output["absolute_tangent_dot"],
                "branches": [
                    {
                        "direction": branch["direction"],
                        "points": branch["point_count"],
                        "distance": branch["endpoint_distance_from_doubled_parent"],
                        "endpoint_half_period_closure": (
                            branch["rows"][-1]["half_period_closure"]
                            if branch["rows"]
                            else None
                        ),
                        "endpoint_modulus": (
                            branch["rows"][-1]["max_nontrivial_multiplier_modulus"]
                            if branch["rows"]
                            else None
                        ),
                    }
                    for branch in branches
                ],
            },
            sort_keys=True,
        )
    )
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
