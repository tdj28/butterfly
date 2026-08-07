#!/usr/bin/env python3
"""Refine a signed segmented block-Floquet -1 event from a bound scan."""
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
    parser.add_argument("--scan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    expected_manifest_schema = "butterfly.segmented-block-flip-refinement-manifest.v1"
    if manifest.get("schema") != expected_manifest_schema:
        raise SystemExit("unsupported segmented refinement manifest")
    scan_bytes = args.scan.read_bytes()
    if sha256_bytes(scan_bytes) != manifest["scan_receipt_sha256"]:
        raise SystemExit("scan receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    scan = json.loads(scan_bytes)
    if scan.get("schema") != manifest["scan_schema"]:
        raise SystemExit("bound scan schema mismatch")
    if not scan.get("passed") or len(scan.get("qualifying_brackets", [])) != 1:
        raise SystemExit("bound scan must contain exactly one qualifying bracket")
    if scan["segment_count"] != manifest["segment_count"]:
        raise SystemExit("bound scan segment count mismatch")
    bracket = scan["qualifying_brackets"][0]
    rows_by_b = {float(row["b"]): row for row in scan["rows"]}
    upper = rows_by_b[float(bracket["upper_b"])]
    lower = rows_by_b[float(bracket["lower_b"])]
    segment_count = scan["segment_count"]
    a = float(manifest["fixed_a"])
    c = float(manifest["fixed_c"])
    solver = SolverConfig(**manifest["solver"])
    phase_reference = np.asarray(upper["nodes"][0], dtype=float)
    phase_parameters = RosslerParameters(a=a, b=upper["b"], c=c)
    phase = rossler_rhs(0.0, phase_reference, phase_parameters)
    phase /= np.linalg.norm(phase)

    def residual(row):
        return row["floquet"]["dominant_nontrivial_multiplier"]["real"] + 1.0

    upper["multiplier_residual"] = residual(upper)
    lower["multiplier_residual"] = residual(lower)
    if residual(upper) * residual(lower) > 0.0:
        raise SystemExit("bound endpoints do not retain a signed -1 bracket")

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
        multiplier = floquet["dominant_nontrivial_multiplier"]
        return {
            "b": b,
            "initial_state": nodes[0].tolist(),
            "period_time": duration,
            "status": status,
            "half_node_rms": float(
                np.sqrt(
                    np.mean(
                        (nodes[: segment_count // 2]
                        - nodes[segment_count // 2 :]) ** 2
                    )
                )
            ),
            "floquet": floquet,
            "multiplier_residual": multiplier["real"] + 1.0,
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
    candidates = [upper, lower, *evaluations]
    best = min(candidates, key=lambda row: abs(residual(row)))
    slope = (residual(upper) - residual(lower)) / (upper["b"] - lower["b"])
    estimated_uncertainty = abs(residual(best) / slope)
    prediction_error = best["b"] - scan["predicted_b"]
    acceptance = manifest["acceptance"]
    output = {
        "schema": "butterfly.segmented-block-flip-refinement.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "parent_period_label": manifest["parent_period_label"],
        "child_period_label": manifest["child_period_label"],
        "segment_count": segment_count,
        "predicted_b": scan["predicted_b"],
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
    multiplier = best["floquet"]["dominant_nontrivial_multiplier"]
    output["passed"] = bool(
        best["status"]["success"]
        and best["status"]["matching_residual"] <= acceptance["max_matching_residual"]
        and abs(best["multiplier_residual"]) <= acceptance["max_multiplier_residual"]
        and abs(multiplier["imag"]) <= acceptance["max_multiplier_imaginary_part"]
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
