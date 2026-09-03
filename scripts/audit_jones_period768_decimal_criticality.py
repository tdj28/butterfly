#!/usr/bin/env python3
"""Resolve the seventh-birth parent side in 50-digit arithmetic."""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, localcontext
from pathlib import Path

from audit_jones_period768_decimal_parent_side import integrate_task
from audit_jones_period768_decimal_multiplier import (
    profile_spectrum,
    serializable_spectrum,
)
from audit_jones_period768_decimal_richardson import richardson
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period768-decimal-criticality-manifest.v1"


def source_is_qualified(qualification: dict, event: dict, manifest: dict) -> bool:
    """Require the preserved neutral-parent/stable-child source evidence."""

    requirements = manifest["source_requirements"]
    solver_names = manifest["qualification_solvers"]
    classifications = qualification.get("classifications", {})
    results = qualification.get("results", {})
    identities = [results[name]["child"]["section_identity"] for name in solver_names]
    return bool(
        not qualification.get("passed")
        and event.get("passed")
        and qualification.get("event_receipt_sha256")
        == manifest["event_receipt_sha256"]
        and all(
            classifications[name]["parent"]
            == requirements["parent_classification"]
            and classifications[name]["child"]
            == requirements["child_classification"]
            for name in solver_names
        )
        and float(qualification["child_multiplier_relative_spread"])
        <= float(requirements["maximum_child_multiplier_relative_spread"])
        and min(
            float(results[name]["child"]["half_period_closure"])
            for name in solver_names
        )
        >= float(requirements["minimum_child_half_period_closure"])
        and all(
            identity["historical_integration_success"]
            and identity["barrio_integration_success"]
            and int(identity["historical_phase_count"])
            == int(requirements["historical_phase_count"])
            and int(identity["barrio_phase_count"])
            == int(requirements["barrio_phase_count"])
            for identity in identities
        )
    )


def resolved_classification(residuals: list[float], minimum_signal: float) -> str:
    """Classify the real flip root only when both tableaux clear the margin."""

    if all(value >= minimum_signal for value in residuals):
        return "stable"
    if all(value <= -minimum_signal for value in residuals):
        return "unstable"
    return "neutral"


def criticality(parent: str, child: str) -> str:
    if parent == "unstable" and child == "stable":
        return "supercritical"
    if parent == "stable" and child == "unstable":
        return "subcritical"
    return "other-or-unresolved"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--qualification", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    qualification_bytes = args.qualification.read_bytes()
    event_bytes = args.event.read_bytes()
    manifest = json.loads(manifest_bytes)
    qualification = json.loads(qualification_bytes)
    event = json.loads(event_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported Decimal criticality manifest")
    if sha256_bytes(qualification_bytes) != manifest["qualification_receipt_sha256"]:
        raise SystemExit("qualification receipt hash mismatch")
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    if qualification.get("schema") != manifest["qualification_schema"]:
        raise SystemExit("qualification schema mismatch")
    if event.get("schema") != manifest["event_schema"]:
        raise SystemExit("event schema mismatch")
    if not source_is_qualified(qualification, event, manifest):
        raise SystemExit("source neutral-parent/stable-child state is not qualified")

    target_a = Decimal(str(qualification["target_a"]))
    extrapolated_event_a = Decimal(event["extrapolated_a_decimal"])
    event_separation = target_a - extrapolated_event_a
    if event_separation < Decimal(str(manifest["minimum_event_separation"])):
        raise SystemExit("qualified child is not above the extrapolated event")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    parent = qualification["results"][manifest["parent_seed_solver"]]["parent"]
    nodes = parent["nodes"]
    count = len(nodes)
    tasks = [
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
        for index, node in enumerate(nodes)
    ]

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
                    [
                        Decimal(value)
                        for value in row["methods"][method_name]["transitions"][
                            profile_index
                        ]
                    ]
                    for row in rows
                ]
                spectra.append(
                    profile_spectrum(
                        transitions, manifest["cyclic_shifts"], context.prec
                    )
                )
            coarse_flip, medium_flip, fine_flip = [
                spectrum["flip_median"] for spectrum in spectra
            ]
            coarse_neutral, medium_neutral, fine_neutral = [
                spectrum["neutral_median"] for spectrum in spectra
            ]
            first_flip = richardson(
                coarse_flip, medium_flip, manifest["method_order"]
            )
            second_flip = richardson(
                medium_flip, fine_flip, manifest["method_order"]
            )
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
                "successive_neutral_difference": float(
                    abs(first_neutral - second_neutral)
                ),
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
    uncertainty = max(
        cross_flip, *(row["successive_flip_difference"] for row in values)
    )
    minimum_signal = float(acceptance["minimum_absolute_flip_residual"])
    parent_classification = resolved_classification(
        [row["second_flip_residual"] for row in values], minimum_signal
    )
    child_classification = manifest["source_requirements"]["child_classification"]
    local_criticality = criticality(parent_classification, child_classification)
    signal = min(abs(row["second_flip_residual"]) for row in values)
    signal_to_error = signal / uncertainty if uncertainty > 0.0 else float("inf")
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
        "resolved_parent": parent_classification in {"stable", "unstable"},
        "signal_to_error": signal_to_error
        >= float(acceptance["minimum_signal_to_error_ratio"]),
        "resolved_criticality": local_criticality
        in set(acceptance["accepted_criticality"]),
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
        "schema": manifest["output_schema"],
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "qualification_receipt_sha256": sha256_bytes(qualification_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "workers": workers,
        },
        "target_a": qualification["target_a"],
        "extrapolated_event_a_decimal": str(extrapolated_event_a),
        "event_separation_decimal": str(event_separation),
        "segment_count": count,
        "decimal_digits": manifest["decimal_digits"],
        "step_counts": manifest["step_counts"],
        "methods": method_results,
        "cross_tableau_flip_difference": cross_flip,
        "cross_tableau_neutral_difference": cross_neutral,
        "empirical_multiplier_uncertainty": uncertainty,
        "minimum_flip_signal": signal,
        "signal_to_error_ratio": signal_to_error,
        "parent_classification": parent_classification,
        "child_classification": child_classification,
        "local_criticality_classification": local_criticality,
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
