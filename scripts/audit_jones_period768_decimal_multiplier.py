#!/usr/bin/env python3
"""Audit the full period-768 monodromy in 50-digit Decimal arithmetic."""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, localcontext
from pathlib import Path

from audit_jones_period768_decimal_segments import dec, max_difference, rk4
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period768-decimal-multiplier-audit-manifest.v1"


def matmul(left: list[Decimal], right: list[Decimal]) -> list[Decimal]:
    return [
        sum(left[3 * row + inner] * right[3 * inner + column] for inner in range(3))
        for row in range(3)
        for column in range(3)
    ]


def matvec(matrix: list[Decimal], vector: list[Decimal]) -> list[Decimal]:
    return [
        sum(matrix[3 * row + column] * vector[column] for column in range(3))
        for row in range(3)
    ]


def determinant(matrix: list[Decimal]) -> Decimal:
    a, b, c, d, e, f, g, h, i = matrix
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def characteristic_root(matrix: list[Decimal], start: Decimal, digits: int):
    trace = matrix[0] + matrix[4] + matrix[8]
    square = matmul(matrix, matrix)
    second = (trace * trace - square[0] - square[4] - square[8]) / Decimal(2)
    det = determinant(matrix)
    value = start
    tolerance = Decimal(10) ** Decimal(-(digits - 12))
    iterations = 0
    for iterations in range(1, 81):
        polynomial = value**3 - trace * value**2 + second * value - det
        derivative = Decimal(3) * value**2 - Decimal(2) * trace * value + second
        delta = polynomial / derivative
        value -= delta
        if abs(delta) <= tolerance:
            break
    residual = value**3 - trace * value**2 + second * value - det
    return value, abs(residual), iterations


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
        medium = rk4(node + identity, duration, int(task["steps"][0]), a, b, c)
        fine = rk4(node + identity, duration, int(task["steps"][1]), a, b, c)
        transported = matvec(fine[3:], tangent)
        return {
            "index": task["index"],
            "medium_transition": [str(value) for value in medium[3:]],
            "fine_transition": [str(value) for value in fine[3:]],
            "fine_medium_endpoint_difference": max_difference(medium[:3], fine[:3]),
            "fine_medium_transition_difference": max_difference(medium[3:], fine[3:]),
            "fine_orbit_matching_residual": max_difference(fine[:3], expected_node),
            "fine_tangent_matching_residual": max_difference(transported, expected_tangent),
        }


def median(values: list[Decimal]) -> Decimal:
    ordered = sorted(values)
    middle = len(ordered) // 2
    return (ordered[middle - 1] + ordered[middle]) / Decimal(2)


def profile_spectrum(transitions, shifts, digits):
    identity = [
        Decimal(1), Decimal(0), Decimal(0),
        Decimal(0), Decimal(1), Decimal(0),
        Decimal(0), Decimal(0), Decimal(1),
    ]
    products = []
    for shift in shifts:
        monodromy = identity
        for transition in transitions[shift:] + transitions[:shift]:
            monodromy = matmul(transition, monodromy)
        flip, flip_residual, flip_iterations = characteristic_root(
            monodromy, Decimal(-1), digits
        )
        neutral, neutral_residual, neutral_iterations = characteristic_root(
            monodromy, Decimal(1), digits
        )
        products.append(
            {
                "cyclic_shift": shift,
                "flip": flip,
                "flip_characteristic_residual": flip_residual,
                "flip_iterations": flip_iterations,
                "neutral": neutral,
                "neutral_characteristic_residual": neutral_residual,
                "neutral_iterations": neutral_iterations,
            }
        )
    flip_values = [row["flip"] for row in products]
    neutral_values = [row["neutral"] for row in products]
    flip_median = median(flip_values)
    return {
        "flip_median": flip_median,
        "flip_cyclic_spread": max(flip_values) - min(flip_values),
        "neutral_median": median(neutral_values),
        "maximum_characteristic_residual": max(
            max(row["flip_characteristic_residual"], row["neutral_characteristic_residual"])
            for row in products
        ),
        "products": products,
    }


def serializable_spectrum(spectrum):
    return {
        "flip_median_decimal": str(spectrum["flip_median"]),
        "flip_median": float(spectrum["flip_median"]),
        "flip_residual": float(spectrum["flip_median"] + Decimal(1)),
        "flip_cyclic_spread": float(spectrum["flip_cyclic_spread"]),
        "neutral_median_decimal": str(spectrum["neutral_median"]),
        "neutral_median": float(spectrum["neutral_median"]),
        "neutral_residual": float(spectrum["neutral_median"] - Decimal(1)),
        "maximum_characteristic_residual_decimal": str(
            spectrum["maximum_characteristic_residual"]
        ),
        "maximum_characteristic_residual": float(
            spectrum["maximum_characteristic_residual"]
        ),
        "products": [
            {
                "cyclic_shift": row["cyclic_shift"],
                "flip_decimal": str(row["flip"]),
                "flip": float(row["flip"]),
                "flip_characteristic_residual_decimal": str(
                    row["flip_characteristic_residual"]
                ),
                "flip_iterations": row["flip_iterations"],
                "neutral_decimal": str(row["neutral"]),
                "neutral": float(row["neutral"]),
                "neutral_characteristic_residual_decimal": str(
                    row["neutral_characteristic_residual"]
                ),
                "neutral_iterations": row["neutral_iterations"],
            }
            for row in spectrum["products"]
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--pilot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported decimal multiplier audit manifest")
    event_bytes = args.event.read_bytes()
    pilot_bytes = args.pilot.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    if sha256_bytes(pilot_bytes) != manifest["pilot_receipt_sha256"]:
        raise SystemExit("pilot receipt hash mismatch")
    event = json.loads(event_bytes)
    pilot = json.loads(pilot_bytes)
    if event.get("schema") != manifest["event_schema"] or event.get("passed"):
        raise SystemExit("bound event is not the failed source")
    if pilot.get("schema") != manifest["pilot_schema"] or not pilot.get("passed"):
        raise SystemExit("bound pilot is not the passed source")
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
                "steps": manifest["step_counts"],
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
        medium_transitions = [
            [Decimal(value) for value in row["medium_transition"]] for row in rows
        ]
        fine_transitions = [
            [Decimal(value) for value in row["fine_transition"]] for row in rows
        ]
        medium = profile_spectrum(
            medium_transitions, manifest["cyclic_shifts"], context.prec
        )
        fine = profile_spectrum(fine_transitions, manifest["cyclic_shifts"], context.prec)
        multiplier_difference = abs(medium["flip_median"] - fine["flip_median"])
        fine_neutral_residual = abs(fine["neutral_median"] - Decimal(1))

    acceptance = manifest["acceptance"]
    checks = {
        "multiplier_convergence": float(multiplier_difference)
        <= float(acceptance["maximum_medium_fine_flip_difference"]),
        "cyclic": float(fine["flip_cyclic_spread"])
        <= float(acceptance["maximum_fine_cyclic_spread"]),
        "characteristic": float(fine["maximum_characteristic_residual"])
        <= float(acceptance["maximum_fine_characteristic_residual"]),
        "neutral": float(fine_neutral_residual)
        <= float(acceptance["maximum_fine_neutral_residual"]),
        "endpoint_difference": max(row["fine_medium_endpoint_difference"] for row in rows)
        <= float(acceptance["maximum_fine_medium_endpoint_difference"]),
        "transition_difference": max(row["fine_medium_transition_difference"] for row in rows)
        <= float(acceptance["maximum_fine_medium_transition_difference"]),
        "orbit_matching": max(row["fine_orbit_matching_residual"] for row in rows)
        <= float(acceptance["maximum_fine_orbit_matching_residual"]),
        "tangent_matching": max(row["fine_tangent_matching_residual"] for row in rows)
        <= float(acceptance["maximum_fine_tangent_matching_residual"]),
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
        "schema": "butterfly.jones-period768-decimal-multiplier-audit-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "pilot_receipt_sha256": sha256_bytes(pilot_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "workers": workers,
        },
        "decimal_digits": manifest["decimal_digits"],
        "step_counts": manifest["step_counts"],
        "profiles": {
            "medium": serializable_spectrum(medium),
            "fine": serializable_spectrum(fine),
        },
        "medium_fine_flip_difference_decimal": str(multiplier_difference),
        "medium_fine_flip_difference": float(multiplier_difference),
        "maximum_fine_medium_endpoint_difference": max(
            row["fine_medium_endpoint_difference"] for row in rows
        ),
        "maximum_fine_medium_transition_difference": max(
            row["fine_medium_transition_difference"] for row in rows
        ),
        "maximum_fine_orbit_matching_residual": max(
            row["fine_orbit_matching_residual"] for row in rows
        ),
        "maximum_fine_tangent_matching_residual": max(
            row["fine_tangent_matching_residual"] for row in rows
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
