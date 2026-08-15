#!/usr/bin/env python3
"""Bisect solver-specific period-1536 real-minus-one event brackets."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from bracket_jones_period1536_solver_events import signed_residual
from butterfly import RosslerParameters, SolverConfig
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from qualify_jones_period24_segmented_endpoint import corrected_family


SCHEMA = "butterfly.jones-period1536-solver-event-refinement-manifest.v1"


def ordered_endpoints(bracket: dict) -> list[dict]:
    rows = [
        {"a": float(bracket["near_a"]), "residual": float(bracket["near_residual"])},
        {"a": float(bracket["new_a"]), "residual": float(bracket["new_residual"])},
    ]
    rows.sort(key=lambda row: row["a"])
    if rows[0]["residual"] * rows[1]["residual"] >= 0.0:
        raise ValueError("source endpoints do not retain a signed bracket")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--bracket-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported period-1536 solver-event refinement manifest")
    bracket_bytes = args.bracket_receipt.read_bytes()
    if sha256_bytes(bracket_bytes) != manifest["bracket_receipt_sha256"]:
        raise SystemExit("bracket receipt hash mismatch")
    receipt = json.loads(bracket_bytes)
    if receipt.get("schema") != manifest["bracket_schema"] or not receipt.get("passed"):
        raise SystemExit("a passed solver-event bracket receipt is required")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    fixed_b = float(manifest["fixed_b"])
    fixed_c = float(manifest["fixed_c"])
    segment_count = int(manifest["segment_count"])
    solvers = {
        name: SolverConfig(**profile) for name, profile in manifest["solvers"].items()
    }
    iterations = int(manifest["bisection_iterations"])
    started = time.perf_counter()
    results = {}
    for name, solver in solvers.items():
        endpoints = ordered_endpoints(receipt["brackets"][name])
        seed = receipt["results"][name]["evaluation"]
        evaluations = []
        for iteration in range(iterations):
            target_a = 0.5 * (endpoints[0]["a"] + endpoints[1]["a"])
            parameters = RosslerParameters(a=target_a, b=fixed_b, c=fixed_c)
            corrected = corrected_family(
                seed, segment_count, parameters, solver, manifest
            )
            residual = signed_residual(corrected)
            stored = {**corrected, "nodes": corrected["nodes"].tolist()}
            evaluations.append(
                {
                    "iteration": iteration,
                    "a": target_a,
                    "residual": residual,
                    "evaluation": stored,
                }
            )
            point = {"a": target_a, "residual": residual}
            if endpoints[0]["residual"] * residual < 0.0:
                endpoints[1] = point
            elif residual * endpoints[1]["residual"] < 0.0:
                endpoints[0] = point
            else:
                raise RuntimeError(f"{name} midpoint lost the signed bracket")
            seed = corrected
            print(
                json.dumps(
                    {
                        "solver": name,
                        "iteration": iteration,
                        "a": target_a,
                        "residual": residual,
                        "bracket": endpoints,
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
        results[name] = {
            "source_bracket": receipt["brackets"][name],
            "evaluations": evaluations,
            "refined_bracket": {
                "lower_a": endpoints[0]["a"],
                "lower_residual": endpoints[0]["residual"],
                "upper_a": endpoints[1]["a"],
                "upper_residual": endpoints[1]["residual"],
                "width": endpoints[1]["a"] - endpoints[0]["a"],
            },
        }

    acceptance = manifest["acceptance"]
    evaluations = [
        row["evaluation"]
        for result in results.values()
        for row in result["evaluations"]
    ]
    passed = bool(
        max(result["refined_bracket"]["width"] for result in results.values())
        <= float(acceptance["maximum_bracket_width"])
        and all(
            result["refined_bracket"]["lower_residual"]
            * result["refined_bracket"]["upper_residual"]
            < 0.0
            for result in results.values()
        )
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
        "bracket_receipt_sha256": sha256_bytes(bracket_bytes),
        "event_receipt_sha256": receipt["event_receipt_sha256"],
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "fixed_b": fixed_b,
        "fixed_c": fixed_c,
        "segment_count": segment_count,
        "bisection_iterations": iterations,
        "results": results,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    printed = {key: value for key, value in output.items() if key != "results"}
    printed["refined_brackets"] = {
        name: result["refined_bracket"] for name, result in results.items()
    }
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
