#!/usr/bin/env python3
"""Resolve period-768 Floquet conditioning on one canonical phase representative."""

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
from qualify_jones_period24_segmented_endpoint import corrected_family, cyclic_node_identity
from validate_multiple_shooting_switch import half_closure


SCHEMA = "butterfly.jones-period768-canonical-floquet-audit-manifest.v1"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--sign-audit", type=Path, required=True)
    parser.add_argument("--qualification", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported canonical Floquet audit manifest")
    sign_bytes = args.sign_audit.read_bytes()
    qualification_bytes = args.qualification.read_bytes()
    if sha256_bytes(sign_bytes) != manifest["sign_audit_receipt_sha256"]:
        raise SystemExit("sign-audit receipt hash mismatch")
    if sha256_bytes(qualification_bytes) != manifest["qualification_receipt_sha256"]:
        raise SystemExit("qualification receipt hash mismatch")
    sign_audit = json.loads(sign_bytes)
    qualification = json.loads(qualification_bytes)
    if sign_audit.get("passed") or not qualification.get("passed"):
        raise SystemExit("a failed sign audit and passed qualification are required")
    expected_checks = {
        key: key != manifest["isolated_failed_check"]
        for key in sign_audit["checks"]
    }
    if sign_audit["checks"] != expected_checks:
        raise SystemExit("sign-audit failure is not isolated as declared")
    if sign_audit["switch_receipt_sha256"] != qualification["switch_receipt_sha256"]:
        raise SystemExit("source receipts do not bind the same switch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    source_solver = manifest["canonical_source_solver"]
    source_sign = str(int(manifest["canonical_source_sign"]))
    source_row = sign_audit["results"][source_solver][source_sign]
    seed = {
        "nodes": source_row["nodes"],
        "period_time": source_row["period_time"],
    }
    parameters = RosslerParameters(
        a=float(sign_audit["target_a"]),
        b=float(sign_audit["fixed_b"]),
        c=float(sign_audit["fixed_c"]),
    )
    started = time.perf_counter()
    results = {}
    for name, profile in manifest["solvers"].items():
        solver = SolverConfig(**profile)
        row = corrected_family(
            seed, int(manifest["segment_count"]), parameters, solver, manifest
        )
        nodes = np.asarray(row["nodes"], dtype=float)
        orbit = SimpleNamespace(initial_state=nodes[0], period_time=row["period_time"])
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
        row["half_period_closure"] = half_closure(
            nodes[0], row["period_time"], parameters, solver
        )
        row["section_identity"] = {
            "historical_phase_count": historical[0],
            "historical_integration_success": historical[1],
            "barrio_phase_count": barrio[0],
            "barrio_integration_success": barrio[1],
        }
        row["nodes"] = nodes.tolist()
        results[name] = row

    reference = results[manifest["reference_solver"]]
    independent = results[manifest["independent_solver"]]
    identity = cyclic_node_identity(
        np.asarray(reference["nodes"], dtype=float),
        np.asarray(independent["nodes"], dtype=float),
    )
    moduli = [row["dominant_modulus"] for row in results.values()]
    periods = [row["period_time"] for row in results.values()]
    acceptance = manifest["acceptance"]
    section_rows = [row["section_identity"] for row in results.values()]
    checks = {
        "source_failure_isolated": True,
        "source_sign_identity": bool(sign_audit["checks"]["sign_identity"]),
        "qualification": bool(qualification["passed"]),
        "all_corrections": all(row["status"]["success"] for row in results.values()),
        "matching": max(row["status"]["matching_residual"] for row in results.values())
        <= float(acceptance["maximum_matching_residual"]),
        "phase": max(row["status"]["phase_residual"] for row in results.values())
        <= float(acceptance["maximum_phase_residual"]),
        "solver_identity": identity["rms"]
        <= float(acceptance["maximum_solver_node_rms"]),
        "period_agreement": max(periods) - min(periods)
        <= float(acceptance["maximum_period_spread"]),
        "modulus_agreement": max(moduli) - min(moduli)
        <= float(acceptance["maximum_modulus_spread"]),
        "stable": max(moduli) <= float(acceptance["maximum_stable_modulus"]),
        "primitive": min(row["half_period_closure"] for row in results.values())
        >= float(acceptance["minimum_half_period_closure"]),
        "section_identity": all(
            row["historical_integration_success"]
            and row["barrio_integration_success"]
            and row["historical_phase_count"]
            == int(manifest["identity"]["historical_phase_count"])
            and row["barrio_phase_count"]
            == int(manifest["identity"]["barrio_phase_count"])
            for row in section_rows
        ),
    }
    output = {
        "schema": manifest["output_schema"],
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "sign_audit_receipt_sha256": sha256_bytes(sign_bytes),
        "qualification_receipt_sha256": sha256_bytes(qualification_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "target_a": parameters.a,
        "fixed_b": parameters.b,
        "fixed_c": parameters.c,
        "canonical_source_solver": source_solver,
        "canonical_source_sign": int(source_sign),
        "results": results,
        "solver_identity": identity,
        "period_spread": max(periods) - min(periods),
        "modulus_spread": max(moduli) - min(moduli),
        "checks": checks,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(checks.values()),
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    printed = {**output, "results": {}}
    for name, row in results.items():
        printed["results"][name] = {
            key: value for key, value in row.items() if key not in {"nodes", "block_floquet"}
        }
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
