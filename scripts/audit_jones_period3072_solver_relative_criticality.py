#!/usr/bin/env python3
"""Audit event-relative period-3072 criticality under DOP853 and Radau."""

from __future__ import annotations

import argparse
import json
import math
import platform
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig, barrio_rossler_section, legacy_rossler_section
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from qualify_jones_period12_children import _section_count
from qualify_jones_period24_segmented_endpoint import (
    classify,
    corrected_family,
    cyclic_node_identity,
)
from validate_multiple_shooting_switch import half_closure


SCHEMA = "butterfly.jones-period3072-solver-relative-criticality-manifest.v1"


def selected_child_seed(switch: dict, manifest: dict) -> dict:
    """Select the frozen child without consulting any multiplier."""

    target = manifest["source_candidate"]
    selected = [
        row
        for row in switch.get("accepted_candidates", [])
        if float(row["step_length"]) == float(target["step_length"])
        and int(row["direction"]) == int(target["direction"])
    ]
    if len(selected) != 1:
        raise ValueError("source candidate is not uniquely selected")
    return selected[0]


def solver_parent_seed(refinement: dict, solver_name: str, manifest: dict) -> dict:
    """Return the frozen positive-side parent evaluation for one solver."""

    specification = manifest["solver_targets"][solver_name]
    result = refinement["results"][solver_name]
    bracket = result["refined_bracket"]
    expected_upper = float(specification["event_upper_a"])
    if float(bracket["upper_a"]) != expected_upper:
        raise ValueError(f"{solver_name} upper event bound changed")
    if float(bracket["upper_residual"]) <= 0.0:
        raise ValueError(f"{solver_name} upper event bound is not on the positive side")
    evaluations = [
        row
        for row in result["evaluations"]
        if int(row["iteration"]) == int(specification["parent_seed_iteration"])
    ]
    if len(evaluations) != 1:
        raise ValueError(f"{solver_name} parent seed is not uniquely selected")
    selected = evaluations[0]
    if float(selected["a"]) != expected_upper:
        raise ValueError(f"{solver_name} parent seed is not the upper event bound")
    if float(selected["residual"]) <= 0.0:
        raise ValueError(f"{solver_name} parent seed residual is not positive")
    return selected["evaluation"]


def solver_target_a(refinement: dict, solver_name: str, manifest: dict) -> float:
    """Replay the preregistered target from the solver's upper event bound."""

    specification = manifest["solver_targets"][solver_name]
    upper = float(refinement["results"][solver_name]["refined_bracket"]["upper_a"])
    offset = float(specification["offset_from_upper_bound"])
    target = upper + offset
    expected = float(specification["target_a"])
    if target != expected:
        raise ValueError(f"{solver_name} event-relative target does not replay")
    if not target > upper:
        raise ValueError(f"{solver_name} target is not beyond the positive event bound")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--refinement", type=Path, required=True)
    parser.add_argument("--switch", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported solver-relative criticality manifest")
    refinement_bytes = args.refinement.read_bytes()
    switch_bytes = args.switch.read_bytes()
    if sha256_bytes(refinement_bytes) != manifest["refinement_receipt_sha256"]:
        raise SystemExit("refinement receipt hash mismatch")
    if sha256_bytes(switch_bytes) != manifest["switch_receipt_sha256"]:
        raise SystemExit("switch receipt hash mismatch")
    refinement = json.loads(refinement_bytes)
    switch = json.loads(switch_bytes)
    if (
        refinement.get("schema") != manifest["refinement_schema"]
        or not refinement.get("passed")
    ):
        raise SystemExit("a passed solver-event refinement is required")
    if switch.get("schema") != manifest["switch_schema"] or not switch.get("passed"):
        raise SystemExit("a passed period-3072 switch is required")
    if refinement.get("event_receipt_sha256") != switch.get("event_receipt_sha256"):
        raise SystemExit("refinement and switch do not share an event binding")
    if (
        float(refinement["fixed_b"]) != float(manifest["fixed_b"])
        or float(refinement["fixed_c"]) != float(manifest["fixed_c"])
        or float(switch["fixed_b"]) != float(manifest["fixed_b"])
        or float(switch["fixed_c"]) != float(manifest["fixed_c"])
    ):
        raise SystemExit("fixed parameters do not match the bound receipts")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    try:
        child_seed = selected_child_seed(switch, manifest)
        parent_seeds = {
            name: solver_parent_seed(refinement, name, manifest)
            for name in manifest["solvers"]
        }
        target_coordinates = {
            name: solver_target_a(refinement, name, manifest)
            for name in manifest["solvers"]
        }
    except ValueError as error:
        raise SystemExit(str(error)) from error

    fixed_b = float(manifest["fixed_b"])
    fixed_c = float(manifest["fixed_c"])
    solvers = {
        name: SolverConfig(**profile) for name, profile in manifest["solvers"].items()
    }
    started = time.perf_counter()
    results = {}
    for name, solver in solvers.items():
        parameters = RosslerParameters(
            a=target_coordinates[name], b=fixed_b, c=fixed_c
        )
        parent = corrected_family(
            parent_seeds[name],
            int(refinement["segment_count"]),
            parameters,
            solver,
            manifest,
        )
        child = corrected_family(
            child_seed,
            int(switch["segment_count"]),
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
        child["half_period_closure"] = half_closure(
            child["nodes"][0], child["period_time"], parameters, solver
        )
        child["section_identity"] = {
            "historical_phase_count": historical[0],
            "historical_integration_success": historical[1],
            "barrio_phase_count": barrio[0],
            "barrio_integration_success": barrio[1],
        }
        parent["nodes"] = parent["nodes"].tolist()
        child["nodes"] = child["nodes"].tolist()
        results[name] = {
            "event_upper_a": float(
                refinement["results"][name]["refined_bracket"]["upper_a"]
            ),
            "offset_from_upper_bound": float(
                manifest["solver_targets"][name]["offset_from_upper_bound"]
            ),
            "target_a": target_coordinates[name],
            "parent": parent,
            "child": child,
        }
        print(
            json.dumps(
                {
                    "solver": name,
                    "target_a": target_coordinates[name],
                    "parent_modulus": parent["dominant_modulus"],
                    "child_modulus": child["dominant_modulus"],
                    "parent_matching": parent["status"]["matching_residual"],
                    "child_matching": child["status"]["matching_residual"],
                    "half_period_closure": child["half_period_closure"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    names = list(solvers)
    left = results[names[0]]
    right = results[names[1]]
    identities = {
        family: cyclic_node_identity(
            np.asarray(left[family]["nodes"], dtype=float),
            np.asarray(right[family]["nodes"], dtype=float),
        )
        for family in ("parent", "child")
    }
    margin = float(manifest["acceptance"]["classification_margin"])
    classifications = {
        name: {
            family: classify(results[name][family]["dominant_modulus"], margin)
            for family in ("parent", "child")
        }
        for name in results
    }
    if all(
        row == {"parent": "stable", "child": "unstable"}
        for row in classifications.values()
    ):
        criticality = "subcritical"
    elif all(
        row == {"parent": "unstable", "child": "stable"}
        for row in classifications.values()
    ):
        criticality = "supercritical"
    else:
        criticality = "other-or-unresolved"
    families = [row[family] for row in results.values() for family in ("parent", "child")]
    parent_moduli = [row["parent"]["dominant_modulus"] for row in results.values()]
    child_moduli = [row["child"]["dominant_modulus"] for row in results.values()]
    parent_spread = (max(parent_moduli) - min(parent_moduli)) / max(parent_moduli)
    child_spread = (max(child_moduli) - min(child_moduli)) / max(child_moduli)
    identity_rows = [row["child"]["section_identity"] for row in results.values()]
    acceptance = manifest["acceptance"]
    passed = bool(
        criticality == manifest["expected_criticality"]
        and all(family["status"]["success"] for family in families)
        and max(float(family["status"]["matching_residual"]) for family in families)
        <= float(acceptance["maximum_matching_residual"])
        and max(float(family["status"]["phase_residual"]) for family in families)
        <= float(acceptance["maximum_phase_residual"])
        and max(float(family["direct_closure_error"]) for family in families)
        <= float(acceptance["maximum_direct_closure_error"])
        and max(float(family["direct_neutral_error"]) for family in families)
        <= float(acceptance["maximum_direct_neutral_error"])
        and identities["parent"]["rms"]
        <= float(acceptance["maximum_parent_solver_node_rms"])
        and identities["child"]["rms"]
        <= float(acceptance["maximum_child_solver_node_rms"])
        and parent_spread
        <= float(acceptance["maximum_parent_multiplier_relative_spread"])
        and child_spread
        <= float(acceptance["maximum_child_multiplier_relative_spread"])
        and min(float(row["child"]["half_period_closure"]) for row in results.values())
        >= float(acceptance["minimum_half_period_closure"])
        and all(
            identity["historical_integration_success"]
            and identity["barrio_integration_success"]
            and identity["historical_phase_count"]
            == int(manifest["identity"]["historical_phase_count"])
            and identity["barrio_phase_count"]
            == int(manifest["identity"]["barrio_phase_count"])
            for identity in identity_rows
        )
        and math.isclose(
            left["offset_from_upper_bound"],
            right["offset_from_upper_bound"],
            rel_tol=0.0,
            abs_tol=0.0,
        )
    )
    output = {
        "schema": manifest["output_schema"],
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "refinement_receipt_sha256": sha256_bytes(refinement_bytes),
        "switch_receipt_sha256": sha256_bytes(switch_bytes),
        "event_receipt_sha256": refinement["event_receipt_sha256"],
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "fixed_b": fixed_b,
        "fixed_c": fixed_c,
        "segment_count": int(refinement["segment_count"]),
        "child_segment_count": int(switch["segment_count"]),
        "results": results,
        "solver_identities": identities,
        "classifications": classifications,
        "parent_multiplier_relative_spread": parent_spread,
        "child_multiplier_relative_spread": child_spread,
        "local_criticality_classification": criticality,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    printed = {**output, "results": {}}
    for name, row in results.items():
        printed["results"][name] = {
            "event_upper_a": row["event_upper_a"],
            "offset_from_upper_bound": row["offset_from_upper_bound"],
            "target_a": row["target_a"],
            "parent": {
                key: value
                for key, value in row["parent"].items()
                if key not in {"nodes", "block_floquet"}
            },
            "child": {
                key: value
                for key, value in row["child"].items()
                if key not in {"nodes", "block_floquet"}
            },
        }
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
