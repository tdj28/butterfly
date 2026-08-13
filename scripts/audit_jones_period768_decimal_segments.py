#!/usr/bin/env python3
"""Pilot high-precision state and variational integration on selected segments."""

from __future__ import annotations

import argparse
import json
import platform
import time
from decimal import Decimal, localcontext
from pathlib import Path

from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period768-decimal-segment-pilot-manifest.v1"


def dec(value) -> Decimal:
    return Decimal(repr(float(value)))


def rhs(value: list[Decimal], a: Decimal, b: Decimal, c: Decimal) -> list[Decimal]:
    x, y, z = value[:3]
    derivative = [-y - z, x + a * y, b + z * (x - c)]
    matrix = value[3:]
    jacobian = (
        (Decimal(0), Decimal(-1), Decimal(-1)),
        (Decimal(1), a, Decimal(0)),
        (z, Decimal(0), x - c),
    )
    for row in range(3):
        for column in range(3):
            derivative.append(
                sum(
                    jacobian[row][inner] * matrix[3 * inner + column]
                    for inner in range(3)
                )
            )
    return derivative


def rk4(initial: list[Decimal], duration: Decimal, steps: int, a, b, c):
    value = initial.copy()
    step = duration / Decimal(steps)
    half = step / Decimal(2)
    sixth = step / Decimal(6)
    for _ in range(steps):
        k1 = rhs(value, a, b, c)
        k2 = rhs([v + half * k for v, k in zip(value, k1)], a, b, c)
        k3 = rhs([v + half * k for v, k in zip(value, k2)], a, b, c)
        k4 = rhs([v + step * k for v, k in zip(value, k3)], a, b, c)
        value = [
            v + sixth * (d1 + Decimal(2) * d2 + Decimal(2) * d3 + d4)
            for v, d1, d2, d3, d4 in zip(value, k1, k2, k3, k4)
        ]
    return value


def max_difference(left, right) -> float:
    return float(max(abs(a - b) for a, b in zip(left, right)))


def convergence_ratio(coarse, medium, fine) -> float:
    denominator = max_difference(medium, fine)
    return float("inf") if denominator == 0.0 else max_difference(coarse, medium) / denominator


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--resolution", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported decimal segment pilot manifest")
    event_bytes = args.event.read_bytes()
    resolution_bytes = args.resolution.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    if sha256_bytes(resolution_bytes) != manifest["resolution_receipt_sha256"]:
        raise SystemExit("resolution receipt hash mismatch")
    event = json.loads(event_bytes)
    resolution = json.loads(resolution_bytes)
    if event.get("schema") != manifest["event_schema"] or event.get("passed"):
        raise SystemExit("bound event is not the failed source")
    if resolution.get("schema") != manifest["resolution_schema"] or not resolution.get("passed"):
        raise SystemExit("bound resolution diagnostic is not the passed source")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    started = time.perf_counter()
    rows = []
    with localcontext() as context:
        context.prec = int(manifest["decimal_digits"])
        a = dec(event["corrected_a"])
        b = dec(event["fixed_b"])
        c = dec(event["fixed_c"])
        duration = dec(event["period_time"]) / Decimal(int(event["segment_count"]))
        nodes = [[dec(value) for value in row] for row in event["nodes"]]
        tangents = [[dec(value) for value in row] for row in event["tangent_nodes"]]
        identity = [
            Decimal(1), Decimal(0), Decimal(0),
            Decimal(0), Decimal(1), Decimal(0),
            Decimal(0), Decimal(0), Decimal(1),
        ]
        for index in map(int, manifest["segment_indices"]):
            initial = nodes[index] + identity
            integrations = [
                rk4(initial, duration, int(steps), a, b, c)
                for steps in manifest["step_counts"]
            ]
            endpoints = [row[:3] for row in integrations]
            transitions = [row[3:] for row in integrations]
            next_index = (index + 1) % int(event["segment_count"])
            expected_tangent = tangents[next_index]
            if next_index == 0:
                expected_tangent = [-value for value in expected_tangent]
            transported = [
                sum(transitions[-1][3 * row + column] * tangents[index][column] for column in range(3))
                for row in range(3)
            ]
            rows.append(
                {
                    "segment_index": index,
                    "endpoint_convergence_ratio": convergence_ratio(*endpoints),
                    "transition_convergence_ratio": convergence_ratio(*transitions),
                    "fine_medium_endpoint_difference": max_difference(endpoints[-2], endpoints[-1]),
                    "fine_medium_transition_difference": max_difference(transitions[-2], transitions[-1]),
                    "fine_orbit_matching_residual": max_difference(endpoints[-1], nodes[next_index]),
                    "fine_tangent_matching_residual": max_difference(transported, expected_tangent),
                }
            )

    acceptance = manifest["acceptance"]
    checks = {
        "endpoint_convergence": min(row["endpoint_convergence_ratio"] for row in rows)
        >= float(acceptance["minimum_endpoint_convergence_ratio"]),
        "transition_convergence": min(row["transition_convergence_ratio"] for row in rows)
        >= float(acceptance["minimum_transition_convergence_ratio"]),
        "endpoint_difference": max(row["fine_medium_endpoint_difference"] for row in rows)
        <= float(acceptance["maximum_fine_medium_endpoint_difference"]),
        "transition_difference": max(row["fine_medium_transition_difference"] for row in rows)
        <= float(acceptance["maximum_fine_medium_transition_difference"]),
        "orbit_matching": max(row["fine_orbit_matching_residual"] for row in rows)
        <= float(acceptance["maximum_fine_orbit_matching_residual"]),
        "tangent_matching": max(row["fine_tangent_matching_residual"] for row in rows)
        <= float(acceptance["maximum_fine_tangent_matching_residual"]),
    }
    output = {
        "schema": "butterfly.jones-period768-decimal-segment-pilot-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "resolution_receipt_sha256": sha256_bytes(resolution_bytes),
        "source": source,
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "decimal_digits": manifest["decimal_digits"],
        "step_counts": manifest["step_counts"],
        "rows": rows,
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
