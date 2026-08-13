#!/usr/bin/env python3
"""Independently audit period 768 with the fourth-order RK 3/8 tableau."""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, localcontext
from pathlib import Path

from audit_jones_period768_decimal_multiplier import profile_spectrum, serializable_spectrum
from audit_jones_period768_decimal_richardson import richardson
from audit_jones_period768_decimal_segments import dec, max_difference, rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period768-decimal-independent-richardson-manifest.v1"


def rk_three_eighths(initial, duration, steps, a, b, c):
    value = initial.copy()
    step = duration / Decimal(steps)
    third = step / Decimal(3)
    eighth = step / Decimal(8)
    for _ in range(steps):
        k1 = rhs(value, a, b, c)
        k2 = rhs([v + third * d1 for v, d1 in zip(value, k1)], a, b, c)
        k3 = rhs(
            [v + step * (-d1 / Decimal(3) + d2) for v, d1, d2 in zip(value, k1, k2)],
            a,
            b,
            c,
        )
        k4 = rhs(
            [v + step * (d1 - d2 + d3) for v, d1, d2, d3 in zip(value, k1, k2, k3)],
            a,
            b,
            c,
        )
        value = [
            v + eighth * (d1 + Decimal(3) * d2 + Decimal(3) * d3 + d4)
            for v, d1, d2, d3, d4 in zip(value, k1, k2, k3, k4)
        ]
    return value


def integrate_task(task):
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
        integrations = [
            rk_three_eighths(node + identity, duration, int(steps), a, b, c)
            for steps in task["steps"]
        ]
        fine_matrix = integrations[-1][3:]
        transported = [
            sum(fine_matrix[3 * row + column] * tangent[column] for column in range(3))
            for row in range(3)
        ]
        return {
            "index": task["index"],
            "transitions": [
                [str(value) for value in result[3:]] for result in integrations
            ],
            "fine_orbit_matching_residual": max_difference(
                integrations[-1][:3], expected_node
            ),
            "fine_tangent_matching_residual": max_difference(
                transported, expected_tangent
            ),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--classical", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported independent Decimal manifest")
    event_bytes = args.event.read_bytes()
    classical_bytes = args.classical.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    if sha256_bytes(classical_bytes) != manifest["classical_receipt_sha256"]:
        raise SystemExit("classical receipt hash mismatch")
    event = json.loads(event_bytes)
    classical = json.loads(classical_bytes)
    if event.get("schema") != manifest["event_schema"] or event.get("passed"):
        raise SystemExit("bound event is not the failed source")
    if classical.get("schema") != manifest["classical_schema"] or not classical.get("passed"):
        raise SystemExit("bound classical audit is not the passed source")
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
        spectra = []
        for profile_index in range(len(manifest["step_counts"])):
            transitions = [
                [Decimal(value) for value in row["transitions"][profile_index]]
                for row in rows
            ]
            spectra.append(
                profile_spectrum(transitions, manifest["cyclic_shifts"], context.prec)
            )
        coarse_flip, medium_flip, fine_flip = [row["flip_median"] for row in spectra]
        coarse_neutral, medium_neutral, fine_neutral = [
            row["neutral_median"] for row in spectra
        ]
        raw_ratio = abs((coarse_flip - medium_flip) / (medium_flip - fine_flip))
        first_flip = richardson(coarse_flip, medium_flip, manifest["method_order"])
        second_flip = richardson(medium_flip, fine_flip, manifest["method_order"])
        first_neutral = richardson(
            coarse_neutral, medium_neutral, manifest["method_order"]
        )
        second_neutral = richardson(
            medium_neutral, fine_neutral, manifest["method_order"]
        )
        classical_flip = Decimal(classical["richardson"]["second_flip_decimal"])
        classical_neutral = Decimal(
            classical["richardson"]["second_neutral_decimal"]
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
        "cross_tableau_flip": float(abs(second_flip - classical_flip))
        <= float(acceptance["maximum_cross_tableau_flip_difference"]),
        "richardson_neutral_convergence": float(abs(first_neutral - second_neutral))
        <= float(acceptance["maximum_successive_richardson_neutral_difference"]),
        "extrapolated_neutral": float(abs(second_neutral - Decimal(1)))
        <= float(acceptance["maximum_extrapolated_neutral_residual"]),
        "cross_tableau_neutral": float(abs(second_neutral - classical_neutral))
        <= float(acceptance["maximum_cross_tableau_neutral_difference"]),
        "cyclic": float(spectra[-1]["flip_cyclic_spread"])
        <= float(acceptance["maximum_fine_cyclic_spread"]),
        "characteristic": float(spectra[-1]["maximum_characteristic_residual"])
        <= float(acceptance["maximum_fine_characteristic_residual"]),
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
        "schema": "butterfly.jones-period768-decimal-independent-richardson-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "classical_receipt_sha256": sha256_bytes(classical_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "workers": workers,
        },
        "decimal_digits": manifest["decimal_digits"],
        "method": manifest["method"],
        "step_counts": manifest["step_counts"],
        "profiles": [serializable_spectrum(row) for row in spectra],
        "raw_convergence_ratio_decimal": str(raw_ratio),
        "raw_convergence_ratio": float(raw_ratio),
        "richardson": {
            "first_flip_decimal": str(first_flip),
            "first_flip": float(first_flip),
            "second_flip_decimal": str(second_flip),
            "second_flip": float(second_flip),
            "successive_flip_difference": float(abs(first_flip - second_flip)),
            "second_flip_residual": float(second_flip + Decimal(1)),
            "classical_flip_decimal": str(classical_flip),
            "cross_tableau_flip_difference": float(abs(second_flip - classical_flip)),
            "first_neutral_decimal": str(first_neutral),
            "first_neutral": float(first_neutral),
            "second_neutral_decimal": str(second_neutral),
            "second_neutral": float(second_neutral),
            "successive_neutral_difference": float(abs(first_neutral - second_neutral)),
            "second_neutral_residual": float(second_neutral - Decimal(1)),
            "classical_neutral_decimal": str(classical_neutral),
            "cross_tableau_neutral_difference": float(
                abs(second_neutral - classical_neutral)
            ),
        },
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
