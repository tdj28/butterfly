#!/usr/bin/env python3
"""Add a third Decimal RK4 level and gate Richardson convergence."""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, localcontext
from pathlib import Path

from audit_jones_period768_decimal_multiplier import (
    profile_spectrum,
    serializable_spectrum,
)
from audit_jones_period768_decimal_segments import dec, max_difference, rk4
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period768-decimal-richardson-audit-manifest.v1"


def integrate_task(task: dict) -> dict:
    with localcontext() as context:
        context.prec = int(task["digits"])
        a, b, c = map(dec, (task["a"], task["b"], task["c"]))
        duration = dec(task["period_time"]) / Decimal(int(task["segment_count"]))
        node = [dec(value) for value in task["node"]]
        tangent = [dec(value) for value in task["tangent"]]
        expected_node = [dec(value) for value in task["expected_node"]]
        expected_tangent = [dec(value) for value in task["expected_tangent"]]
        identity = [
            Decimal(1), Decimal(0), Decimal(0),
            Decimal(0), Decimal(1), Decimal(0),
            Decimal(0), Decimal(0), Decimal(1),
        ]
        result = rk4(node + identity, duration, int(task["steps"]), a, b, c)
        matrix = result[3:]
        transported = [
            sum(matrix[3 * row + column] * tangent[column] for column in range(3))
            for row in range(3)
        ]
        return {
            "index": task["index"],
            "transition": [str(value) for value in matrix],
            "orbit_matching_residual": max_difference(result[:3], expected_node),
            "tangent_matching_residual": max_difference(transported, expected_tangent),
        }


def richardson(lower: Decimal, upper: Decimal, order: int) -> Decimal:
    return upper + (upper - lower) / (Decimal(2) ** order - Decimal(1))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported Decimal Richardson manifest")
    event_bytes = args.event.read_bytes()
    source_bytes = args.source.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    if sha256_bytes(source_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash mismatch")
    event = json.loads(event_bytes)
    source_receipt = json.loads(source_bytes)
    if event.get("schema") != manifest["event_schema"] or event.get("passed"):
        raise SystemExit("bound event is not the failed source")
    if source_receipt.get("schema") != manifest["source_schema"] or source_receipt.get("passed"):
        raise SystemExit("bound multiplier audit is not the failed source")
    failed = [key for key, value in source_receipt["checks"].items() if not value]
    if failed != [manifest["expected_source_failed_check"]]:
        raise SystemExit("source audit failure is not isolated as declared")
    if source_receipt["step_counts"] != manifest["source_step_counts"]:
        raise SystemExit("source step counts do not match")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    count = int(event["segment_count"])
    tasks = []
    for index in range(count):
        next_index = (index + 1) % count
        expected_tangent = list(event["tangent_nodes"][next_index])
        if next_index == 0:
            expected_tangent = [-float(value) for value in expected_tangent]
        tasks.append(
            {
                "index": index,
                "digits": manifest["decimal_digits"],
                "steps": manifest["new_step_count"],
                "a": event["corrected_a"],
                "b": event["fixed_b"],
                "c": event["fixed_c"],
                "period_time": event["period_time"],
                "segment_count": count,
                "node": event["nodes"][index],
                "tangent": event["tangent_nodes"][index],
                "expected_node": event["nodes"][next_index],
                "expected_tangent": expected_tangent,
            }
        )

    started = time.perf_counter()
    workers = min(int(manifest["workers"]), os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        rows = list(executor.map(integrate_task, tasks, chunksize=1))
    rows.sort(key=lambda row: row["index"])

    with localcontext() as context:
        context.prec = int(manifest["decimal_digits"])
        transitions = [
            [Decimal(value) for value in row["transition"]] for row in rows
        ]
        new_profile = profile_spectrum(
            transitions, manifest["cyclic_shifts"], context.prec
        )
        coarse_flip = Decimal(
            source_receipt["profiles"]["medium"]["flip_median_decimal"]
        )
        medium_flip = Decimal(
            source_receipt["profiles"]["fine"]["flip_median_decimal"]
        )
        fine_flip = new_profile["flip_median"]
        coarse_neutral = Decimal(
            source_receipt["profiles"]["medium"]["neutral_median_decimal"]
        )
        medium_neutral = Decimal(
            source_receipt["profiles"]["fine"]["neutral_median_decimal"]
        )
        fine_neutral = new_profile["neutral_median"]
        raw_ratio = abs((coarse_flip - medium_flip) / (medium_flip - fine_flip))
        first_flip = richardson(coarse_flip, medium_flip, manifest["method_order"])
        second_flip = richardson(medium_flip, fine_flip, manifest["method_order"])
        first_neutral = richardson(
            coarse_neutral, medium_neutral, manifest["method_order"]
        )
        second_neutral = richardson(
            medium_neutral, fine_neutral, manifest["method_order"]
        )

    acceptance = manifest["acceptance"]
    checks = {
        "raw_convergence": float(raw_ratio)
        >= float(acceptance["minimum_raw_convergence_ratio"])
        and float(raw_ratio) <= float(acceptance["maximum_raw_convergence_ratio"]),
        "richardson_flip_convergence": float(abs(first_flip - second_flip))
        <= float(acceptance["maximum_successive_richardson_flip_difference"]),
        "extrapolated_flip": float(abs(second_flip + Decimal(1)))
        <= float(acceptance["maximum_extrapolated_flip_residual"]),
        "richardson_neutral_convergence": float(abs(first_neutral - second_neutral))
        <= float(acceptance["maximum_successive_richardson_neutral_difference"]),
        "extrapolated_neutral": float(abs(second_neutral - Decimal(1)))
        <= float(acceptance["maximum_extrapolated_neutral_residual"]),
        "cyclic": float(new_profile["flip_cyclic_spread"])
        <= float(acceptance["maximum_new_cyclic_spread"]),
        "characteristic": float(new_profile["maximum_characteristic_residual"])
        <= float(acceptance["maximum_new_characteristic_residual"]),
        "orbit_matching": max(row["orbit_matching_residual"] for row in rows)
        <= float(acceptance["maximum_new_orbit_matching_residual"]),
        "tangent_matching": max(row["tangent_matching_residual"] for row in rows)
        <= float(acceptance["maximum_new_tangent_matching_residual"]),
        "primitive": float(event["minimum_proper_subperiod_closure"])
        >= float(acceptance["minimum_proper_subperiod_closure"]),
        "section_identity": bool(
            event["section_identity"]["historical_integration_success"]
            and event["section_identity"]["barrio_integration_success"]
            and int(event["section_identity"]["historical_phase_count"])
            == int(manifest["identity"]["historical_phase_count"])
            and int(event["section_identity"]["barrio_phase_count"])
            == int(manifest["identity"]["barrio_phase_count"])
        ),
    }
    output = {
        "schema": "butterfly.jones-period768-decimal-richardson-audit-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "source_receipt_sha256": sha256_bytes(source_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "workers": workers,
        },
        "decimal_digits": manifest["decimal_digits"],
        "step_counts": [*manifest["source_step_counts"], manifest["new_step_count"]],
        "new_profile": serializable_spectrum(new_profile),
        "raw_convergence_ratio_decimal": str(raw_ratio),
        "raw_convergence_ratio": float(raw_ratio),
        "richardson": {
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
        },
        "maximum_new_orbit_matching_residual": max(
            row["orbit_matching_residual"] for row in rows
        ),
        "maximum_new_tangent_matching_residual": max(
            row["tangent_matching_residual"] for row in rows
        ),
        "minimum_proper_subperiod_closure": event["minimum_proper_subperiod_closure"],
        "section_identity": event["section_identity"],
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
