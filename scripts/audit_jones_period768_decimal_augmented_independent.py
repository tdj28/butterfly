#!/usr/bin/env python3
"""Independently refine the Decimal augmented flip with RK4 3/8."""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, localcontext
from pathlib import Path

from audit_jones_period768_decimal_richardson import richardson
from correct_jones_period768_decimal_parent import state_rhs
from refine_jones_period768_decimal_augmented import (
    convergence_ratio,
    correct_profile,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period768-decimal-augmented-independent-manifest.v1"


def flattened_difference(left, right):
    return [
        value - reference
        for row, reference_row in zip(left, right)
        for value, reference in zip(row, reference_row)
    ]


def rms(values):
    return (sum(value * value for value in values) / Decimal(len(values))).sqrt()


def tangent_line_metrics(reference, candidate):
    base_dot = sum(a * b for a, b in zip(reference[0], candidate[0]))
    sign = Decimal(1) if base_dot >= 0 else Decimal(-1)
    aligned = [[sign * value for value in row] for row in candidate]
    base_difference = max(
        abs(value - source)
        for value, source in zip(aligned[0], reference[0])
    )
    numerator = sum(
        value * source
        for row, source_row in zip(aligned, reference)
        for value, source in zip(row, source_row)
    )
    left_norm = sum(value * value for row in aligned for value in row).sqrt()
    right_norm = sum(value * value for row in reference for value in row).sqrt()
    global_cosine = numerator / (left_norm * right_norm)
    pointwise = []
    for row, source_row in zip(aligned, reference):
        dot = sum(value * source for value, source in zip(row, source_row))
        row_norm = sum(value * value for value in row).sqrt()
        source_norm = sum(value * value for value in source_row).sqrt()
        pointwise.append(abs(dot / (row_norm * source_norm)))
    ordered = sorted(pointwise)
    middle = len(ordered) // 2
    median = (ordered[middle - 1] + ordered[middle]) / Decimal(2)
    threshold = Decimal("0.999")
    fraction = Decimal(sum(value >= threshold for value in pointwise)) / Decimal(
        len(pointwise)
    )
    maximum_difference = max(
        abs(value - source)
        for row, source_row in zip(aligned, reference)
        for value, source in zip(row, source_row)
    )
    return {
        "alignment_sign": int(sign),
        "base_maximum_difference_decimal": str(base_difference),
        "base_maximum_difference": float(base_difference),
        "global_cosine_decimal": str(global_cosine),
        "global_cosine": float(global_cosine),
        "median_absolute_pointwise_cosine_decimal": str(median),
        "median_absolute_pointwise_cosine": float(median),
        "fraction_pointwise_cosine_at_least_0_999_decimal": str(fraction),
        "fraction_pointwise_cosine_at_least_0_999": float(fraction),
        "maximum_aligned_field_difference_decimal": str(maximum_difference),
        "maximum_aligned_field_difference": float(maximum_difference),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--classical", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported independent augmented manifest")
    classical_bytes = args.classical.read_bytes()
    if sha256_bytes(classical_bytes) != manifest["classical_receipt_sha256"]:
        raise SystemExit("classical receipt hash mismatch")
    classical = json.loads(classical_bytes)
    if classical.get("schema") != manifest["classical_schema"] or classical.get("passed"):
        raise SystemExit("bound classical result is not the preserved failed source")
    if [name for name, passed in classical["checks"].items() if not passed] != [
        "source_neighborhood"
    ]:
        raise SystemExit("classical source did not fail only source_neighborhood")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    started = time.perf_counter()
    with localcontext() as context:
        context.prec = int(manifest["decimal_digits"])
        classical_nodes = [
            [Decimal(value) for value in row] for row in classical["nodes_decimal"]
        ]
        classical_tangents = [
            [Decimal(value) for value in row]
            for row in classical["tangent_nodes_decimal"]
        ]
        finest_classical = classical["profiles"][-1]
        classical_period = Decimal(finest_classical["period_time_decimal"])
        classical_a = Decimal(finest_classical["a_decimal"])
        b = Decimal(str(manifest["fixed_b"]))
        c = Decimal(str(manifest["fixed_c"]))
        phase = state_rhs(classical_nodes[0], classical_a, b, c)
        phase_norm = sum(value * value for value in phase).sqrt()
        phase = [value / phase_norm for value in phase]

        nodes = [row.copy() for row in classical_nodes]
        tangents = [row.copy() for row in classical_tangents]
        period_time = classical_period
        parameter = classical_a
        profiles = []
        workers = min(int(manifest["workers"]), os.cpu_count() or 1)
        with ProcessPoolExecutor(max_workers=workers) as executor:
            for steps in manifest["step_counts"]:
                corrected = correct_profile(
                    executor,
                    nodes,
                    tangents,
                    period_time,
                    parameter,
                    classical_nodes,
                    classical_tangents,
                    classical_period,
                    phase,
                    b,
                    c,
                    manifest,
                    int(steps),
                )
                profiles.append(
                    {key: value for key, value in corrected.items() if key not in {"nodes", "tangents", "period", "parameter"}}
                )
                nodes = corrected["nodes"]
                tangents = corrected["tangents"]
                period_time = corrected["period"]
                parameter = corrected["parameter"]

        a_values = [Decimal(row["a_decimal"]) for row in profiles]
        period_values = [Decimal(row["period_time_decimal"]) for row in profiles]
        a_ratio = convergence_ratio(a_values)
        period_ratio = convergence_ratio(period_values)
        extrapolated_a = richardson(a_values[1], a_values[2], manifest["method_order"])
        extrapolated_period = richardson(
            period_values[1], period_values[2], manifest["method_order"]
        )
        classical_extrapolated_a = Decimal(classical["extrapolated_a_decimal"])
        classical_extrapolated_period = Decimal(
            classical["extrapolated_period_decimal"]
        )
        node_differences = flattened_difference(nodes, classical_nodes)
        node_maximum = max(map(abs, node_differences))
        node_rms = rms(node_differences)
        tangent_metrics = tangent_line_metrics(classical_tangents, tangents)

    acceptance = manifest["acceptance"]
    lower_a, upper_a = map(Decimal, map(str, manifest["a_bounds"]))
    finest = profiles[-1]
    checks = {
        "correction": all(row["converged"] for row in profiles),
        "a_convergence": float(acceptance["minimum_convergence_ratio"])
        <= float(a_ratio)
        <= float(acceptance["maximum_convergence_ratio"]),
        "period_convergence": float(acceptance["minimum_convergence_ratio"])
        <= float(period_ratio)
        <= float(acceptance["maximum_convergence_ratio"]),
        "a_bounds": (
            lower_a <= Decimal(finest["a_decimal"]) <= upper_a
            and lower_a <= extrapolated_a <= upper_a
        ),
        "cross_a": (
            abs(Decimal(finest["a_decimal"]) - Decimal(classical["profiles"][-1]["a_decimal"]))
            <= Decimal(str(acceptance["maximum_cross_tableau_finest_a_difference"]))
            and abs(extrapolated_a - classical_extrapolated_a)
            <= Decimal(str(acceptance["maximum_cross_tableau_extrapolated_a_difference"]))
        ),
        "cross_period": abs(extrapolated_period - classical_extrapolated_period)
        <= Decimal(str(acceptance["maximum_cross_tableau_extrapolated_period_difference"])),
        "node_identity": (
            node_maximum <= Decimal(str(acceptance["maximum_node_difference"]))
            and node_rms <= Decimal(str(acceptance["maximum_node_rms_difference"]))
        ),
        "base_tangent": tangent_metrics["base_maximum_difference"]
        <= float(acceptance["maximum_base_tangent_difference"]),
        "tangent_line": (
            tangent_metrics["global_cosine"]
            >= float(acceptance["minimum_global_tangent_cosine"])
            and tangent_metrics["median_absolute_pointwise_cosine"]
            >= float(acceptance["minimum_median_pointwise_tangent_cosine"])
            and tangent_metrics["fraction_pointwise_cosine_at_least_0_999"]
            >= float(acceptance["minimum_fraction_pointwise_tangent_cosine"])
        ),
        "primitive_half_separation": finest["half_node_rms_separation"]
        >= float(acceptance["minimum_half_node_rms_separation"]),
    }
    output = {
        "schema": "butterfly.jones-period768-decimal-augmented-independent-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "classical_receipt_sha256": sha256_bytes(classical_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "workers": workers,
        },
        "decimal_digits": manifest["decimal_digits"],
        "method": manifest["method"],
        "method_order": manifest["method_order"],
        "step_counts": manifest["step_counts"],
        "profiles": profiles,
        "a_convergence_ratio_decimal": str(a_ratio),
        "a_convergence_ratio": float(a_ratio),
        "period_convergence_ratio_decimal": str(period_ratio),
        "period_convergence_ratio": float(period_ratio),
        "extrapolated_a_decimal": str(extrapolated_a),
        "extrapolated_a": float(extrapolated_a),
        "cross_tableau_extrapolated_a_difference": float(
            abs(extrapolated_a - classical_extrapolated_a)
        ),
        "extrapolated_period_decimal": str(extrapolated_period),
        "extrapolated_period": float(extrapolated_period),
        "cross_tableau_extrapolated_period_difference": float(
            abs(extrapolated_period - classical_extrapolated_period)
        ),
        "node_maximum_difference_decimal": str(node_maximum),
        "node_maximum_difference": float(node_maximum),
        "node_rms_difference_decimal": str(node_rms),
        "node_rms_difference": float(node_rms),
        "tangent_line_metrics": tangent_metrics,
        "nodes_decimal": [[str(value) for value in row] for row in nodes],
        "tangent_nodes_decimal": [[str(value) for value in row] for row in tangents],
        "checks": checks,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(checks.values()),
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {key: value for key, value in output.items() if key not in {"nodes_decimal", "tangent_nodes_decimal"}},
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
