#!/usr/bin/env python3
"""Refine a segmented flip using a precision-audited solver profile."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import scipy

from audit_segmented_floquet_precision import block_and_product_floquet
from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from multiple_shooting_core import correct_fixed_b


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--seed-scan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.precision-audited-flip-refinement-manifest.v1":
        raise SystemExit("unsupported precision-audited refinement manifest")
    audit_bytes = args.audit.read_bytes()
    scan_bytes = args.seed_scan.read_bytes()
    if sha256_bytes(audit_bytes) != manifest["audit_receipt_sha256"]:
        raise SystemExit("audit receipt hash mismatch")
    if sha256_bytes(scan_bytes) != manifest["seed_scan_receipt_sha256"]:
        raise SystemExit("seed scan receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    audit = json.loads(audit_bytes)
    scan = json.loads(scan_bytes)
    if audit.get("schema") != manifest["audit_schema"] or not audit.get("passed"):
        raise SystemExit("bound precision audit must have passed")
    if scan.get("schema") != manifest["seed_scan_schema"] or not scan.get("passed"):
        raise SystemExit("bound seed scan must have passed")
    if audit["segment_count"] != manifest["segment_count"]:
        raise SystemExit("audit segment count mismatch")
    audit_rows = {
        float(row["b"]): row
        for row in audit["rows"]
        if row["profile"] == manifest["source_profile"]
    }
    scan_rows = {float(row["b"]): row for row in scan["rows"]}

    def endpoint(b):
        row = {**audit_rows[float(b)]}
        seed = scan_rows[float(b)]
        row["nodes"] = seed["nodes"]
        row["period_time"] = seed["period_time"]
        return row

    lower = endpoint(manifest["lower_b"])
    upper = endpoint(manifest["upper_b"])
    segment_count = manifest["segment_count"]
    a = float(manifest["fixed_a"])
    c = float(manifest["fixed_c"])
    solver = SolverConfig(**manifest["solver"])
    phase_reference = np.asarray(upper["nodes"][0], dtype=float)
    phase_parameters = RosslerParameters(a=a, b=upper["b"], c=c)
    phase = rossler_rhs(0.0, phase_reference, phase_parameters)
    phase /= np.linalg.norm(phase)

    def residual(row):
        return row["floquet"]["block"]["dominant_nontrivial_multiplier"]["real"] + 1.0

    if residual(lower) * residual(upper) > 0.0:
        raise SystemExit("audited endpoints do not preserve a signed bracket")

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
        floquet = block_and_product_floquet(
            nodes,
            duration,
            parameters,
            solver,
            manifest["cyclic_shifts"],
        )
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
    prediction_error = best["b"] - manifest["predicted_b"]
    block_value = best["floquet"]["block"]["dominant_nontrivial_multiplier"]
    product_values = [
        row["dominant_nontrivial_multiplier"]["real"]
        for row in best["floquet"]["direct_products"]
    ]
    block_product_difference = abs(block_value["real"] - float(np.median(product_values)))
    cyclic_product_spread = max(product_values) - min(product_values)
    acceptance = manifest["acceptance"]
    output = {
        "schema": "butterfly.precision-audited-flip-refinement.v1",
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
        "predicted_b": manifest["predicted_b"],
        "b_estimate": best["b"],
        "prediction_error": prediction_error,
        "estimated_b_uncertainty": estimated_uncertainty,
        "retained_bracket": {
            "lower_b": lower["b"],
            "upper_b": upper["b"],
            "lower_residual": residual(lower),
            "upper_residual": residual(upper),
        },
        "block_product_difference": block_product_difference,
        "cyclic_product_spread": cyclic_product_spread,
        "best_evaluation": best,
        "evaluations": evaluations,
    }
    output["passed"] = bool(
        best["status"]["success"]
        and best["status"]["matching_residual"] <= acceptance["max_matching_residual"]
        and abs(residual(best)) <= acceptance["max_multiplier_residual"]
        and abs(block_value["imag"]) <= acceptance["max_multiplier_imaginary_part"]
        and best["half_node_rms"] >= acceptance["minimum_half_node_rms"]
        and estimated_uncertainty <= acceptance["max_estimated_b_uncertainty"]
        and abs(prediction_error) <= acceptance["max_prediction_error"]
        and block_product_difference <= acceptance["max_block_product_difference"]
        and cyclic_product_spread <= acceptance["max_cyclic_product_spread"]
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
