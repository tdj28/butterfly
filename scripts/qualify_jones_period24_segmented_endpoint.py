#!/usr/bin/env python3
"""Independently qualify the separated Jones period-24 endpoint and parent."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import scipy

from audit_segmented_floquet_precision import block_and_product_floquet
from butterfly import (
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    flow_monodromy,
    legacy_rossler_section,
    rossler_rhs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from multiple_shooting_core import correct_fixed_parameter
from qualify_jones_period12_children import _section_count
from validate_multiple_shooting_switch import half_closure


SCHEMA = "butterfly.jones-period24-segmented-qualification-manifest.v1"


def cyclic_node_identity(left: np.ndarray, right: np.ndarray) -> dict:
    values = [
        float(np.sqrt(np.mean((left - np.roll(right, shift, axis=0)) ** 2)))
        for shift in range(len(left))
    ]
    best = int(np.argmin(values))
    return {"rms": values[best], "node_shift": best}


def corrected_family(seed, segment_count, parameters, solver, manifest):
    nodes = np.asarray(seed["nodes"], dtype=float)
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
    )
    corrected_nodes = corrected[: 3 * segment_count].reshape(segment_count, 3)
    duration = float(corrected[3 * segment_count])
    floquet = block_and_product_floquet(
        corrected_nodes,
        duration,
        parameters,
        solver,
        manifest["cyclic_shifts"][str(segment_count)],
    )
    cluster_index = floquet["block"]["dominant_nontrivial_cluster_index"]
    cluster = floquet["block"]["clusters"][cluster_index]
    direct = flow_monodromy(
        parameters, corrected_nodes[0], duration, config=solver
    )
    neutral_index = int(np.argmin(np.abs(direct.multipliers - 1.0)))
    return {
        "nodes": corrected_nodes,
        "period_time": duration,
        "status": status,
        "block_floquet": floquet,
        "dominant_modulus": float(cluster["floquet_modulus"]),
        "dominant_multiplier": cluster["floquet_multiplier"],
        "direct_closure_error": float(direct.closure_error),
        "direct_neutral_error": float(
            abs(direct.multipliers[neutral_index] - 1.0)
        ),
    }


def classify(modulus: float, margin: float) -> str:
    if modulus <= 1.0 - margin:
        return "stable"
    if modulus >= 1.0 + margin:
        return "unstable"
    return "neutral"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--continuation", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported Jones period-24 qualification manifest")
    continuation_bytes = args.continuation.read_bytes()
    event_bytes = args.event.read_bytes()
    if sha256_bytes(continuation_bytes) != manifest["continuation_receipt_sha256"]:
        raise SystemExit("continuation receipt hash mismatch")
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    continuation = json.loads(continuation_bytes)
    event = json.loads(event_bytes)
    if not continuation.get("passed") or not event.get("passed"):
        raise SystemExit("passed continuation and event receipts are required")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    fixed_b = float(manifest["fixed_b"])
    fixed_c = float(manifest["fixed_c"])
    child_seed = continuation["rows"][-1]
    target_a = float(child_seed["a"])
    parameters = RosslerParameters(a=target_a, b=fixed_b, c=fixed_c)
    parent_seed = {
        "nodes": event["nodes"],
        "period_time": event["period_time"],
    }
    solvers = {
        name: SolverConfig(**profile) for name, profile in manifest["solvers"].items()
    }
    started = time.perf_counter()
    results = {}
    for name, solver in solvers.items():
        parent = corrected_family(
            parent_seed, int(event["segment_count"]), parameters, solver, manifest
        )
        child = corrected_family(
            child_seed,
            int(continuation["segment_count"]),
            parameters,
            solver,
            manifest,
        )
        child_orbit = SimpleNamespace(
            initial_state=child["nodes"][0], period_time=child["period_time"]
        )
        historical = _section_count(
            parameters,
            child_orbit,
            legacy_rossler_section(parameters),
            int(manifest["identity"]["historical_phase_count"]),
            solver,
        )
        barrio = _section_count(
            parameters,
            child_orbit,
            barrio_rossler_section(parameters),
            int(manifest["identity"]["barrio_phase_count"]),
            solver,
        )
        for family in (parent, child):
            family["nodes"] = family["nodes"].tolist()
        child["half_period_closure"] = half_closure(
            np.asarray(child["nodes"])[0],
            child["period_time"],
            parameters,
            solver,
        )
        child["section_identity"] = {
            "historical_phase_count": historical[0],
            "historical_integration_success": historical[1],
            "barrio_phase_count": barrio[0],
            "barrio_integration_success": barrio[1],
        }
        results[name] = {"parent": parent, "child": child}

    reference = results[manifest["reference_solver"]]
    independent = results[manifest["independent_solver"]]
    identities = {
        family: cyclic_node_identity(
            np.asarray(reference[family]["nodes"], dtype=float),
            np.asarray(independent[family]["nodes"], dtype=float),
        )
        for family in ("parent", "child")
    }
    classifications = {
        solver_name: {
            family: classify(
                results[solver_name][family]["dominant_modulus"],
                float(manifest["acceptance"]["classification_margin"]),
            )
            for family in ("parent", "child")
        }
        for solver_name in results
    }
    child_moduli = [row["child"]["dominant_modulus"] for row in results.values()]
    child_relative_spread = (max(child_moduli) - min(child_moduli)) / max(child_moduli)
    acceptance = manifest["acceptance"]
    all_families = [family for row in results.values() for family in row.values()]
    identity_checks = [row["child"]["section_identity"] for row in results.values()]
    passed = bool(
        all(family["status"]["success"] for family in all_families)
        and max(family["status"]["matching_residual"] for family in all_families)
        <= float(acceptance["maximum_matching_residual"])
        and max(family["status"]["phase_residual"] for family in all_families)
        <= float(acceptance["maximum_phase_residual"])
        and identities["parent"]["rms"]
        <= float(acceptance["maximum_parent_solver_node_rms"])
        and identities["child"]["rms"]
        <= float(acceptance["maximum_child_solver_node_rms"])
        and abs(reference["parent"]["period_time"] - independent["parent"]["period_time"])
        <= float(acceptance["maximum_parent_period_difference"])
        and abs(reference["child"]["period_time"] - independent["child"]["period_time"])
        <= float(acceptance["maximum_child_period_difference"])
        and max(row["child"]["direct_closure_error"] for row in results.values())
        <= float(acceptance["maximum_child_closure_error"])
        and max(row["child"]["direct_neutral_error"] for row in results.values())
        <= float(acceptance["maximum_child_neutral_error"])
        and min(row["child"]["half_period_closure"] for row in results.values())
        >= float(acceptance["minimum_half_period_closure"])
        and child_relative_spread
        <= float(acceptance["maximum_child_multiplier_relative_spread"])
        and classifications[manifest["reference_solver"]]["parent"]
        == classifications[manifest["independent_solver"]]["parent"]
        != "neutral"
        and classifications[manifest["reference_solver"]]["child"]
        == classifications[manifest["independent_solver"]]["child"]
        != "neutral"
        and all(
            identity["historical_integration_success"]
            and identity["barrio_integration_success"]
            and identity["historical_phase_count"]
            == int(manifest["identity"]["historical_phase_count"])
            and identity["barrio_phase_count"]
            == int(manifest["identity"]["barrio_phase_count"])
            for identity in identity_checks
        )
    )
    if all(row["parent"] == "stable" and row["child"] == "unstable" for row in classifications.values()):
        local_classification = "subcritical"
    elif all(row["parent"] == "unstable" and row["child"] == "stable" for row in classifications.values()):
        local_classification = "supercritical"
    else:
        local_classification = "other-or-unresolved"
    output = {
        "schema": "butterfly.jones-period24-segmented-qualification-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "continuation_receipt_sha256": sha256_bytes(continuation_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "fixed_b": fixed_b,
        "fixed_c": fixed_c,
        "target_a": target_a,
        "event_a": float(event["corrected_a"]),
        "results": results,
        "solver_identities": identities,
        "classifications": classifications,
        "child_multiplier_relative_spread": child_relative_spread,
        "local_criticality_classification": local_classification,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    printed = {**output, "results": {}}
    for solver_name, row in results.items():
        printed["results"][solver_name] = {}
        for family, values in row.items():
            printed["results"][solver_name][family] = {
                key: value
                for key, value in values.items()
                if key not in {"nodes", "block_floquet"}
            }
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
