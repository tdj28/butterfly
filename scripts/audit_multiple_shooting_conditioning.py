#!/usr/bin/env python3
"""Audit segmented multiple-shooting conditioning at a high-period flip."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from butterfly import RosslerParameters, SolverConfig, rossler_jacobian, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def segment_system(state, duration, parameters, solver):
    initial = np.r_[state, np.eye(3).ravel(), np.zeros(3)]

    def augmented(time, value):
        point = value[:3]
        jacobian = rossler_jacobian(point, parameters)
        transition = value[3:12].reshape(3, 3)
        sensitivity = value[12:15]
        return np.r_[
            rossler_rhs(time, point, parameters),
            (jacobian @ transition).ravel(),
            jacobian @ sensitivity + np.asarray((0.0, 0.0, 1.0)),
        ]

    result = solve_ivp(
        augmented,
        (0.0, duration),
        initial,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
    )
    if not result.success:
        raise RuntimeError(result.message)
    final = result.y[:, -1]
    return final[:3], final[3:12].reshape(3, 3), final[12:15]


def audit(segment_count, state, total_duration, parameters, phase, solver):
    segment_duration = total_duration / segment_count
    nodes = [state]
    transitions = []
    sensitivities = []
    endpoints = []
    for _ in range(segment_count):
        endpoint, transition, sensitivity = segment_system(
            nodes[-1], segment_duration, parameters, solver
        )
        endpoints.append(endpoint)
        transitions.append(transition)
        sensitivities.append(sensitivity)
        nodes.append(endpoint)
    rows = 3 * segment_count + 1
    columns = 3 * segment_count + 2
    jacobian = np.zeros((rows, columns))
    residuals = []
    for index in range(segment_count):
        row = slice(3 * index, 3 * index + 3)
        current = slice(3 * index, 3 * index + 3)
        next_index = (index + 1) % segment_count
        following = slice(3 * next_index, 3 * next_index + 3)
        jacobian[row, current] += transitions[index]
        jacobian[row, following] -= np.eye(3)
        jacobian[row, 3 * segment_count] = rossler_rhs(
            segment_duration, endpoints[index], parameters
        ) / segment_count
        jacobian[row, 3 * segment_count + 1] = sensitivities[index]
        target = nodes[index + 1] if index + 1 < segment_count else state
        residuals.append(endpoints[index] - target)
    jacobian[-1, :3] = phase
    singular_values = np.linalg.svd(jacobian, compute_uv=False)
    transition_conditions = [np.linalg.cond(matrix) for matrix in transitions]
    residual = np.concatenate(residuals)
    return {
        "segment_count": segment_count,
        "segment_duration": segment_duration,
        "smallest_singular_value": float(singular_values[-1]),
        "largest_singular_value": float(singular_values[0]),
        "jacobian_condition_number": float(singular_values[0] / singular_values[-1]),
        "singular_values_tail": singular_values[-6:].tolist(),
        "maximum_segment_transition_condition": float(max(transition_conditions)),
        "median_segment_transition_condition": float(np.median(transition_conditions)),
        "matching_residual_norm": float(np.linalg.norm(residual)),
        "closure_error": float(np.linalg.norm(nodes[-1] - state)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    event_bytes = args.event.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["dirty"]:
        raise SystemExit("clean source required")
    event = json.loads(event_bytes)
    best = event["best_evaluation"]
    parameters = RosslerParameters(
        a=manifest["fixed_a"], b=event["b_estimate"], c=manifest["fixed_c"]
    )
    state = np.asarray(best["initial_state"], dtype=float)
    total_duration = manifest["duration_multiplier"] * best["period_time"]
    phase = rossler_rhs(0.0, state, parameters)
    phase /= np.linalg.norm(phase)
    solver = SolverConfig(**manifest["solver"])
    audits = [
        audit(count, state, total_duration, parameters, phase, solver)
        for count in manifest["segment_counts"]
    ]
    baseline = audits[0]["smallest_singular_value"]
    final = audits[-1]
    acceptance = manifest["acceptance"]
    output = {
        "schema": "butterfly.multiple-shooting-conditioning-audit.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "parameters": {"a": parameters.a, "b": parameters.b, "c": parameters.c},
        "total_duration": total_duration,
        "audits": audits,
        "baseline_smallest_singular_value": baseline,
        "final_smallest_singular_value": final["smallest_singular_value"],
        "singular_value_reduction_factor": baseline / final["smallest_singular_value"],
    }
    output["passed"] = bool(
        final["smallest_singular_value"]
        <= acceptance["max_final_smallest_singular_value"]
        and final["matching_residual_norm"] <= acceptance["max_matching_residual"]
        and output["singular_value_reduction_factor"]
        >= acceptance["minimum_singular_value_reduction_factor"]
    )
    atomic_write(args.output, canonical_json(output))
    print(json.dumps(output, sort_keys=True))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
