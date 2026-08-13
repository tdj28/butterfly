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
from switch_jones_period12_segmented_child import qualified_audit_bytes
from validate_multiple_shooting_switch import half_closure


SCHEMAS = {
    "butterfly.jones-period24-near-event-qualification-manifest.v1",
    "butterfly.jones-period48-near-event-qualification-manifest.v1",
    "butterfly.jones-period96-near-event-qualification-manifest.v1",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--switch", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--audit", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") not in SCHEMAS:
        raise SystemExit("unsupported near-event qualification manifest")
    switch_bytes = args.switch.read_bytes()
    event_bytes = args.event.read_bytes()
    if sha256_bytes(switch_bytes) != manifest["switch_receipt_sha256"]:
        raise SystemExit("switch receipt hash mismatch")
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    switch = json.loads(switch_bytes)
    event = json.loads(event_bytes)
    if not switch.get("passed"):
        raise SystemExit("a passed switch receipt is required")
    try:
        audit_bytes = qualified_audit_bytes(
            event, event_bytes, manifest, args.audit
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
    target = manifest["source_candidate"]
    selected = [
        row
        for row in switch["accepted_candidates"]
        if float(row["step_length"]) == float(target["step_length"])
        and int(row["direction"]) == int(target["direction"])
    ]
    if len(selected) != 1:
        raise SystemExit("source candidate is not uniquely selected")
    child_seed = selected[0]
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
            child_seed, int(switch["segment_count"]), parameters, solver, manifest
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
    families = [family for row in results.values() for family in row.values()]
    child_moduli = [row["child"]["dominant_modulus"] for row in results.values()]
    parent_moduli = [row["parent"]["dominant_modulus"] for row in results.values()]
    child_spread = (max(child_moduli) - min(child_moduli)) / max(child_moduli)
    parent_spread = (max(parent_moduli) - min(parent_moduli)) / max(parent_moduli)
    identities_rows = [row["child"]["section_identity"] for row in results.values()]
    passed = bool(
        criticality == manifest["expected_criticality"]
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
        "switch_receipt_sha256": sha256_bytes(switch_bytes),
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
