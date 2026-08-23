#!/usr/bin/env python3
"""Continue the immediate Decimal period-1536 daughter toward EXP-299 scale."""

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

from correct_jones_period768_decimal_parent import state_rhs, vector_add
from switch_jones_period1536_decimal_child import (
    evaluate,
    reduced_newton_correction,
    transverse_spectrum,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period1536-decimal-continuation-manifest.v1"


def selected_source_candidates(receipt: dict, manifest: dict) -> list[dict]:
    selected = [
        row
        for row in receipt.get("candidates", [])
        if int(row["direction"]) == int(manifest["source_direction"])
        and float(row["step_length"])
        in {float(value) for value in manifest["source_step_lengths"]}
    ]
    selected.sort(key=lambda row: float(row["step_length"]))
    if [float(row["step_length"]) for row in selected] != [
        float(value) for value in manifest["source_step_lengths"]
    ]:
        raise ValueError("continuation sources are not uniquely selected")
    return selected


def normalized_secant(left: dict, right: dict):
    left_nodes = [[Decimal(value) for value in row] for row in left["nodes_decimal"]]
    right_nodes = [[Decimal(value) for value in row] for row in right["nodes_decimal"]]
    node_difference = [
        [right_value - left_value for left_value, right_value in zip(left_row, right_row)]
        for left_row, right_row in zip(left_nodes, right_nodes)
    ]
    period_difference = Decimal(right["period_time_decimal"]) - Decimal(
        left["period_time_decimal"]
    )
    parameter_difference = Decimal(right["a_decimal"]) - Decimal(left["a_decimal"])
    norm = (
        sum(value * value for row in node_difference for value in row)
        + period_difference * period_difference
        + parameter_difference * parameter_difference
    ).sqrt()
    return (
        [[value / norm for value in row] for row in node_difference],
        period_difference / norm,
        parameter_difference / norm,
        norm,
    )


def half_node_rms(nodes):
    half = len(nodes) // 2
    return (
        sum(
            (nodes[index + half][column] - nodes[index][column]) ** 2
            for index in range(half)
            for column in range(3)
        )
        / Decimal(3 * half)
    ).sqrt()


def phase_invariant_target_identity(nodes, target_nodes):
    left = np.asarray([[float(value) for value in row] for row in nodes])
    right = np.asarray(target_nodes, dtype=float)
    if left.shape != right.shape:
        raise ValueError("target node shape changed")
    best_rms = float("inf")
    best_shift = 0
    for shift in range(len(left)):
        rms = float(np.sqrt(np.mean((left - np.roll(right, shift, axis=0)) ** 2)))
        if rms < best_rms:
            best_rms = rms
            best_shift = shift
    return {"rms": best_rms, "node_shift": best_shift}


def correct_step(
    executor,
    base,
    tangent_nodes,
    tangent_period,
    tangent_parameter,
    manifest,
):
    step = Decimal(str(manifest["continuation_step_length"]))
    base_nodes = [[Decimal(value) for value in row] for row in base["nodes_decimal"]]
    base_period = Decimal(base["period_time_decimal"])
    base_parameter = Decimal(base["a_decimal"])
    predictor_nodes = [
        [value + step * tangent for value, tangent in zip(row, tangent_row)]
        for row, tangent_row in zip(base_nodes, tangent_nodes)
    ]
    predictor_period = base_period + step * tangent_period
    predictor_parameter = base_parameter + step * tangent_parameter
    nodes = [row.copy() for row in predictor_nodes]
    period_time = predictor_period
    parameter = predictor_parameter
    b = Decimal(str(manifest["fixed_b"]))
    c = Decimal(str(manifest["fixed_c"]))
    phase = state_rhs(base_nodes[0], base_parameter, b, c)
    phase_norm = sum(value * value for value in phase).sqrt()
    phase = [value / phase_norm for value in phase]
    tolerance = Decimal(str(manifest["acceptance"]["maximum_matching_residual"]))
    history = []
    rows = None
    for iteration in range(int(manifest["maximum_newton_updates"]) + 1):
        rows = evaluate(executor, nodes, period_time, parameter, manifest)
        matching = max(abs(value) for row in rows for value in row["residual"])
        phase_residual = sum(
            phase[column] * (nodes[0][column] - base_nodes[0][column])
            for column in range(3)
        )
        arclength = (
            sum(
                tangent * (value - predictor)
                for row, predictor_row, tangent_row in zip(
                    nodes, predictor_nodes, tangent_nodes
                )
                for value, predictor, tangent in zip(row, predictor_row, tangent_row)
            )
            + tangent_period * (period_time - predictor_period)
            + tangent_parameter * (parameter - predictor_parameter)
        )
        history.append(
            {
                "iteration": iteration,
                "a_decimal": str(parameter),
                "period_time_decimal": str(period_time),
                "matching_residual_decimal": str(matching),
                "matching_residual": float(matching),
                "phase_residual_decimal": str(abs(phase_residual)),
                "phase_residual": float(abs(phase_residual)),
                "arclength_residual_decimal": str(abs(arclength)),
                "arclength_residual": float(abs(arclength)),
            }
        )
        print(json.dumps(history[-1], sort_keys=True), flush=True)
        if max(matching, abs(phase_residual), abs(arclength)) <= tolerance:
            break
        if iteration == int(manifest["maximum_newton_updates"]):
            break
        corrections, period_delta, parameter_delta = reduced_newton_correction(
            rows,
            phase,
            phase_residual,
            tangent_nodes,
            arclength,
            tangent_period,
            tangent_parameter,
        )
        nodes = [
            vector_add(node, correction)
            for node, correction in zip(nodes, corrections)
        ]
        period_time += period_delta
        parameter += parameter_delta
    half_rms = half_node_rms(nodes)
    spectrum = transverse_spectrum(
        [row["transition"] for row in rows],
        manifest["cyclic_shifts"],
        int(manifest["decimal_digits"]),
    )
    return {
        "a_decimal": str(parameter),
        "a": float(parameter),
        "period_time_decimal": str(period_time),
        "period_time": float(period_time),
        "half_node_rms_decimal": str(half_rms),
        "half_node_rms": float(half_rms),
        "spectrum": spectrum,
        "history": history,
        "nodes_decimal": [[str(value) for value in row] for row in nodes],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    source_bytes = args.source.read_bytes()
    target_bytes = args.target.read_bytes()
    manifest = json.loads(manifest_bytes)
    source_receipt = json.loads(source_bytes)
    target_receipt = json.loads(target_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported Decimal continuation manifest")
    if sha256_bytes(source_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash mismatch")
    if sha256_bytes(target_bytes) != manifest["target_receipt_sha256"]:
        raise SystemExit("target receipt hash mismatch")
    if (
        source_receipt.get("schema") != manifest["source_schema"]
        or not source_receipt.get("passed")
        or source_receipt.get("local_criticality_classification")
        != "supercritical"
    ):
        raise SystemExit("a passed supercritical source is required")
    if (
        target_receipt.get("schema") != manifest["target_schema"]
        or target_receipt.get("classifications", {}).get("dop853", {}).get("child")
        != "stable"
    ):
        raise SystemExit("the qualified stable target candidate is required")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    try:
        selected = selected_source_candidates(source_receipt, manifest)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    target_nodes = target_receipt["results"][manifest["target_solver"]]["child"][
        "nodes"
    ]
    started = time.perf_counter()
    with localcontext() as context:
        context.prec = int(manifest["decimal_digits"])
        tangent_nodes, tangent_period, tangent_parameter, source_secant_norm = (
            normalized_secant(selected[0], selected[1])
        )
        workers = min(int(manifest["workers"]), os.cpu_count() or 1)
        rows = []
        current = selected[1]
        with ProcessPoolExecutor(max_workers=workers) as executor:
            for index in range(int(manifest["continuation_steps"])):
                corrected = correct_step(
                    executor,
                    current,
                    tangent_nodes,
                    tangent_period,
                    tangent_parameter,
                    manifest,
                )
                corrected["index"] = index + 1
                corrected["target_identity"] = phase_invariant_target_identity(
                    corrected["nodes_decimal"], target_nodes
                )
                rows.append(corrected)
                next_tangent = normalized_secant(current, corrected)
                tangent_nodes, tangent_period, tangent_parameter, _ = next_tangent
                current = corrected

    source_a = float(selected[1]["a"])
    coordinates = [source_a] + [row["a"] for row in rows]
    amplitudes = [float(selected[1]["half_node_rms"])] + [
        row["half_node_rms"] for row in rows
    ]
    increments = np.diff(coordinates)
    fold_brackets = [
        {
            "left_index": index,
            "right_index": index + 1,
            "left_a": coordinates[index],
            "right_a": coordinates[index + 1],
        }
        for index in range(1, len(increments))
        if increments[index - 1] * increments[index] < 0.0
    ]
    margin = float(manifest["acceptance"]["stability_margin"])
    stability = [
        "stable"
        if row["spectrum"]["dominant_modulus"] <= 1.0 - margin
        else "unstable"
        if row["spectrum"]["dominant_modulus"] >= 1.0 + margin
        else "neutral"
        for row in rows
    ]
    acceptance = manifest["acceptance"]
    checks = {
        "row_count": len(rows) == int(manifest["continuation_steps"]),
        "correction": all(
            max(
                row["history"][-1]["matching_residual"],
                row["history"][-1]["phase_residual"],
                row["history"][-1]["arclength_residual"],
            )
            <= float(acceptance["maximum_matching_residual"])
            for row in rows
        ),
        "amplitude_growth": all(right > left for left, right in zip(amplitudes, amplitudes[1:])),
        "terminal_amplitude": amplitudes[-1]
        >= float(acceptance["minimum_terminal_half_node_rms"]),
        "period_ratio": max(
            abs(row["period_time"] / float(source_receipt["event_period_decimal"]) - 2.0)
            for row in rows
        ) <= float(acceptance["maximum_period_ratio_error"]),
        "cyclic_spectrum": max(row["spectrum"]["cyclic_spread"] for row in rows)
        <= float(acceptance["maximum_cyclic_spread"]),
        "neutral_spectrum": max(
            row["spectrum"]["maximum_neutral_residual"] for row in rows
        ) <= float(acceptance["maximum_neutral_residual"]),
    }
    output = {
        "schema": manifest["output_schema"],
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_receipt_sha256": sha256_bytes(source_bytes),
        "target_receipt_sha256": sha256_bytes(target_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "workers": workers,
        },
        "decimal_digits": manifest["decimal_digits"],
        "method": "rk4_three_eighths",
        "steps_per_segment": manifest["steps_per_segment"],
        "source_secant_norm_decimal": str(source_secant_norm),
        "continuation_step_length": manifest["continuation_step_length"],
        "rows": rows,
        "a_coordinates": coordinates,
        "half_node_rms": amplitudes,
        "a_increments": increments.tolist(),
        "fold_brackets": fold_brackets,
        "stability": stability,
        "minimum_target_node_rms": min(row["target_identity"]["rms"] for row in rows),
        "checks": checks,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(checks.values()),
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    printed = {**output, "rows": [
        {key: value for key, value in row.items() if key != "nodes_decimal"}
        for row in rows
    ]}
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
