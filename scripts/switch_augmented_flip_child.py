#!/usr/bin/env python3
"""Switch an exact augmented flip event onto its doubled child branch."""
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
from validate_multiple_shooting_switch import half_closure


def doubled_event_variables(event):
    nodes = np.asarray(event["nodes"], dtype=float)
    return np.r_[
        np.tile(nodes, (2, 1)).ravel(),
        2.0 * float(event["period_time"]),
        float(event["corrected_b"]),
    ]


def phase_fixed_child_tangent(event, parameters, phase):
    nodes = np.asarray(event["nodes"], dtype=float)
    tangents = np.asarray(event["tangent_nodes"], dtype=float)
    child_mode = np.vstack((tangents, -tangents))
    flow_mode = np.vstack(
        ([rossler_rhs(0.0, node, parameters) for node in nodes],) * 2
    )
    coefficient = -float(np.dot(phase, child_mode[0])) / float(
        np.dot(phase, flow_mode[0])
    )
    state_mode = child_mode + coefficient * flow_mode
    full_mode = np.r_[state_mode.ravel(), 0.0, 0.0]
    return full_mode / np.linalg.norm(full_mode), coefficient


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.augmented-flip-child-switch-manifest.v1":
        raise SystemExit("unsupported augmented flip child switch manifest")
    event_bytes = args.event.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    event = json.loads(event_bytes)
    if event.get("schema") != manifest["event_schema"] or not event.get("passed"):
        raise SystemExit("a passed analytic augmented event is required")
    source_segment_count = int(event["segment_count"])
    segment_count = int(manifest["segment_count"])
    if segment_count != 2 * source_segment_count:
        raise SystemExit("target segment count must double the event source")
    event_variables = doubled_event_variables(event)
    a = float(manifest["fixed_a"])
    c = float(manifest["fixed_c"])
    b_star = float(event["corrected_b"])
    parameters = RosslerParameters(a=a, b=b_star, c=c)
    solver = SolverConfig(**manifest["solver"])
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
    secondary_tangent, phase_coefficient = phase_fixed_child_tangent(
        event, parameters, phase
    )
    null_residual = float(np.linalg.norm(event_jacobian @ secondary_tangent))
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
                        "period_ratio_to_parent": duration
                        / float(event["period_time"]),
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
            print(
                json.dumps(
                    {
                        "step_length": step,
                        "direction": direction,
                        "accepted": row["accepted"],
                        "status": status,
                        "b": row.get("b"),
                        "half_node_rms": row.get("half_node_rms"),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
    accepted = [row for row in attempts if row["accepted"]]
    output = {
        "schema": "butterfly.augmented-flip-child-switch.v1",
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
        "parent_period_time": float(event["period_time"]),
        "source_segment_count": source_segment_count,
        "segment_count": segment_count,
        "event_matching_residual": float(np.linalg.norm(event_residual[:-1])),
        "phase_fix_coefficient": phase_coefficient,
        "secondary_null_residual": null_residual,
        "attempts": attempts,
        "accepted_candidates": accepted,
        "passed": bool(
            null_residual <= acceptance["max_secondary_null_residual"]
            and len(accepted) >= acceptance["minimum_accepted_candidates"]
        ),
    }
    atomic_write(args.output, canonical_json(output))
    printed = {**output, "attempts": len(attempts)}
    printed["accepted_candidates"] = [
        {key: value for key, value in row.items() if key != "nodes"}
        for row in accepted
    ]
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
