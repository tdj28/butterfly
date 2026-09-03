#!/usr/bin/env python3
"""Diagnose Float64 parameter resolution at the candidate period-768 flip."""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np

from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period768-float64-resolution-manifest.v1"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--scan", type=Path, required=True)
    parser.add_argument("--precision", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported Float64 resolution manifest")
    scan_bytes = args.scan.read_bytes()
    precision_bytes = args.precision.read_bytes()
    if sha256_bytes(scan_bytes) != manifest["scan_receipt_sha256"]:
        raise SystemExit("scan receipt hash mismatch")
    if sha256_bytes(precision_bytes) != manifest["precision_receipt_sha256"]:
        raise SystemExit("precision receipt hash mismatch")
    scan = json.loads(scan_bytes)
    precision = json.loads(precision_bytes)
    if scan.get("schema") != manifest["scan_schema"] or not scan.get("passed"):
        raise SystemExit("bound scan is not the passed source")
    if precision.get("schema") != manifest["precision_schema"] or precision.get("passed"):
        raise SystemExit("bound precision audit is not the failed source")

    failed = sorted(key for key, value in precision["checks"].items() if not value)
    expected_failed = sorted(manifest["expected_precision_failed_checks"])
    if failed != expected_failed:
        raise SystemExit("precision failure set does not match the manifest")

    lower_index, upper_index = map(int, manifest["bracket_row_indices"])
    first = scan["rows"][lower_index]
    second = scan["rows"][upper_index]
    a_first = float(first["a"])
    a_second = float(second["a"])
    multiplier_first = float(first["tracked_multiplier"]["real"])
    multiplier_second = float(second["tracked_multiplier"]["real"])
    bracket_low, bracket_high = sorted((a_first, a_second))
    corrected_a = float(precision["corrected_a"])
    spacing = float(np.spacing(np.float64(corrected_a)))
    secant_slope = (multiplier_second - multiplier_first) / (a_second - a_first)
    estimated_increment = abs(secant_slope) * spacing

    reference = manifest["reference_solver"]
    independent = manifest["independent_solver"]
    reference_multiplier = float(
        precision["results"][reference]["flip_spectrum"]["direct_flip_median"]
    )
    independent_multiplier = float(
        precision["results"][independent]["flip_spectrum"]["direct_flip_median"]
    )
    solver_disagreement = abs(reference_multiplier - independent_multiplier)
    minimax_centering_residual = 0.5 * solver_disagreement
    bracket_width_ulps = (bracket_high - bracket_low) / spacing
    acceptance = manifest["acceptance"]
    checks = {
        "source_failures_match": True,
        "corrected_a_inside_bracket": bracket_low <= corrected_a <= bracket_high,
        "solver_disagreement_exceeds_two_gates": solver_disagreement
        >= float(acceptance["minimum_solver_disagreement"]),
        "minimax_centering_exceeds_gate": minimax_centering_residual
        > float(acceptance["maximum_flip_residual"]),
        "estimated_ulp_increment_exceeds_gate": estimated_increment
        >= float(acceptance["minimum_estimated_multiplier_increment_per_ulp"]),
        "bracket_resolves_many_ulps": bracket_width_ulps
        >= float(acceptance["minimum_bracket_width_ulps"]),
    }
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    output = {
        "schema": "butterfly.jones-period768-float64-resolution-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "scan_receipt_sha256": sha256_bytes(scan_bytes),
        "precision_receipt_sha256": sha256_bytes(precision_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "corrected_a": corrected_a,
        "a_spacing": spacing,
        "adjacent_a": {
            "lower": float(np.nextafter(corrected_a, -np.inf)),
            "upper": float(np.nextafter(corrected_a, np.inf)),
        },
        "bracket": {
            "a_low": bracket_low,
            "a_high": bracket_high,
            "width_ulps": bracket_width_ulps,
            "endpoint_multipliers": [multiplier_first, multiplier_second],
            "secant_slope": secant_slope,
        },
        "solver_multipliers": {
            reference: reference_multiplier,
            independent: independent_multiplier,
        },
        "solver_disagreement": solver_disagreement,
        "minimax_centering_residual": minimax_centering_residual,
        "estimated_multiplier_increment_per_ulp": estimated_increment,
        "checks": checks,
        "passed": all(checks.values()),
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    print(json.dumps(output, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
