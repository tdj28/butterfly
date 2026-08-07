#!/usr/bin/env python3
"""Switch a high-period flip with a validated segmented shooting system."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from multiple_shooting_core import base_system, correct_arclength, seed_variables
from validate_multiple_shooting_switch import half_closure


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.high-period-multiple-shooting-switch-manifest.v1":
        raise SystemExit("unsupported high-period switch manifest")
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

    event = json.loads(event_bytes)
    parent = json.loads(parent_bytes)
    parent_rows = next(
        branch["rows"]
        for branch in parent["branches"]
        if branch["direction"] == manifest["parent_branch_direction"]
    )
    best = event["best_evaluation"]
    a = float(manifest["fixed_a"])
    c = float(manifest["fixed_c"])
    b_star = float(event["b_estimate"])
    segment_count = int(manifest["segment_count"])
    if segment_count % 2:
        raise SystemExit("segment_count must be even for the half-period test")
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
    event_residual, event_jacobian = base_system(
        event_variables,
        segment_count=segment_count,
        a=a,
        c=c,
        phase=phase,
        phase_reference=event_variables[:3],
        solver=solver,
    )
    _, singular_values, right_vectors = np.linalg.svd(
        event_jacobian, full_matrices=True
    )
    null_basis = right_vectors[-2:].T

    below = max(
        (row for row in parent_rows if row["b"] < b_star), key=lambda row: row["b"]
    )
    above = min(
        (row for row in parent_rows if row["b"] > b_star), key=lambda row: row["b"]
    )
    primary_variables = []
    for row in (below, above):
        primary_variables.append(
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
    observed_primary = primary_variables[1] - primary_variables[0]
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
    acceptance = manifest["acceptance"]
    for step in manifest["step_lengths"]:
        for direction in (-1, 1):
            tangent = direction * secondary_tangent
            predictor = event_variables + float(step) * tangent
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
                nodes = corrected[: 3 * segment_count].reshape(segment_count, 3)
                duration = float(corrected[3 * segment_count])
                b = float(corrected[3 * segment_count + 1])
                current_parameters = RosslerParameters(a=a, b=b, c=c)
                row.update(
                    {
                        "b": b,
                        "parameter_displacement": b_star - b,
                        "period_time": duration,
                        "period_ratio_to_parent": duration / best["period_time"],
                        "half_period_closure": half_closure(
                            nodes[0], duration, current_parameters, solver
                        ),
                        "half_node_rms": float(
                            np.sqrt(
                                np.mean(
                                    (nodes[: segment_count // 2]
                                    - nodes[segment_count // 2 :])
                                    ** 2
                                )
                            )
                        ),
                        "initial_state": nodes[0].tolist(),
                        "nodes": nodes.tolist(),
                    }
                )
                row["accepted"] = bool(
                    status["matching_residual"]
                    <= acceptance["max_matching_residual"]
                    and status["phase_residual"] <= acceptance["max_phase_residual"]
                    and row["half_period_closure"]
                    >= acceptance["minimum_half_period_closure"]
                    and row["half_node_rms"] >= acceptance["minimum_half_node_rms"]
                    and 0.0
                    < row["parameter_displacement"]
                    <= acceptance["maximum_parameter_displacement"]
                    and abs(row["period_ratio_to_parent"] - 2.0)
                    <= acceptance["maximum_period_ratio_error"]
                )
            else:
                row["accepted"] = False
            attempts.append(row)

    accepted = [row for row in attempts if row["accepted"]]
    output = {
        "schema": "butterfly.high-period-multiple-shooting-switch.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "event_b": b_star,
        "parent_period_time": float(best["period_time"]),
        "segment_count": segment_count,
        "event_matching_residual": float(np.linalg.norm(event_residual[:-1])),
        "event_smallest_singular_values": singular_values[-2:].tolist(),
        "absolute_tangent_dot": abs(float(np.dot(primary_tangent, secondary_tangent))),
        "attempts": attempts,
        "accepted_candidates": accepted,
        "passed": bool(
            len(accepted) >= acceptance["minimum_accepted_candidates"]
        ),
    }
    atomic_write(args.output, canonical_json(output))
    printed = {**output, "attempts": len(attempts)}
    printed["accepted_candidates"] = [
        {key: value for key, value in row.items() if key != "nodes"}
        for row in accepted
    ]
    print(json.dumps(printed, sort_keys=True))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
