#!/usr/bin/env python3
"""Connect the immediate seventh daughter to the qualified eighth event."""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, localcontext
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from continue_jones_period1536_decimal_child import (
    correct_step,
    half_node_rms,
    normalized_secant,
    phase_invariant_target_identity,
)
from correct_jones_period1536_decimal_target import (
    reduced_fixed_parameter_correction,
    trial_is_acceptable,
)
from correct_jones_period768_decimal_parent import state_rhs
from switch_jones_period1536_decimal_child import evaluate, transverse_spectrum
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period1536-decimal-event-connection-manifest.v1"


def interpolate(left: dict, right: dict, target_a: Decimal):
    left_a = Decimal(left["a_decimal"])
    right_a = Decimal(right["a_decimal"])
    if not min(left_a, right_a) <= target_a <= max(left_a, right_a):
        raise ValueError("target coordinate is not bracketed")
    fraction = (target_a - left_a) / (right_a - left_a)
    left_nodes = [[Decimal(value) for value in row] for row in left["nodes_decimal"]]
    right_nodes = [[Decimal(value) for value in row] for row in right["nodes_decimal"]]
    nodes = [
        [lvalue + fraction * (rvalue - lvalue) for lvalue, rvalue in zip(lrow, rrow)]
        for lrow, rrow in zip(left_nodes, right_nodes)
    ]
    left_period = Decimal(left["period_time_decimal"])
    right_period = Decimal(right["period_time_decimal"])
    period = left_period + fraction * (right_period - left_period)
    return nodes, period, fraction


def target_profile(receipt: dict, steps: int) -> dict:
    profiles = [
        profile
        for profile in receipt.get("profiles", [])
        if int(profile["steps_per_segment"]) == steps
    ]
    if len(profiles) != 1:
        raise ValueError("target event profile is not uniquely selected")
    return profiles[0]


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
        raise SystemExit("unsupported event-connection manifest")
    if sha256_bytes(source_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash mismatch")
    if sha256_bytes(target_bytes) != manifest["target_receipt_sha256"]:
        raise SystemExit("target receipt hash mismatch")
    if (
        source_receipt.get("schema") != manifest["source_schema"]
        or source_receipt.get("passed") is not True
        or len(source_receipt.get("rows", [])) < 2
    ):
        raise SystemExit("passed continuation source with two rows required")
    if (
        target_receipt.get("schema") != manifest["target_schema"]
        or target_receipt.get("passed") is not True
    ):
        raise SystemExit("passed independent event target required")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    steps = int(manifest["steps_per_segment"])
    try:
        profile = target_profile(target_receipt, steps)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    target_a = Decimal(profile["a_decimal"])
    target_nodes = target_receipt["nodes_decimal"]
    target_period = Decimal(profile["period_time_decimal"])
    source_rows = source_receipt["rows"]
    started = time.perf_counter()

    with localcontext() as context:
        context.prec = int(manifest["decimal_digits"])
        tangent_nodes, tangent_period, tangent_parameter, secant_norm = normalized_secant(
            source_rows[-2], source_rows[-1]
        )
        workers = min(int(manifest["workers"]), os.cpu_count() or 1)
        continued = []
        current = source_rows[-1]
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
                continued.append(corrected)
                tangent_nodes, tangent_period, tangent_parameter, _ = normalized_secant(
                    current, corrected
                )
                current = corrected

            combined = [source_rows[-1], *continued]
            brackets = [
                (left, right)
                for left, right in zip(combined, combined[1:])
                if min(Decimal(left["a_decimal"]), Decimal(right["a_decimal"]))
                <= target_a
                <= max(Decimal(left["a_decimal"]), Decimal(right["a_decimal"]))
            ]
            if len(brackets) == 1:
                bracket_left, bracket_right = brackets[0]
                nodes, period_time, interpolation_fraction = interpolate(
                    bracket_left, bracket_right, target_a
                )
                phase = state_rhs(
                    nodes[0],
                    target_a,
                    Decimal(str(manifest["fixed_b"])),
                    Decimal(str(manifest["fixed_c"])),
                )
                phase_norm = sum(value * value for value in phase).sqrt()
                phase = [value / phase_norm for value in phase]
                phase_source = [value for value in nodes[0]]
                correction_history = []
                trial_history = []
                map_rows = evaluate(executor, nodes, period_time, target_a, manifest)
                termination_reason = "maximum_updates"
                tolerance = Decimal(str(manifest["acceptance"]["maximum_residual"]))
                for iteration in range(int(manifest["maximum_newton_updates"]) + 1):
                    matching = max(
                        abs(value) for row in map_rows for value in row["residual"]
                    )
                    phase_residual = sum(
                        phase[column] * (nodes[0][column] - phase_source[column])
                        for column in range(3)
                    )
                    amplitude = half_node_rms(nodes)
                    record = {
                        "iteration": iteration,
                        "period_time_decimal": str(period_time),
                        "matching_residual_decimal": str(matching),
                        "matching_residual": float(matching),
                        "phase_residual_decimal": str(abs(phase_residual)),
                        "phase_residual": float(abs(phase_residual)),
                        "half_node_rms_decimal": str(amplitude),
                        "half_node_rms": float(amplitude),
                    }
                    correction_history.append(record)
                    print(json.dumps(record, sort_keys=True), flush=True)
                    if max(matching, abs(phase_residual)) <= tolerance:
                        termination_reason = "converged"
                        break
                    if iteration == int(manifest["maximum_newton_updates"]):
                        break
                    corrections, period_delta = reduced_fixed_parameter_correction(
                        map_rows, phase, phase_residual
                    )
                    current_residual = max(matching, abs(phase_residual))
                    accepted = False
                    for factor_value in manifest["damping"]["factors"]:
                        factor = Decimal(str(factor_value))
                        trial_nodes = [
                            [
                                value + factor * delta
                                for value, delta in zip(node, correction)
                            ]
                            for node, correction in zip(nodes, corrections)
                        ]
                        trial_period = period_time + factor * period_delta
                        trial_rows = evaluate(
                            executor, trial_nodes, trial_period, target_a, manifest
                        )
                        trial_matching = max(
                            abs(value)
                            for row in trial_rows
                            for value in row["residual"]
                        )
                        trial_phase = abs(
                            sum(
                                phase[column]
                                * (trial_nodes[0][column] - phase_source[column])
                                for column in range(3)
                            )
                        )
                        trial_residual = max(trial_matching, trial_phase)
                        trial = {
                            "update": iteration + 1,
                            "factor": float(factor),
                            "matching_residual_decimal": str(trial_matching),
                            "matching_residual": float(trial_matching),
                            "phase_residual_decimal": str(trial_phase),
                            "phase_residual": float(trial_phase),
                            "residual_ratio": float(trial_residual / current_residual),
                        }
                        trial_history.append(trial)
                        print(json.dumps({"trial": trial}, sort_keys=True), flush=True)
                        if trial_is_acceptable(
                            current_residual,
                            trial_residual,
                            tolerance,
                            factor,
                            manifest["damping"],
                        ):
                            nodes = trial_nodes
                            period_time = trial_period
                            map_rows = trial_rows
                            accepted = True
                            break
                    if not accepted:
                        termination_reason = "backtracking_failed"
                        break
            else:
                bracket_left = bracket_right = None
                nodes = [[Decimal(value) for value in row] for row in source_rows[-1]["nodes_decimal"]]
                period_time = Decimal(source_rows[-1]["period_time_decimal"])
                interpolation_fraction = None
                correction_history = []
                trial_history = []
                map_rows = None
                termination_reason = "target_not_uniquely_bracketed"

        amplitude = half_node_rms(nodes)
        identity = phase_invariant_target_identity(nodes, target_nodes)
        spectrum = (
            transverse_spectrum(
                [row["transition"] for row in map_rows],
                manifest["cyclic_shifts"],
                int(manifest["decimal_digits"]),
            )
            if map_rows is not None
            else None
        )

    acceptance = manifest["acceptance"]
    continuation_correction = all(
        max(
            row["history"][-1]["matching_residual"],
            row["history"][-1]["phase_residual"],
            row["history"][-1]["arclength_residual"],
        )
        <= float(acceptance["maximum_residual"])
        for row in continued
    )
    checks = {
        "row_count": len(continued) == int(manifest["continuation_steps"]),
        "continuation_correction": continuation_correction,
        "target_bracket": len(brackets) == 1,
        "target_correction": bool(correction_history)
        and max(
            correction_history[-1]["matching_residual"],
            correction_history[-1]["phase_residual"],
        )
        <= float(acceptance["maximum_residual"]),
        "primitive": float(amplitude)
        >= float(acceptance["minimum_primitive_half_node_rms"]),
        "node_identity": identity["rms"]
        <= float(acceptance["maximum_target_node_rms"]),
        "period_identity": abs(float(period_time - target_period))
        <= float(acceptance["maximum_target_period_difference"]),
        "cyclic_spectrum": spectrum is not None
        and spectrum["cyclic_spread"] <= float(acceptance["maximum_cyclic_spread"]),
        "neutral_spectrum": spectrum is not None
        and spectrum["maximum_neutral_residual"]
        <= float(acceptance["maximum_neutral_residual"]),
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
        "method": manifest["method"],
        "steps_per_segment": steps,
        "source_secant_norm_decimal": str(secant_norm),
        "target_a_decimal": str(target_a),
        "target_period_decimal": str(target_period),
        "continuation_rows": continued,
        "target_bracket": (
            {
                "left_a_decimal": bracket_left["a_decimal"],
                "right_a_decimal": bracket_right["a_decimal"],
                "interpolation_fraction_decimal": str(interpolation_fraction),
            }
            if bracket_left is not None
            else None
        ),
        "correction_history": correction_history,
        "trial_history": trial_history,
        "termination_reason": termination_reason,
        "connected_a_decimal": str(target_a),
        "connected_period_decimal": str(period_time),
        "connected_half_node_rms_decimal": str(amplitude),
        "target_identity": identity,
        "target_period_difference": abs(float(period_time - target_period)),
        "spectrum": spectrum,
        "nodes_decimal": [[str(value) for value in row] for row in nodes],
        "checks": checks,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(checks.values()),
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    printed = {
        **output,
        "continuation_rows": [
            {key: value for key, value in row.items() if key != "nodes_decimal"}
            for row in continued
        ],
    }
    printed.pop("nodes_decimal")
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
