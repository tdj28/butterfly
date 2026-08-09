#!/usr/bin/env python3
"""Switch the fixed-(a,b) period-2 flip onto its period-4 child in c."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.periodic_c import (
    correct_arclength_c,
    diagnose_periodic_c,
    extended_shooting_jacobian_c,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from switch_period1_c_flip import (
    _half_period_closure,
    _parent_distance,
    _parent_variables,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.period2-c-flip-switch-manifest.v1":
        raise SystemExit("unsupported period-2 c-flip switch manifest")
    event_bytes = args.event.read_bytes()
    parent_bytes = args.parent.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    if sha256_bytes(parent_bytes) != manifest["parent_receipt_sha256"]:
        raise SystemExit("parent receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    event_receipt = json.loads(event_bytes)
    parent_receipt = json.loads(parent_bytes)
    if event_receipt.get("schema") != "butterfly.period2-c-flip-receipt.v1":
        raise SystemExit("event receipt is not the period-2 c flip")
    if (
        parent_receipt.get("schema")
        != "butterfly.period2-c-arclength-to-flip-receipt.v1"
    ):
        raise SystemExit("parent receipt is not the period-2 arclength branch")
    a = float(event_receipt["fixed_a"])
    b = float(event_receipt["fixed_b"])
    event_c = float(event_receipt["corrected_c"])
    event = np.r_[
        event_receipt["nodes"][0],
        2.0 * float(event_receipt["period_time"]),
        event_c,
    ]
    solver = SolverConfig(**manifest["solver"])
    event_parameters = RosslerParameters(a=a, b=b, c=event_c)
    phase = rossler_rhs(0.0, event[:3], event_parameters)
    phase /= np.linalg.norm(phase)
    jacobian = extended_shooting_jacobian_c(
        event, a=a, b=b, phase_direction=phase, solver=solver
    )
    _, singular_values, right_vectors = np.linalg.svd(jacobian, full_matrices=True)
    null_basis = right_vectors[-2:].T
    rows = parent_receipt["rows"]
    below = max(
        (row for row in rows if float(row["parameters"]["c"]) < event_c),
        key=lambda row: float(row["parameters"]["c"]),
    )
    above = min(
        (row for row in rows if float(row["parameters"]["c"]) > event_c),
        key=lambda row: float(row["parameters"]["c"]),
    )
    observed_primary = _parent_variables(above) - _parent_variables(below)
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
    continuation = manifest["continuation"]
    step_length = float(continuation["step_length"])
    started = time.perf_counter()
    branches = []
    for direction in (-1, 1):
        tangent = direction * secondary_tangent
        predictor = event + step_length * tangent
        corrected, status = correct_arclength_c(
            predictor,
            tangent,
            event[:3],
            event_c,
            a=a,
            b=b,
            solver=solver,
            tolerance=float(manifest["corrector"]["tolerance"]),
            max_evaluations=int(manifest["corrector"]["maximum_evaluations"]),
        )
        points = [event]
        branch_rows = []
        statuses = [{**status, "step_index": 0}]
        if status["success"]:
            points.append(corrected)
            row = diagnose_periodic_c(corrected, a=a, b=b, solver=solver)
            row["half_period_closure"] = _half_period_closure(row, solver)
            branch_rows.append(row)
        for step_index in range(1, int(continuation["steps_per_direction"])):
            if len(points) < 2:
                break
            tangent = points[-1] - points[-2]
            tangent /= np.linalg.norm(tangent)
            predictor = points[-1] + step_length * tangent
            corrected, status = correct_arclength_c(
                predictor,
                tangent,
                points[-1][:3],
                float(points[-1][4]),
                a=a,
                b=b,
                solver=solver,
                tolerance=float(manifest["corrector"]["tolerance"]),
                max_evaluations=int(manifest["corrector"]["maximum_evaluations"]),
            )
            statuses.append({**status, "step_index": step_index})
            if not status["success"]:
                break
            points.append(corrected)
            row = diagnose_periodic_c(corrected, a=a, b=b, solver=solver)
            row["half_period_closure"] = _half_period_closure(row, solver)
            branch_rows.append(row)
            if not (
                float(continuation["c_guard"][0])
                <= corrected[4]
                <= float(continuation["c_guard"][1])
            ):
                break
        branches.append(
            {
                "direction": direction,
                "point_count": len(branch_rows),
                "rows": branch_rows,
                "statuses": statuses,
                "endpoint_distance_from_doubled_parent": _parent_distance(
                    points[-1], rows
                ),
            }
        )
    acceptance = manifest["acceptance"]
    qualified = [
        branch
        for branch in branches
        if branch["point_count"] >= int(acceptance["minimum_points_per_direction"])
        and branch["endpoint_distance_from_doubled_parent"]
        >= float(acceptance["minimum_endpoint_distance"])
        and branch["rows"][-1]["half_period_closure"]
        >= float(acceptance["minimum_endpoint_half_period_closure"])
    ]
    all_rows = [row for branch in branches for row in branch["rows"]]
    tangent_dot = abs(float(np.dot(primary_tangent, secondary_tangent)))
    output = {
        "schema": "butterfly.period2-c-flip-switch-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "parent_receipt_sha256": sha256_bytes(parent_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "fixed_a": a,
        "fixed_b": b,
        "event_variables": event.tolist(),
        "shooting_singular_values": singular_values.tolist(),
        "primary_tangent": primary_tangent.tolist(),
        "secondary_tangent": secondary_tangent.tolist(),
        "absolute_tangent_dot": tangent_dot,
        "branches": branches,
        "qualified_directions": [branch["direction"] for branch in qualified],
        "elapsed_seconds": time.perf_counter() - started,
    }
    output["passed"] = bool(
        singular_values[-1] <= float(acceptance["maximum_small_singular_value"])
        and tangent_dot <= float(acceptance["maximum_tangent_dot"])
        and len(qualified) >= int(acceptance["minimum_qualified_directions"])
        and all(
            row["closure_error"] <= float(acceptance["maximum_closure_error"])
            for row in all_rows
        )
    )
    output["scientific_scope"] = (
        "local period-4 branch switch at the second fixed-path flip; independent "
        "child identity, stability exchange, and attraction require qualification"
    )
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {
                "passed": output["passed"],
                "shooting_singular_values": output["shooting_singular_values"],
                "absolute_tangent_dot": tangent_dot,
                "branches": [
                    {
                        "direction": branch["direction"],
                        "points": branch["point_count"],
                        "c_range": (
                            [
                                min(row["parameters"]["c"] for row in branch["rows"]),
                                max(row["parameters"]["c"] for row in branch["rows"]),
                            ]
                            if branch["rows"]
                            else None
                        ),
                        "endpoint_distance": branch[
                            "endpoint_distance_from_doubled_parent"
                        ],
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
