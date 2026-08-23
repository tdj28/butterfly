#!/usr/bin/env python3
"""Tight-solver segmented identity audit of the event-relative period-3072 child."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from multiple_shooting_core import correct_fixed_parameter
from qualify_jones_period24_segmented_endpoint import cyclic_node_identity


SCHEMA = "butterfly.jones-period3072-segmented-identity-manifest.v1"


def phase_invariant_half_identity(nodes: np.ndarray) -> dict:
    """Minimize RMS mismatch between the two orbit halves over cyclic phase."""

    nodes = np.asarray(nodes, dtype=float)
    if nodes.ndim != 2 or nodes.shape[1] != 3 or len(nodes) % 2:
        raise ValueError("nodes must have even shape (n, 3)")
    midpoint = len(nodes) // 2
    return cyclic_node_identity(nodes[:midpoint], nodes[midpoint:])


def corrected_child(seed: dict, parameters, solver, manifest) -> dict:
    nodes = np.asarray(seed["nodes"], dtype=float)
    segment_count = len(nodes)
    phase_reference = nodes[0].copy()
    phase = rossler_rhs(0.0, phase_reference, parameters)
    phase /= np.linalg.norm(phase)
    initial = np.r_[nodes.ravel(), float(seed["period_time"])]
    corrected, status = correct_fixed_parameter(
        initial,
        parameters.a,
        segment_count=segment_count,
        a=None,
        c=parameters.c,
        phase=phase,
        phase_reference=phase_reference,
        solver=solver,
        tolerance=float(manifest["corrector"]["tolerance"]),
        max_evaluations=int(manifest["corrector"]["maximum_evaluations"]),
        continuation_parameter="a",
        fixed_b=parameters.b,
        sparse_jacobian=manifest.get("jacobian_storage") == "sparse_csr",
    )
    corrected_nodes = corrected[: 3 * segment_count].reshape(segment_count, 3)
    return {
        "nodes": corrected_nodes,
        "period_time": float(corrected[3 * segment_count]),
        "status": status,
        "half_identity": phase_invariant_half_identity(corrected_nodes),
        "base_identity": cyclic_node_identity(corrected_nodes, nodes),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported segmented identity manifest")
    source_bytes = args.source.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash mismatch")
    source_receipt = json.loads(source_bytes)
    if source_receipt.get("schema") != manifest["source_schema"]:
        raise SystemExit("source schema mismatch")
    if source_receipt.get("passed"):
        raise SystemExit("EXP-317 requires the preserved failed EXP-316 receipt")
    if source_receipt.get("local_criticality_classification") != "subcritical":
        raise SystemExit("source criticality pattern changed")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    fixed_b = float(source_receipt["fixed_b"])
    fixed_c = float(source_receipt["fixed_c"])
    if fixed_b != float(manifest["fixed_b"]) or fixed_c != float(manifest["fixed_c"]):
        raise SystemExit("fixed parameters changed")
    solvers = {
        name: SolverConfig(**profile) for name, profile in manifest["solvers"].items()
    }
    started = time.perf_counter()
    results = {}
    for name, solver in solvers.items():
        source_row = source_receipt["results"][name]
        target_a = float(source_row["target_a"])
        if target_a != float(manifest["target_a"][name]):
            raise SystemExit(f"{name} target changed")
        seed = source_row["child"]
        identity = seed["section_identity"]
        if not (
            identity["historical_integration_success"]
            and identity["barrio_integration_success"]
            and identity["historical_phase_count"]
            == int(manifest["source_identity"]["historical_phase_count"])
            and identity["barrio_phase_count"]
            == int(manifest["source_identity"]["barrio_phase_count"])
        ):
            raise SystemExit(f"{name} source section identity changed")
        parameters = RosslerParameters(a=target_a, b=fixed_b, c=fixed_c)
        row = corrected_child(seed, parameters, solver, manifest)
        row["target_a"] = target_a
        row["source_section_identity"] = identity
        row["nodes"] = row["nodes"].tolist()
        results[name] = row
        print(
            json.dumps(
                {
                    "solver": name,
                    "target_a": target_a,
                    "matching": row["status"]["matching_residual"],
                    "half_rms": row["half_identity"]["rms"],
                    "half_shift": row["half_identity"]["node_shift"],
                    "base_rms": row["base_identity"]["rms"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    names = list(solvers)
    cross_identity = cyclic_node_identity(
        np.asarray(results[names[0]]["nodes"], dtype=float),
        np.asarray(results[names[1]]["nodes"], dtype=float),
    )
    half_rms = [float(row["half_identity"]["rms"]) for row in results.values()]
    base_rms = [float(row["base_identity"]["rms"]) for row in results.values()]
    representation_error = max(*base_rms, float(cross_identity["rms"]))
    separation_ratio = min(half_rms) / max(representation_error, np.finfo(float).tiny)
    acceptance = manifest["acceptance"]
    statuses = [row["status"] for row in results.values()]
    period_difference = abs(
        float(results[names[0]]["period_time"])
        - float(results[names[1]]["period_time"])
    )
    passed = bool(
        all(status["success"] for status in statuses)
        and max(float(status["matching_residual"]) for status in statuses)
        <= float(acceptance["maximum_matching_residual"])
        and max(float(status["phase_residual"]) for status in statuses)
        <= float(acceptance["maximum_phase_residual"])
        and min(half_rms) >= float(acceptance["minimum_phase_invariant_half_rms"])
        and max(base_rms) <= float(acceptance["maximum_base_to_tight_node_rms"])
        and float(cross_identity["rms"])
        <= float(acceptance["maximum_cross_solver_node_rms"])
        and separation_ratio >= float(acceptance["minimum_separation_error_ratio"])
        and period_difference <= float(acceptance["maximum_period_difference"])
    )
    output = {
        "schema": manifest["output_schema"],
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_receipt_sha256": sha256_bytes(source_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "fixed_b": fixed_b,
        "fixed_c": fixed_c,
        "segment_count": int(source_receipt["child_segment_count"]),
        "results": results,
        "cross_solver_identity": cross_identity,
        "representation_error_rms": representation_error,
        "minimum_half_rms": min(half_rms),
        "separation_error_ratio": separation_ratio,
        "period_difference": period_difference,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    printed = {**output, "results": {}}
    for name, row in results.items():
        printed["results"][name] = {key: value for key, value in row.items() if key != "nodes"}
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
