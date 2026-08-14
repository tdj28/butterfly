#!/usr/bin/env python3
"""Resolve the period-768 parent side at the EXP-289 child coordinate."""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, localcontext
from pathlib import Path

from audit_jones_period768_decimal_independent import rk_three_eighths
from audit_jones_period768_decimal_multiplier import (
    profile_spectrum,
    serializable_spectrum,
)
from audit_jones_period768_decimal_richardson import richardson
from audit_jones_period768_decimal_segments import dec, max_difference, rk4
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period768-decimal-parent-side-manifest.v1"
METHODS = {
    "classical_rk4": rk4,
    "rk4_three_eighths": rk_three_eighths,
}


def integrate_task(task: dict) -> dict:
    with localcontext() as context:
        context.prec = int(task["digits"])
        a, b, c = map(dec, (task["a"], task["b"], task["c"]))
        duration = dec(task["period_time"]) / Decimal(int(task["segment_count"]))
        node = [dec(value) for value in task["node"]]
        expected_node = [dec(value) for value in task["expected_node"]]
        identity = [
            Decimal(1), Decimal(0), Decimal(0),
            Decimal(0), Decimal(1), Decimal(0),
            Decimal(0), Decimal(0), Decimal(1),
        ]
        profiles = {}
        for method_name in task["methods"]:
            integrator = METHODS[method_name]
            integrations = [
                integrator(node + identity, duration, int(steps), a, b, c)
                for steps in task["steps"]
            ]
            profiles[method_name] = {
                "transitions": [
                    [str(value) for value in result[3:]] for result in integrations
                ],
                "fine_orbit_matching_residual": max_difference(
                    integrations[-1][:3], expected_node
                ),
            }
        return {"index": task["index"], "methods": profiles}


def source_is_qualified(receipt: dict, manifest: dict) -> bool:
    requirements = manifest["source_requirements"]
    solver_names = (
        manifest["qualification_solver"],
        manifest["independent_solver"],
    )
    classifications = receipt.get("classifications", {})
    results = receipt.get("results", {})
    child_identities = [results[name]["child"]["section_identity"] for name in solver_names]
    return bool(
        not receipt.get("passed")
        and all(
            classifications[name]["child"] == requirements["child_classification"]
            and classifications[name]["parent"] == requirements["parent_classification"]
            for name in solver_names
        )
        and float(receipt["child_multiplier_relative_spread"])
        <= float(requirements["maximum_child_multiplier_relative_spread"])
        and min(results[name]["child"]["half_period_closure"] for name in solver_names)
        >= float(requirements["minimum_child_half_period_closure"])
        and all(
            identity["historical_integration_success"]
            and identity["barrio_integration_success"]
            and int(identity["historical_phase_count"])
            == int(requirements["historical_phase_count"])
            and int(identity["barrio_phase_count"])
            == int(requirements["barrio_phase_count"])
            for identity in child_identities
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--qualification", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported Decimal parent-side manifest")
    qualification_bytes = args.qualification.read_bytes()
    if sha256_bytes(qualification_bytes) != manifest["qualification_receipt_sha256"]:
        raise SystemExit("qualification receipt hash mismatch")
    qualification = json.loads(qualification_bytes)
    if qualification.get("schema") != manifest["qualification_schema"]:
        raise SystemExit("qualification schema mismatch")
    if not source_is_qualified(qualification, manifest):
        raise SystemExit("source child instability and neutral-parent state are not qualified")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    solver_name = manifest["qualification_solver"]
    parent = qualification["results"][solver_name][manifest["family"]]
    nodes = parent["nodes"]
    count = len(nodes)
    tasks = []
    for index, node in enumerate(nodes):
        tasks.append(
            {
                "index": index,
                "digits": manifest["decimal_digits"],
                "steps": manifest["step_counts"],
                "methods": manifest["methods"],
                "a": qualification["target_a"],
                "b": qualification["fixed_b"],
                "c": qualification["fixed_c"],
                "period_time": parent["period_time"],
                "segment_count": count,
                "node": node,
                "expected_node": nodes[(index + 1) % count],
            }
        )

    started = time.perf_counter()
    workers = min(int(manifest["workers"]), os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        rows = list(executor.map(integrate_task, tasks, chunksize=1))
    rows.sort(key=lambda row: row["index"])

    with localcontext() as context:
        context.prec = int(manifest["decimal_digits"])
        method_results = {}
        for method_name in manifest["methods"]:
            spectra = []
            for profile_index in range(len(manifest["step_counts"])):
                transitions = [
                    [Decimal(value) for value in row["methods"][method_name]["transitions"][profile_index]]
                    for row in rows
                ]
                spectra.append(
                    profile_spectrum(transitions, manifest["cyclic_shifts"], context.prec)
                )
            coarse_flip, medium_flip, fine_flip = [row["flip_median"] for row in spectra]
            coarse_neutral, medium_neutral, fine_neutral = [
                row["neutral_median"] for row in spectra
            ]
            first_flip = richardson(coarse_flip, medium_flip, manifest["method_order"])
            second_flip = richardson(medium_flip, fine_flip, manifest["method_order"])
            first_neutral = richardson(
                coarse_neutral, medium_neutral, manifest["method_order"]
            )
            second_neutral = richardson(
                medium_neutral, fine_neutral, manifest["method_order"]
            )
            method_results[method_name] = {
                "profiles": [serializable_spectrum(row) for row in spectra],
                "raw_convergence_ratio": float(
                    abs((coarse_flip - medium_flip) / (medium_flip - fine_flip))
                ),
                "first_flip_decimal": str(first_flip),
                "first_flip": float(first_flip),
                "second_flip_decimal": str(second_flip),
                "second_flip": float(second_flip),
                "successive_flip_difference": float(abs(first_flip - second_flip)),
                "second_flip_residual": float(second_flip + Decimal(1)),
                "first_neutral_decimal": str(first_neutral),
                "first_neutral": float(first_neutral),
                "second_neutral_decimal": str(second_neutral),
                "second_neutral": float(second_neutral),
                "successive_neutral_difference": float(abs(first_neutral - second_neutral)),
                "second_neutral_residual": float(second_neutral - Decimal(1)),
                "fine_cyclic_spread": float(spectra[-1]["flip_cyclic_spread"]),
                "fine_characteristic_residual": float(
                    spectra[-1]["maximum_characteristic_residual"]
                ),
                "maximum_fine_orbit_matching_residual": max(
                    row["methods"][method_name]["fine_orbit_matching_residual"]
                    for row in rows
                ),
            }

    acceptance = manifest["acceptance"]
    values = list(method_results.values())
    cross_flip = abs(values[0]["second_flip"] - values[1]["second_flip"])
    cross_neutral = abs(values[0]["second_neutral"] - values[1]["second_neutral"])
    checks = {
        "raw_convergence": all(
            float(acceptance["minimum_raw_convergence_ratio"])
            <= row["raw_convergence_ratio"]
            <= float(acceptance["maximum_raw_convergence_ratio"])
            for row in values
        ),
        "richardson_flip_convergence": all(
            row["successive_flip_difference"]
            <= float(acceptance["maximum_successive_richardson_flip_difference"])
            for row in values
        ),
        "cross_tableau_flip": cross_flip
        <= float(acceptance["maximum_cross_tableau_flip_difference"]),
        "stable_side": all(
            float(acceptance["minimum_stable_side_flip_residual"])
            <= row["second_flip_residual"]
            <= float(acceptance["maximum_stable_side_flip_residual"])
            for row in values
        ),
        "richardson_neutral_convergence": all(
            row["successive_neutral_difference"]
            <= float(acceptance["maximum_successive_richardson_neutral_difference"])
            for row in values
        ),
        "cross_tableau_neutral": cross_neutral
        <= float(acceptance["maximum_cross_tableau_neutral_difference"]),
        "neutral": all(
            abs(row["second_neutral_residual"])
            <= float(acceptance["maximum_extrapolated_neutral_residual"])
            for row in values
        ),
        "cyclic": all(
            row["fine_cyclic_spread"]
            <= float(acceptance["maximum_fine_cyclic_spread"])
            for row in values
        ),
        "characteristic": all(
            row["fine_characteristic_residual"]
            <= float(acceptance["maximum_fine_characteristic_residual"])
            for row in values
        ),
        "orbit_matching": all(
            row["maximum_fine_orbit_matching_residual"]
            <= float(acceptance["maximum_fine_orbit_matching_residual"])
            for row in values
        ),
    }
    output = {
        "schema": "butterfly.jones-period768-decimal-parent-side-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "qualification_receipt_sha256": sha256_bytes(qualification_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "workers": workers,
        },
        "target_a": qualification["target_a"],
        "event_a": qualification["event_a"],
        "a_offset": qualification["a_offset"],
        "segment_count": count,
        "decimal_digits": manifest["decimal_digits"],
        "step_counts": manifest["step_counts"],
        "methods": method_results,
        "cross_tableau_flip_difference": cross_flip,
        "cross_tableau_neutral_difference": cross_neutral,
        "checks": checks,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(checks.values()),
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    print(json.dumps(output, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
