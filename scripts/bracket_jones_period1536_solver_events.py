#!/usr/bin/env python3
"""Bracket the period-1536 real-minus-one event under DOP853 and Radau."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from qualify_jones_period24_segmented_endpoint import corrected_family


SCHEMA = "butterfly.jones-period1536-solver-event-bracket-manifest.v1"


def signed_residual(parent: dict) -> float:
    multiplier = parent["dominant_multiplier"]
    if abs(float(multiplier["imag"])) > 1e-8:
        raise ValueError("dominant parent multiplier is not real")
    return float(multiplier["real"]) + 1.0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--near-receipt", type=Path, required=True)
    parser.add_argument("--far-receipt", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported period-1536 solver-event bracket manifest")
    near_bytes = args.near_receipt.read_bytes()
    far_bytes = args.far_receipt.read_bytes()
    if sha256_bytes(near_bytes) != manifest["near_receipt_sha256"]:
        raise SystemExit("near receipt hash mismatch")
    if sha256_bytes(far_bytes) != manifest["far_receipt_sha256"]:
        raise SystemExit("far receipt hash mismatch")
    near = json.loads(near_bytes)
    far = json.loads(far_bytes)
    if near.get("schema") != manifest["near_schema"]:
        raise SystemExit("near receipt schema mismatch")
    if far.get("schema") != manifest["far_schema"]:
        raise SystemExit("far receipt schema mismatch")
    if near.get("event_receipt_sha256") != far.get("event_receipt_sha256"):
        raise SystemExit("source receipts do not share an event binding")
    if near.get("fixed_b") != far.get("fixed_b") or near.get("fixed_c") != far.get("fixed_c"):
        raise SystemExit("source receipts do not share fixed parameters")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    near_a = float(near["target_a"])
    far_a = float(far["target_a"])
    if near_a != float(manifest["near_a"]) or far_a != float(manifest["far_a"]):
        raise SystemExit("source coordinates do not match the manifest")
    fixed_b = float(manifest["fixed_b"])
    fixed_c = float(manifest["fixed_c"])
    solvers = {
        name: SolverConfig(**profile) for name, profile in manifest["solvers"].items()
    }
    started = time.perf_counter()
    results = {}
    brackets = {}
    for name, solver in solvers.items():
        near_parent = near["results"][name]["parent"]
        far_parent = far["results"][name]["parent"]
        near_residual = signed_residual(near_parent)
        far_residual = signed_residual(far_parent)
        linear_root = far_a + (near_a - far_a) * (
            -far_residual / (near_residual - far_residual)
        )
        declared_root = float(manifest["linear_root_estimates"][name])
        if abs(linear_root - declared_root) > float(
            manifest["acceptance"]["maximum_linear_root_replay_error"]
        ):
            raise SystemExit(f"{name} linear root estimate does not replay")
        target_a = float(manifest["evaluation_a"][name])
        parameters = RosslerParameters(a=target_a, b=fixed_b, c=fixed_c)
        corrected = corrected_family(
            near_parent,
            int(manifest["segment_count"]),
            parameters,
            solver,
            manifest,
        )
        target_residual = signed_residual(corrected)
        if near_residual * target_residual >= 0.0:
            bracket = None
        else:
            bracket = {
                "lower_a": min(near_a, target_a),
                "upper_a": max(near_a, target_a),
                "width": abs(target_a - near_a),
                "near_a": near_a,
                "near_residual": near_residual,
                "new_a": target_a,
                "new_residual": target_residual,
            }
        corrected["nodes"] = corrected["nodes"].tolist()
        results[name] = {
            "near_residual": near_residual,
            "far_residual": far_residual,
            "linear_root_estimate": linear_root,
            "evaluation_a": target_a,
            "evaluation": corrected,
            "evaluation_residual": target_residual,
        }
        brackets[name] = bracket
        print(
            json.dumps(
                {
                    "solver": name,
                    "evaluation_a": target_a,
                    "evaluation_residual": target_residual,
                    "bracket": bracket,
                },
                sort_keys=True,
            ),
            flush=True,
        )

    acceptance = manifest["acceptance"]
    evaluations = [row["evaluation"] for row in results.values()]
    passed = bool(
        all(bracket is not None for bracket in brackets.values())
        and max(bracket["width"] for bracket in brackets.values())
        <= float(acceptance["maximum_bracket_width"])
        and min(abs(row["evaluation_residual"]) for row in results.values())
        >= float(acceptance["minimum_endpoint_multiplier_residual"])
        and all(row["status"]["success"] for row in evaluations)
        and max(float(row["status"]["matching_residual"]) for row in evaluations)
        <= float(acceptance["maximum_matching_residual"])
        and max(float(row["status"]["phase_residual"]) for row in evaluations)
        <= float(acceptance["maximum_phase_residual"])
        and max(float(row["direct_closure_error"]) for row in evaluations)
        <= float(acceptance["maximum_direct_closure_error"])
        and max(float(row["direct_neutral_error"]) for row in evaluations)
        <= float(acceptance["maximum_direct_neutral_error"])
    )
    output = {
        "schema": manifest["output_schema"],
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "near_receipt_sha256": sha256_bytes(near_bytes),
        "far_receipt_sha256": sha256_bytes(far_bytes),
        "event_receipt_sha256": near["event_receipt_sha256"],
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "fixed_b": fixed_b,
        "fixed_c": fixed_c,
        "segment_count": int(manifest["segment_count"]),
        "near_a": near_a,
        "far_a": far_a,
        "results": results,
        "brackets": brackets,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    printed = {key: value for key, value in output.items() if key != "results"}
    printed["result_summary"] = {
        name: {
            "linear_root_estimate": row["linear_root_estimate"],
            "evaluation_a": row["evaluation_a"],
            "evaluation_residual": row["evaluation_residual"],
        }
        for name, row in results.items()
    }
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
