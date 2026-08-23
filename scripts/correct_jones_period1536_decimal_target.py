#!/usr/bin/env python3
"""Correct the EXP-299 period-1536 target in the exact Decimal map."""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, localcontext
from pathlib import Path

from continue_jones_period1536_decimal_child import (
    half_node_rms,
    phase_invariant_target_identity,
)
from correct_jones_period768_decimal_parent import (
    solve_linear,
    state_rhs,
    vector_add,
)
from switch_jones_period1536_decimal_child import evaluate, transverse_spectrum
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period1536-decimal-target-correction-manifest.v1"


def reduced_fixed_parameter_correction(rows, phase, phase_residual):
    """Eliminate cyclic node blocks to a four-variable fixed-a Newton system."""

    mapping = [Decimal(0)] * 12
    for index in range(3):
        mapping[4 * index + index] = Decimal(1)
    forcing = [Decimal(0)] * 3
    maps = []
    forcings = []

    def left_multiply(matrix3, matrix3x4):
        return [
            sum(
                matrix3[3 * row + inner] * matrix3x4[4 * inner + column]
                for inner in range(3)
            )
            for row in range(3)
            for column in range(4)
        ]

    for row in rows:
        maps.append(mapping)
        forcings.append(forcing)
        next_mapping = left_multiply(row["transition"], mapping)
        for state_row in range(3):
            next_mapping[4 * state_row + 3] += row["period_state"][state_row]
        next_forcing = vector_add(
            [
                sum(
                    row["transition"][3 * state_row + column]
                    * forcing[column]
                    for column in range(3)
                )
                for state_row in range(3)
            ],
            row["residual"],
        )
        mapping, forcing = next_mapping, next_forcing

    system = []
    for row in range(3):
        equation = mapping[4 * row : 4 * row + 4]
        equation[row] -= Decimal(1)
        system.append(equation)
    system.append(list(phase) + [Decimal(0)])
    base = solve_linear(
        system,
        [-value for value in forcing] + [-phase_residual],
    )
    corrections = [
        [
            sum(node_map[4 * row + column] * base[column] for column in range(4))
            + node_forcing[row]
            for row in range(3)
        ]
        for node_map, node_forcing in zip(maps, forcings)
    ]
    return corrections, base[3]


def periodicity_classification(amplitude: Decimal, manifest: dict) -> str:
    acceptance = manifest["acceptance"]
    if amplitude >= Decimal(str(acceptance["minimum_primitive_half_node_rms"])):
        return "primitive_period1536"
    if amplitude <= Decimal(str(acceptance["maximum_doubled_parent_half_node_rms"])):
        return "doubled_period768_parent"
    return "unresolved"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--branch", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    target_bytes = args.target.read_bytes()
    event_bytes = args.event.read_bytes()
    branch_bytes = args.branch.read_bytes()
    manifest = json.loads(manifest_bytes)
    target_receipt = json.loads(target_bytes)
    event_receipt = json.loads(event_bytes)
    branch_receipt = json.loads(branch_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported Decimal target-correction manifest")
    for name, payload, expected in (
        ("target", target_bytes, manifest["target_receipt_sha256"]),
        ("event", event_bytes, manifest["event_receipt_sha256"]),
        ("branch", branch_bytes, manifest["branch_receipt_sha256"]),
    ):
        if sha256_bytes(payload) != expected:
            raise SystemExit(f"{name} receipt hash mismatch")
    if (
        target_receipt.get("schema") != manifest["target_schema"]
        or target_receipt.get("classifications", {})
        .get(manifest["target_solver"], {})
        .get("child")
        != "stable"
    ):
        raise SystemExit("preserved stable EXP-299 child seed required")
    if (
        event_receipt.get("schema") != manifest["event_schema"]
        or not event_receipt.get("passed")
        or event_receipt.get("local_criticality_classification")
        != "supercritical"
    ):
        raise SystemExit("passed exact seventh-birth receipt required")
    if (
        branch_receipt.get("schema") != manifest["branch_schema"]
        or not branch_receipt.get("passed")
    ):
        raise SystemExit("passed exact branch receipt required")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    target = target_receipt["results"][manifest["target_solver"]]["child"]
    source_nodes = [
        [Decimal(str(value)) for value in row] for row in target["nodes"]
    ]
    nodes = [row.copy() for row in source_nodes]
    parameter = Decimal(str(target_receipt["target_a"]))
    period_time = Decimal(str(target["period_time"]))
    b = Decimal(str(manifest["fixed_b"]))
    c = Decimal(str(manifest["fixed_c"]))
    tolerance = Decimal(str(manifest["acceptance"]["maximum_residual"]))
    started = time.perf_counter()
    history = []
    rows = None
    with localcontext() as context:
        context.prec = int(manifest["decimal_digits"])
        phase = state_rhs(source_nodes[0], parameter, b, c)
        phase_norm = sum(value * value for value in phase).sqrt()
        phase = [value / phase_norm for value in phase]
        workers = min(int(manifest["workers"]), os.cpu_count() or 1)
        with ProcessPoolExecutor(max_workers=workers) as executor:
            for iteration in range(int(manifest["maximum_newton_updates"]) + 1):
                rows = evaluate(executor, nodes, period_time, parameter, manifest)
                matching = max(
                    abs(value) for row in rows for value in row["residual"]
                )
                phase_residual = sum(
                    phase[column] * (nodes[0][column] - source_nodes[0][column])
                    for column in range(3)
                )
                amplitude = half_node_rms(nodes)
                history.append(
                    {
                        "iteration": iteration,
                        "period_time_decimal": str(period_time),
                        "matching_residual_decimal": str(matching),
                        "matching_residual": float(matching),
                        "phase_residual_decimal": str(abs(phase_residual)),
                        "phase_residual": float(abs(phase_residual)),
                        "half_node_rms_decimal": str(amplitude),
                        "half_node_rms": float(amplitude),
                    }
                )
                print(json.dumps(history[-1], sort_keys=True), flush=True)
                if max(matching, abs(phase_residual)) <= tolerance:
                    break
                if iteration == int(manifest["maximum_newton_updates"]):
                    break
                corrections, period_delta = reduced_fixed_parameter_correction(
                    rows, phase, phase_residual
                )
                nodes = [
                    vector_add(node, correction)
                    for node, correction in zip(nodes, corrections)
                ]
                period_time += period_delta

        amplitude = half_node_rms(nodes)
        periodicity = periodicity_classification(amplitude, manifest)
        spectrum = transverse_spectrum(
            [row["transition"] for row in rows],
            manifest["cyclic_shifts"],
            int(manifest["decimal_digits"]),
        )

    margin = float(manifest["acceptance"]["stability_margin"])
    modulus = spectrum["dominant_modulus"]
    stability = (
        "stable"
        if modulus <= 1.0 - margin
        else "unstable"
        if modulus >= 1.0 + margin
        else "neutral"
    )
    source_identity = phase_invariant_target_identity(nodes, target["nodes"])
    branch_identity = phase_invariant_target_identity(
        nodes, branch_receipt["rows"][-1]["nodes_decimal"]
    )
    acceptance = manifest["acceptance"]
    checks = {
        "correction": max(
            history[-1]["matching_residual"], history[-1]["phase_residual"]
        )
        <= float(acceptance["maximum_residual"]),
        "classified_periodicity": periodicity != "unresolved",
        "period_ratio": abs(
            float(period_time) / float(event_receipt["event_period_decimal"]) - 2.0
        )
        <= float(acceptance["maximum_period_ratio_error"]),
        "cyclic_spectrum": spectrum["cyclic_spread"]
        <= float(acceptance["maximum_cyclic_spread"]),
        "neutral_spectrum": spectrum["maximum_neutral_residual"]
        <= float(acceptance["maximum_neutral_residual"]),
    }
    output = {
        "schema": manifest["output_schema"],
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "target_receipt_sha256": sha256_bytes(target_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "branch_receipt_sha256": sha256_bytes(branch_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "workers": workers,
        },
        "decimal_digits": manifest["decimal_digits"],
        "method": "rk4_three_eighths",
        "steps_per_segment": manifest["steps_per_segment"],
        "a_decimal": str(parameter),
        "period_time_decimal": str(period_time),
        "period_time": float(period_time),
        "initial_half_node_rms": history[0]["half_node_rms"],
        "half_node_rms_decimal": str(amplitude),
        "half_node_rms": float(amplitude),
        "periodicity_classification": periodicity,
        "stability": stability,
        "spectrum": spectrum,
        "source_target_identity": source_identity,
        "exp321_terminal_identity": branch_identity,
        "history": history,
        "nodes_decimal": [[str(value) for value in row] for row in nodes],
        "checks": checks,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(checks.values()),
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    printed = {key: value for key, value in output.items() if key != "nodes_decimal"}
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
