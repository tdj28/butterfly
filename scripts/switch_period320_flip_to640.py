#!/usr/bin/env python3
"""Switch the segmented period-320 flip to period-640 candidates."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from multiple_shooting_core import base_system, correct_arclength


def doubled_variables(row, b, segment_count):
    nodes = np.asarray(row["nodes"], dtype=float)
    if 2 * len(nodes) != segment_count:
        raise ValueError("source node count does not double to target segment count")
    return np.r_[np.tile(nodes, (2, 1)).ravel(), 2.0 * row["period_time"], b]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.period320-to-640-switch-manifest.v1":
        raise SystemExit("unsupported period-640 switch manifest")
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
    best = event["best_evaluation"]
    b_star = float(event["b_estimate"])
    segment_count = int(manifest["segment_count"])
    event_variables = doubled_variables(best, b_star, segment_count)
    a = float(manifest["fixed_a"])
    c = float(manifest["fixed_c"])
    solver = SolverConfig(**manifest["solver"])
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
        (row for row in parent["rows"] if row["b"] < b_star),
        key=lambda row: row["b"],
    )
    above = min(
        (row for row in parent["rows"] if row["b"] > b_star),
        key=lambda row: row["b"],
    )
    primary_difference = doubled_variables(above, above["b"], segment_count) - doubled_variables(
        below, below["b"], segment_count
    )
    primary_difference /= np.linalg.norm(primary_difference)
    primary_tangent = null_basis @ (null_basis.T @ primary_difference)
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
                nodes = corrected[: 3 * segment_count].reshape(segment_count, 3)
                duration = float(corrected[3 * segment_count])
                b = float(corrected[3 * segment_count + 1])
                row.update(
                    {
                        "b": b,
                        "parameter_displacement": b_star - b,
                        "period_time": duration,
                        "period_ratio_to_parent": duration / best["period_time"],
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
        "schema": "butterfly.period320-to-640-switch.v1",
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
        "parent_period_time": best["period_time"],
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
