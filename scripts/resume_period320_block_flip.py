#!/usr/bin/env python3
"""Resume a period-320 block-Floquet refinement from retained endpoints."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from multiple_shooting_core import correct_fixed_b
from qualify_period320_multiple_shooting import block_floquet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--prior", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.period320-block-flip-resume-manifest.v1":
        raise SystemExit("unsupported period-320 resume manifest")
    prior_bytes = args.prior.read_bytes()
    if sha256_bytes(prior_bytes) != manifest["prior_receipt_sha256"]:
        raise SystemExit("prior receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    prior = json.loads(prior_bytes)
    retained = prior["retained_bracket"]
    available = [prior["best_evaluation"], *prior["evaluations"]]

    def endpoint(target_b):
        return min(available, key=lambda row: abs(row["b"] - target_b))

    lower = endpoint(retained["lower_b"])
    upper = endpoint(retained["upper_b"])
    if abs(lower["b"] - retained["lower_b"]) > 1e-15:
        raise SystemExit("lower retained endpoint nodes are unavailable")
    if abs(upper["b"] - retained["upper_b"]) > 1e-15:
        raise SystemExit("upper retained endpoint nodes are unavailable")
    segment_count = len(upper["nodes"])
    a = float(manifest["fixed_a"])
    c = float(manifest["fixed_c"])
    solver = SolverConfig(**manifest["solver"])
    phase_reference = np.asarray(upper["nodes"][0], dtype=float)
    phase_parameters = RosslerParameters(a=a, b=upper["b"], c=c)
    phase = rossler_rhs(0.0, phase_reference, phase_parameters)
    phase /= np.linalg.norm(phase)

    def residual(row):
        return row["floquet"]["dominant_nontrivial_multiplier"]["real"] + 1.0

    def evaluate(b, seed):
        variables = np.r_[np.asarray(seed["nodes"]).ravel(), seed["period_time"]]
        corrected, status = correct_fixed_b(
            variables,
            b,
            segment_count=segment_count,
            a=a,
            c=c,
            phase=phase,
            phase_reference=phase_reference,
            solver=solver,
            tolerance=manifest["corrector"]["tolerance"],
            max_evaluations=manifest["corrector"]["max_evaluations"],
        )
        nodes = corrected[: 3 * segment_count].reshape(segment_count, 3)
        duration = float(corrected[3 * segment_count])
        parameters = RosslerParameters(a=a, b=b, c=c)
        floquet = block_floquet(nodes, duration, parameters, solver)
        return {
            "b": b,
            "initial_state": nodes[0].tolist(),
            "period_time": duration,
            "status": status,
            "half_node_rms": float(
                np.sqrt(
                    np.mean(
                        (nodes[: segment_count // 2] - nodes[segment_count // 2 :])
                        ** 2
                    )
                )
            ),
            "floquet": floquet,
            "multiplier_residual": floquet["dominant_nontrivial_multiplier"][
                "real"
            ]
            + 1.0,
            "nodes": nodes.tolist(),
        }

    evaluations = []
    for _ in range(manifest["refinement"]["maximum_iterations"]):
        upper_residual = residual(upper)
        lower_residual = residual(lower)
        trial_b = (
            upper["b"] * lower_residual - lower["b"] * upper_residual
        ) / (lower_residual - upper_residual)
        width = upper["b"] - lower["b"]
        margin = manifest["refinement"]["minimum_endpoint_fraction"] * width
        if not lower["b"] + margin <= trial_b <= upper["b"] - margin:
            trial_b = 0.5 * (lower["b"] + upper["b"])
        seed = upper if abs(trial_b - upper["b"]) <= abs(trial_b - lower["b"]) else lower
        current = evaluate(trial_b, seed)
        evaluations.append(current)
        if residual(upper) * residual(current) <= 0.0:
            lower = current
        else:
            upper = current
        if abs(residual(current)) <= manifest["refinement"]["multiplier_tolerance"]:
            break
    best = min([lower, upper, *evaluations], key=lambda row: abs(residual(row)))
    slope = (residual(upper) - residual(lower)) / (upper["b"] - lower["b"])
    estimated_uncertainty = abs(residual(best) / slope)
    prediction_error = best["b"] - prior["predicted_b"]
    multiplier = best["floquet"]["dominant_nontrivial_multiplier"]
    acceptance = manifest["acceptance"]
    output = {
        "schema": "butterfly.period320-block-flip-resume.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "parent_period_label": 320,
        "child_period_label": 640,
        "predicted_b": prior["predicted_b"],
        "b_estimate": best["b"],
        "prediction_error": prediction_error,
        "estimated_b_uncertainty": estimated_uncertainty,
        "retained_bracket": {
            "lower_b": lower["b"],
            "upper_b": upper["b"],
            "lower_residual": residual(lower),
            "upper_residual": residual(upper),
        },
        "best_evaluation": best,
        "evaluations": evaluations,
    }
    output["passed"] = bool(
        best["status"]["success"]
        and best["status"]["matching_residual"]
        <= acceptance["max_matching_residual"]
        and abs(residual(best)) <= acceptance["max_multiplier_residual"]
        and abs(multiplier["imag"])
        <= acceptance["max_multiplier_imaginary_part"]
        and best["half_node_rms"] >= acceptance["minimum_half_node_rms"]
        and estimated_uncertainty <= acceptance["max_estimated_b_uncertainty"]
        and abs(prediction_error) <= acceptance["max_prediction_error"]
    )
    atomic_write(args.output, canonical_json(output))
    printed = {**output, "evaluations": len(evaluations)}
    printed["best_evaluation"] = {
        key: value for key, value in best.items() if key != "nodes"
    }
    print(json.dumps(printed, sort_keys=True))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
