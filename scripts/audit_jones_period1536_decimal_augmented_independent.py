#!/usr/bin/env python3
"""Independently reproduce the Decimal period-1536 augmented flip root."""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, localcontext
from pathlib import Path

from audit_jones_period768_decimal_augmented_independent import (
    flattened_difference,
    rms,
    tangent_line_metrics,
)
from audit_jones_period768_decimal_richardson import richardson
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from correct_jones_period768_decimal_parent import state_rhs
from refine_jones_period768_decimal_augmented import (
    convergence_ratio,
    correct_profile,
)


SCHEMA = "butterfly.jones-period1536-decimal-augmented-independent-manifest.v1"


def accepted_a_envelope(continuation: dict) -> tuple[Decimal, Decimal, int]:
    """Return the target-blind parameter envelope of successful stored rows."""

    accepted = [
        Decimal(str(row["a"]))
        for row in continuation.get("rows", [])
        if row.get("status", {}).get("success")
    ]
    if not accepted:
        raise ValueError("continuation has no successful rows")
    return min(accepted), max(accepted), len(accepted)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--classical", type=Path, required=True)
    parser.add_argument("--continuation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported independent period-1536 manifest")
    classical_bytes = args.classical.read_bytes()
    continuation_bytes = args.continuation.read_bytes()
    if sha256_bytes(classical_bytes) != manifest["classical_receipt_sha256"]:
        raise SystemExit("classical receipt hash mismatch")
    if sha256_bytes(continuation_bytes) != manifest["continuation_receipt_sha256"]:
        raise SystemExit("continuation receipt hash mismatch")
    classical = json.loads(classical_bytes)
    continuation = json.loads(continuation_bytes)
    if classical.get("schema") != manifest["classical_schema"] or classical.get("passed"):
        raise SystemExit("bound classical result is not the preserved failed source")
    failed_checks = sorted(name for name, passed in classical["checks"].items() if not passed)
    if failed_checks != sorted(manifest["required_classical_failed_checks"]):
        raise SystemExit("classical failure pattern changed")
    if continuation.get("schema") != manifest["continuation_schema"]:
        raise SystemExit("continuation schema mismatch")
    lower_a, upper_a, accepted_rows = accepted_a_envelope(continuation)
    envelope = manifest["continuation_envelope"]
    if accepted_rows < int(envelope["minimum_successful_rows"]):
        raise SystemExit("continuation envelope has too few successful rows")
    if lower_a != Decimal(envelope["expected_lower_a_decimal"]):
        raise SystemExit("continuation lower envelope changed")
    if upper_a != Decimal(envelope["expected_upper_a_decimal"]):
        raise SystemExit("continuation upper envelope changed")
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
                    {
                        key: value
                        for key, value in corrected.items()
                        if key not in {"nodes", "tangents", "period", "parameter"}
                    }
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
        classical_extrapolated_period = Decimal(classical["extrapolated_period_decimal"])
        node_differences = flattened_difference(nodes, classical_nodes)
        node_maximum = max(map(abs, node_differences))
        node_rms = rms(node_differences)
        tangent_metrics = tangent_line_metrics(classical_tangents, tangents)

    acceptance = manifest["acceptance"]
    finest = profiles[-1]
    checks = {
        "correction": all(row["converged"] for row in profiles),
        "a_convergence": float(acceptance["minimum_convergence_ratio"])
        <= float(a_ratio)
        <= float(acceptance["maximum_convergence_ratio"]),
        "period_convergence": float(acceptance["minimum_convergence_ratio"])
        <= float(period_ratio)
        <= float(acceptance["maximum_convergence_ratio"]),
        "continuation_envelope": (
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
        "schema": manifest["output_schema"],
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "classical_receipt_sha256": sha256_bytes(classical_bytes),
        "continuation_receipt_sha256": sha256_bytes(continuation_bytes),
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
        "continuation_envelope": {
            "lower_a_decimal": str(lower_a),
            "upper_a_decimal": str(upper_a),
            "successful_rows": accepted_rows,
        },
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
            {
                key: value
                for key, value in output.items()
                if key not in {"nodes_decimal", "tangent_nodes_decimal"}
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
