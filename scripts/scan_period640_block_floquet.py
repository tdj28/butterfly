#!/usr/bin/env python3
"""Continue a segmented period-640 cycle across its predicted flip."""
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
from validate_multiple_shooting_switch import half_closure


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--prediction", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.period640-block-floquet-scan-manifest.v1":
        raise SystemExit("unsupported period-640 scan manifest")
    candidate_bytes = args.candidate.read_bytes()
    prediction_bytes = args.prediction.read_bytes()
    if sha256_bytes(candidate_bytes) != manifest["candidate_receipt_sha256"]:
        raise SystemExit("candidate receipt hash mismatch")
    if sha256_bytes(prediction_bytes) != manifest["prediction_receipt_sha256"]:
        raise SystemExit("prediction receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    candidate = json.loads(candidate_bytes)
    prediction = json.loads(prediction_bytes)
    predicted_b = float(prediction["prospective_prediction"]["next_b"])
    if abs(predicted_b - manifest["predicted_b"]) > 1e-15:
        raise SystemExit("manifest prediction does not match bound receipt")
    seed = next(
        row
        for row in candidate["corrected_candidates"]
        if row["direction"] == manifest["source_direction"]
    )
    nodes = np.asarray(seed["nodes"], dtype=float)
    segment_count = len(nodes)
    if segment_count != manifest["segment_count"]:
        raise SystemExit("candidate segment count does not match manifest")
    variables = np.r_[nodes.ravel(), seed["period_time"]]
    a = float(manifest["fixed_a"])
    c = float(manifest["fixed_c"])
    solver = SolverConfig(**manifest["solver"])
    source_parameters = RosslerParameters(a=a, b=float(candidate["target_b"]), c=c)
    phase_reference = nodes[0].copy()
    phase = rossler_rhs(0.0, phase_reference, source_parameters)
    phase /= np.linalg.norm(phase)
    rows = []
    for b in manifest["b_values"]:
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
        row = {"b": b, "status": status}
        if status["success"]:
            nodes = corrected[: 3 * segment_count].reshape(segment_count, 3)
            duration = float(corrected[3 * segment_count])
            parameters = RosslerParameters(a=a, b=b, c=c)
            floquet = block_floquet(nodes, duration, parameters, solver)
            row.update(
                {
                    "period_time": duration,
                    "half_period_closure": half_closure(nodes[0], duration, parameters, solver),
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
            )
            variables = corrected
        rows.append(row)
    brackets = []
    for left, right in zip(rows[:-1], rows[1:]):
        if not left["status"]["success"] or not right["status"]["success"]:
            continue
        left_multiplier = left["floquet"]["dominant_nontrivial_multiplier"]
        right_multiplier = right["floquet"]["dominant_nontrivial_multiplier"]
        left_residual = left_multiplier["real"] + 1.0
        right_residual = right_multiplier["real"] + 1.0
        if left_residual * right_residual <= 0.0:
            brackets.append(
                {
                    "upper_b": left["b"],
                    "lower_b": right["b"],
                    "width": abs(left["b"] - right["b"]),
                    "midpoint": 0.5 * (left["b"] + right["b"]),
                    "prediction_error": 0.5 * (left["b"] + right["b"]) - predicted_b,
                    "upper_multiplier": left_multiplier,
                    "lower_multiplier": right_multiplier,
                }
            )
    acceptance = manifest["acceptance"]
    qualifying_brackets = [
        bracket
        for bracket in brackets
        if bracket["width"] <= acceptance["max_bracket_width"]
        and abs(bracket["prediction_error"]) <= acceptance["max_prediction_error"]
        and abs(bracket["upper_multiplier"]["imag"])
        <= acceptance["max_multiplier_imaginary_part"]
        and abs(bracket["lower_multiplier"]["imag"])
        <= acceptance["max_multiplier_imaginary_part"]
    ]
    output = {
        "schema": "butterfly.period640-block-floquet-scan.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "predicted_b": predicted_b,
        "segment_count": segment_count,
        "rows": rows,
        "flip_brackets": brackets,
        "qualifying_brackets": qualifying_brackets,
    }
    output["passed"] = bool(
        all(
            row["status"]["success"]
            and row["status"]["matching_residual"] <= acceptance["max_matching_residual"]
            and row["half_node_rms"] >= acceptance["minimum_half_node_rms"]
            for row in rows
        )
        and len(qualifying_brackets) >= 1
    )
    atomic_write(args.output, canonical_json(output))
    printed = {**output}
    printed["rows"] = [
        {key: value for key, value in row.items() if key != "nodes"} for row in rows
    ]
    print(json.dumps(printed, sort_keys=True))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
