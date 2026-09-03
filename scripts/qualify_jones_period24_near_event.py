#!/usr/bin/env python3
"""Qualify near-event Jones parent/child stability with two segmented solvers."""

from __future__ import annotations

import argparse
import json
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
from switch_jones_period12_segmented_child import normalized_event, qualified_audit_bytes
from validate_multiple_shooting_switch import half_closure


SCHEMAS = {
    "butterfly.jones-period24-near-event-qualification-manifest.v1",
    "butterfly.jones-period48-near-event-qualification-manifest.v1",
    "butterfly.jones-period96-near-event-qualification-manifest.v1",
    "butterfly.jones-period192-near-event-qualification-manifest.v1",
    "butterfly.jones-period384-near-event-qualification-manifest.v1",
    "butterfly.jones-period768-near-event-qualification-manifest.v1",
    "butterfly.jones-period1536-near-event-qualification-manifest.v1",
    "butterfly.jones-period3072-near-event-qualification-manifest.v1",
}


def selected_child_seed(
    source_receipt: dict, event: dict, manifest: dict, source_kind: str
) -> dict:
    """Select the prospectively declared child without using stability."""

    target = manifest["source_candidate"]
    if source_kind == "switch":
        if not source_receipt.get("passed"):
            raise ValueError("a passed switch receipt is required")
        selected = [
            row
            for row in source_receipt["accepted_candidates"]
            if float(row["step_length"]) == float(target["step_length"])
            and int(row["direction"]) == int(target["direction"])
        ]
        if len(selected) != 1:
            raise ValueError("source candidate is not uniquely selected")
        return selected[0]

    if source_receipt.get("schema") != manifest.get("continuation_schema"):
        raise ValueError("continuation schema mismatch")
    if not source_receipt.get("passed") and not manifest.get(
        "allow_failed_continuation_prefix", False
    ):
        raise ValueError("a failed continuation prefix is not authorized")
    if target.get("selection_rule") != "first_absolute_event_separation":
        raise ValueError("unsupported continuation source-selection rule")
    minimum_separation = float(target["minimum_absolute_event_separation"])
    rows = source_receipt.get("rows", [])
    selected_index = next(
        (
            index
            for index, row in enumerate(rows)
            if abs(float(row["a"]) - float(event["corrected_a"]))
            >= minimum_separation
        ),
        None,
    )
    if selected_index is None:
        raise ValueError("continuation has no row at the declared event separation")
    prefix = rows[: selected_index + 1]
    if not all(row["status"]["success"] for row in prefix):
        raise ValueError("continuation prefix contains an unsuccessful row")
    if max(float(row["status"]["matching_residual"]) for row in prefix) > float(
        target["maximum_prefix_matching_residual"]
    ):
        raise ValueError("continuation prefix exceeds the matching gate")
    if min(float(row["half_node_rms"]) for row in prefix) < float(
        target["minimum_prefix_half_node_rms"]
    ):
        raise ValueError("continuation prefix fails the primitive-separation gate")
    selected = rows[selected_index]
    if "expected_step_index" in target and int(selected["step_index"]) != int(
        target["expected_step_index"]
    ):
        raise ValueError("first-threshold row does not match the frozen step index")
    if "expected_a" in target and float(selected["a"]) != float(
        target["expected_a"]
    ):
        raise ValueError("first-threshold row does not match the frozen coordinate")
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--switch", type=Path)
    source_group.add_argument("--continuation", type=Path)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--audit", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") not in SCHEMAS:
        raise SystemExit("unsupported near-event qualification manifest")
    source_kind = "switch" if args.switch is not None else "continuation"
    source_path = args.switch if args.switch is not None else args.continuation
    source_bytes = source_path.read_bytes()
    event_bytes = args.event.read_bytes()
    source_hash_key = (
        "switch_receipt_sha256"
        if source_kind == "switch"
        else "continuation_receipt_sha256"
    )
    if sha256_bytes(source_bytes) != manifest[source_hash_key]:
        raise SystemExit(f"{source_kind} receipt hash mismatch")
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    source_receipt = json.loads(source_bytes)
    raw_event = json.loads(event_bytes)
    if raw_event.get("schema") != manifest.get("event_schema"):
        raise SystemExit("event schema mismatch")
    if (
        source_kind == "continuation"
        and source_receipt.get("event_receipt_sha256") != sha256_bytes(event_bytes)
    ):
        raise SystemExit("continuation is not bound to the selected event")
    try:
        audit_bytes = qualified_audit_bytes(
            raw_event, event_bytes, manifest, args.audit
        )
    except ValueError as error:
        raise SystemExit(str(error)) from error
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    event = normalized_event(raw_event, manifest)
    try:
        child_seed = selected_child_seed(
            source_receipt, event, manifest, source_kind
        )
    except ValueError as error:
        raise SystemExit(str(error)) from error
    parent_seed = {"nodes": event["nodes"], "period_time": event["period_time"]}
    fixed_b = float(manifest["fixed_b"])
    fixed_c = float(manifest["fixed_c"])
    target_a = float(child_seed["a"])
    parameters = RosslerParameters(a=target_a, b=fixed_b, c=fixed_c)
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
            int(source_receipt["segment_count"]),
            parameters,
            solver,
            manifest,
        )
        orbit = SimpleNamespace(
            initial_state=child["nodes"][0], period_time=child["period_time"]
        )
        historical = _section_count(
            parameters,
            orbit,
            legacy_rossler_section(parameters),
            int(manifest["identity"]["historical_phase_count"]),
            solver,
        )
        barrio = _section_count(
            parameters,
            orbit,
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
        results[name] = {"parent": parent, "child": child}
    reference_name = manifest["reference_solver"]
    independent_name = manifest["independent_solver"]
    reference = results[reference_name]
    independent = results[independent_name]
    identities = {
        family: cyclic_node_identity(
            np.asarray(reference[family]["nodes"], dtype=float),
            np.asarray(independent[family]["nodes"], dtype=float),
        )
        for family in ("parent", "child")
    }
    margin = float(manifest["acceptance"]["classification_margin"])
    classifications = {
        solver_name: {
            family: classify(row[family]["dominant_modulus"], margin)
            for family in ("parent", "child")
        }
        for solver_name, row in results.items()
    }
    if all(row == {"parent": "unstable", "child": "stable"} for row in classifications.values()):
        criticality = "supercritical"
    elif all(row == {"parent": "stable", "child": "unstable"} for row in classifications.values()):
        criticality = "subcritical"
    else:
        criticality = "other-or-unresolved"
    acceptance = manifest["acceptance"]
    expected_criticality = manifest["expected_criticality"]
    criticality_passed = (
        criticality != "other-or-unresolved"
        if expected_criticality == "resolved"
        else criticality == expected_criticality
    )
    families = [family for row in results.values() for family in row.values()]
    child_moduli = [row["child"]["dominant_modulus"] for row in results.values()]
    parent_moduli = [row["parent"]["dominant_modulus"] for row in results.values()]
    child_spread = (max(child_moduli) - min(child_moduli)) / max(child_moduli)
    parent_spread = (max(parent_moduli) - min(parent_moduli)) / max(parent_moduli)
    identities_rows = [row["child"]["section_identity"] for row in results.values()]
    passed = bool(
        criticality_passed
        and all(family["status"]["success"] for family in families)
        and max(family["status"]["matching_residual"] for family in families)
        <= float(acceptance["maximum_matching_residual"])
        and max(family["status"]["phase_residual"] for family in families)
        <= float(acceptance["maximum_phase_residual"])
        and identities["parent"]["rms"] <= float(acceptance["maximum_solver_node_rms"])
        and identities["child"]["rms"] <= float(acceptance["maximum_solver_node_rms"])
        and child_spread <= float(acceptance["maximum_multiplier_relative_spread"])
        and parent_spread <= float(acceptance["maximum_multiplier_relative_spread"])
        and min(row["child"]["half_period_closure"] for row in results.values())
        >= float(acceptance["minimum_half_period_closure"])
        and all(
            identity["historical_integration_success"]
            and identity["barrio_integration_success"]
            and identity["historical_phase_count"] == int(manifest["identity"]["historical_phase_count"])
            and identity["barrio_phase_count"] == int(manifest["identity"]["barrio_phase_count"])
            for identity in identities_rows
        )
    )
    output = {
        "schema": manifest.get(
            "output_schema",
            "butterfly.jones-period24-near-event-qualification-receipt.v1",
        ),
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_receipt_kind": source_kind,
        "switch_receipt_sha256": (
            sha256_bytes(source_bytes) if source_kind == "switch" else None
        ),
        "continuation_receipt_sha256": (
            sha256_bytes(source_bytes) if source_kind == "continuation" else None
        ),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "audit_receipt_sha256": (
            sha256_bytes(audit_bytes) if audit_bytes is not None else None
        ),
        "source": source,
        "environment": {"python": platform.python_version(), "platform": platform.platform(), "numpy": np.__version__, "scipy": scipy.__version__},
        "fixed_b": fixed_b,
        "fixed_c": fixed_c,
        "event_a": float(event["corrected_a"]),
        "target_a": target_a,
        "a_offset": target_a - float(event["corrected_a"]),
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
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    printed = {**output, "results": {}}
    for solver_name, row in results.items():
        printed["results"][solver_name] = {
            family: {key: value for key, value in values.items() if key not in {"nodes", "block_floquet"}}
            for family, values in row.items()
        }
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
