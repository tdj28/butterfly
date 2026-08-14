#!/usr/bin/env python3
"""Correct a period-1536 flip bracket with Decimal cyclic elimination."""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, localcontext
from pathlib import Path

import numpy as np

from butterfly import RosslerParameters, SolverConfig
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from correct_jones_period768_decimal_augmented import (
    augmented_newton_correction,
    evaluate,
    maximum_residual,
    rms_half_node_separation,
)
from correct_jones_period768_decimal_parent import state_rhs, vector_add
from solve_augmented_segmented_flip import initial_tangent_nodes
from solve_jones_period12_augmented_flip import selected_event_bracket


SCHEMA = "butterfly.jones-period1536-decimal-augmented-bracket-manifest.v1"


def secant_seed(source: dict, bracket: dict) -> dict:
    left = source["rows"][int(bracket["left_index"])]
    right = source["rows"][int(bracket["right_index"])]
    if not left["status"]["success"] or not right["status"]["success"]:
        raise ValueError("bracket source rows are not successful")
    left_residual = float(bracket["left_multiplier"]["real"]) + 1.0
    right_residual = float(bracket["right_multiplier"]["real"]) + 1.0
    seed_a = (
        float(left["a"]) * right_residual
        - float(right["a"]) * left_residual
    ) / (right_residual - left_residual)
    fraction = (seed_a - float(left["a"])) / (
        float(right["a"]) - float(left["a"])
    )
    nodes = (1.0 - fraction) * np.asarray(left["nodes"], dtype=float)
    nodes += fraction * np.asarray(right["nodes"], dtype=float)
    return {
        "a": seed_a,
        "period_time": (1.0 - fraction) * float(left["period_time"])
        + fraction * float(right["period_time"]),
        "nodes": nodes,
        "fraction": fraction,
        "source_row_indices": [
            int(bracket["left_index"]),
            int(bracket["right_index"]),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--bracket", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported period-1536 Decimal bracket manifest")
    source_bytes = args.source.read_bytes()
    bracket_bytes = args.bracket.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash mismatch")
    if sha256_bytes(bracket_bytes) != manifest["bracket_receipt_sha256"]:
        raise SystemExit("bracket receipt hash mismatch")
    source_receipt = json.loads(source_bytes)
    bracket_receipt = json.loads(bracket_bytes)
    if source_receipt.get("schema") != manifest["source_schema"]:
        raise SystemExit("source receipt schema mismatch")
    if not source_receipt.get("passed") and not manifest.get(
        "allow_failed_source_prefix", False
    ):
        raise SystemExit("failed source prefix is not authorized")
    try:
        event_bracket = selected_event_bracket(bracket_receipt, manifest)
        seed = secant_seed(source_receipt, event_bracket)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    source_rows = [
        source_receipt["rows"][int(event_bracket["left_index"])],
        source_receipt["rows"][int(event_bracket["right_index"])],
    ]
    if max(float(row["status"]["matching_residual"]) for row in source_rows) > float(
        manifest["maximum_source_matching_residual"]
    ):
        raise SystemExit("bracket source rows exceed the matching gate")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    fixed_b = float(manifest["fixed_b"])
    fixed_c = float(manifest["fixed_c"])
    segment_count = int(manifest["segment_count"])
    if len(seed["nodes"]) != segment_count:
        raise SystemExit("seed segment count mismatch")
    seed_parameters = RosslerParameters(a=seed["a"], b=fixed_b, c=fixed_c)
    tangent_solver = SolverConfig(**manifest["tangent_seed_solver"])
    tangent_nodes, seed_multiplier = initial_tangent_nodes(
        seed["nodes"], seed["period_time"], seed_parameters, tangent_solver
    )
    started = time.perf_counter()

    with localcontext() as context:
        context.prec = int(manifest["decimal_digits"])
        nodes = [
            [Decimal(repr(float(value))) for value in row] for row in seed["nodes"]
        ]
        tangents = [
            [Decimal(repr(float(value))) for value in row] for row in tangent_nodes
        ]
        seed_nodes = [row.copy() for row in nodes]
        seed_tangents = [row.copy() for row in tangents]
        period_time = Decimal(repr(float(seed["period_time"])))
        seed_period = period_time
        parameter = Decimal(repr(float(seed["a"])))
        seed_parameter = parameter
        b = Decimal(repr(fixed_b))
        c = Decimal(repr(fixed_c))
        phase = state_rhs(nodes[0], parameter, b, c)
        phase_norm = sum(value * value for value in phase).sqrt()
        phase = [value / phase_norm for value in phase]
        tolerance = Decimal(str(manifest["acceptance"]["maximum_augmented_residual"]))
        workers = min(int(manifest["workers"]), os.cpu_count() or 1)
        history = []
        rows = None
        with ProcessPoolExecutor(max_workers=workers) as executor:
            for iteration in range(int(manifest["maximum_newton_updates"]) + 1):
                rows = evaluate(
                    executor,
                    nodes,
                    tangents,
                    period_time,
                    parameter,
                    b,
                    c,
                    manifest,
                )
                orbit_residual = maximum_residual(rows, "orbit_residual")
                tangent_residual = maximum_residual(rows, "tangent_residual")
                phase_residual = sum(
                    phase[column] * (nodes[0][column] - seed_nodes[0][column])
                    for column in range(3)
                )
                norm_residual = sum(value * value for value in tangents[0]) - Decimal(1)
                history.append(
                    {
                        "iteration": iteration,
                        "a_decimal": str(parameter),
                        "period_time_decimal": str(period_time),
                        "orbit_residual_decimal": str(orbit_residual),
                        "orbit_residual": float(orbit_residual),
                        "tangent_residual_decimal": str(tangent_residual),
                        "tangent_residual": float(tangent_residual),
                        "phase_residual_decimal": str(abs(phase_residual)),
                        "phase_residual": float(abs(phase_residual)),
                        "normalization_residual_decimal": str(abs(norm_residual)),
                        "normalization_residual": float(abs(norm_residual)),
                    }
                )
                print(json.dumps(history[-1], sort_keys=True), flush=True)
                if max(
                    orbit_residual,
                    tangent_residual,
                    abs(phase_residual),
                    abs(norm_residual),
                ) <= tolerance:
                    break
                if iteration == int(manifest["maximum_newton_updates"]):
                    break
                state_delta, tangent_delta, period_delta, parameter_delta = (
                    augmented_newton_correction(
                        rows, phase, phase_residual, tangents[0], norm_residual
                    )
                )
                nodes = [
                    vector_add(node, delta)
                    for node, delta in zip(nodes, state_delta)
                ]
                tangents = [
                    vector_add(tangent, delta)
                    for tangent, delta in zip(tangents, tangent_delta)
                ]
                period_time += period_delta
                parameter += parameter_delta

        maximum_node_displacement = max(
            abs(value - seed_value)
            for node, seed_node in zip(nodes, seed_nodes)
            for value, seed_value in zip(node, seed_node)
        )
        maximum_tangent_displacement = max(
            abs(value - seed_value)
            for tangent, seed_tangent in zip(tangents, seed_tangents)
            for value, seed_value in zip(tangent, seed_tangent)
        )
        period_displacement = abs(period_time - seed_period)
        parameter_displacement = abs(parameter - seed_parameter)
        half_node_rms = rms_half_node_separation(nodes)

    acceptance = manifest["acceptance"]
    lower_a, upper_a = map(Decimal, map(str, manifest["a_bounds"]))
    checks = {
        "correction": max(
            history[-1]["orbit_residual"],
            history[-1]["tangent_residual"],
            history[-1]["phase_residual"],
            history[-1]["normalization_residual"],
        )
        <= float(acceptance["maximum_augmented_residual"]),
        "a_bounds": lower_a <= parameter <= upper_a,
        "source_neighborhood": (
            maximum_node_displacement
            <= Decimal(str(acceptance["maximum_source_node_displacement"]))
            and maximum_tangent_displacement
            <= Decimal(str(acceptance["maximum_source_tangent_displacement"]))
            and period_displacement
            <= Decimal(str(acceptance["maximum_source_period_displacement"]))
        ),
        "primitive_half_separation": half_node_rms
        >= Decimal(str(acceptance["minimum_half_node_rms_separation"])),
    }
    output = {
        "schema": "butterfly.jones-period1536-decimal-augmented-bracket-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_receipt_sha256": sha256_bytes(source_bytes),
        "bracket_receipt_sha256": sha256_bytes(bracket_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "workers": workers,
        },
        "decimal_digits": manifest["decimal_digits"],
        "method": manifest["method"],
        "steps_per_segment": manifest["steps_per_segment"],
        "segment_count": len(nodes),
        "seed_a": seed["a"],
        "seed_period_time": seed["period_time"],
        "seed_multiplier": {
            "real": float(seed_multiplier.real),
            "imag": float(seed_multiplier.imag),
        },
        "secant_fraction": seed["fraction"],
        "source_row_indices": seed["source_row_indices"],
        "history": history,
        "corrected_a_decimal": str(parameter),
        "corrected_a": float(parameter),
        "period_time_decimal": str(period_time),
        "period_time": float(period_time),
        "parameter_displacement_decimal": str(parameter_displacement),
        "parameter_displacement": float(parameter_displacement),
        "maximum_source_node_displacement_decimal": str(maximum_node_displacement),
        "maximum_source_node_displacement": float(maximum_node_displacement),
        "maximum_source_tangent_displacement_decimal": str(maximum_tangent_displacement),
        "maximum_source_tangent_displacement": float(maximum_tangent_displacement),
        "source_period_displacement_decimal": str(period_displacement),
        "source_period_displacement": float(period_displacement),
        "half_node_rms_separation_decimal": str(half_node_rms),
        "half_node_rms_separation": float(half_node_rms),
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
