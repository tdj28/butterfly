#!/usr/bin/env python3
"""Rephase the exact eighth-event orbit onto the connected daughter section."""

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

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from continue_jones_period1536_decimal_child import half_node_rms
from correct_jones_period1536_decimal_target import (
    reduced_fixed_parameter_correction,
    trial_is_acceptable,
)
from correct_jones_period768_decimal_parent import state_rhs
from switch_jones_period1536_decimal_child import evaluate, transverse_spectrum
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period1536-decimal-phase-registration-manifest.v1"


def direct_node_rms(left, right) -> float:
    left_array = np.asarray([[float(value) for value in row] for row in left])
    right_array = np.asarray([[float(value) for value in row] for row in right])
    if left_array.shape != right_array.shape:
        raise ValueError("node shapes differ")
    return float(np.sqrt(np.mean((left_array - right_array) ** 2)))


def roll_nodes(nodes: list, shift: int) -> list:
    shift %= len(nodes)
    return nodes[-shift:] + nodes[:-shift] if shift else list(nodes)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--connection", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    connection_bytes = args.connection.read_bytes()
    target_bytes = args.target.read_bytes()
    manifest = json.loads(manifest_bytes)
    connection = json.loads(connection_bytes)
    target = json.loads(target_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported phase-registration manifest")
    if sha256_bytes(connection_bytes) != manifest["connection_receipt_sha256"]:
        raise SystemExit("connection receipt hash mismatch")
    if sha256_bytes(target_bytes) != manifest["target_receipt_sha256"]:
        raise SystemExit("target receipt hash mismatch")
    if connection.get("schema") != manifest["connection_schema"] or connection.get("passed"):
        raise SystemExit("preserved failed connection receipt required")
    failed = sorted(name for name, passed in connection["checks"].items() if not passed)
    if failed != ["node_identity"]:
        raise SystemExit("connection failure pattern changed")
    if target.get("schema") != manifest["target_schema"] or target.get("passed") is not True:
        raise SystemExit("passed event target required")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    connected_nodes = [
        [Decimal(value) for value in row] for row in connection["nodes_decimal"]
    ]
    shift = int(connection["target_identity"]["node_shift"])
    shifted_target = roll_nodes(target["nodes_decimal"], shift)
    nodes = [[Decimal(value) for value in row] for row in shifted_target]
    steps = int(manifest["steps_per_segment"])
    profiles = [
        profile
        for profile in target["profiles"]
        if int(profile["steps_per_segment"]) == steps
    ]
    if len(profiles) != 1:
        raise SystemExit("target profile is not uniquely selected")
    profile = profiles[0]
    parameter = Decimal(profile["a_decimal"])
    period_time = Decimal(profile["period_time_decimal"])
    connected_period = Decimal(connection["connected_period_decimal"])
    b = Decimal(str(manifest["fixed_b"]))
    c = Decimal(str(manifest["fixed_c"]))
    tolerance = Decimal(str(manifest["acceptance"]["maximum_residual"]))
    started = time.perf_counter()
    history = []
    trial_history = []
    termination_reason = "maximum_updates"

    with localcontext() as context:
        context.prec = int(manifest["decimal_digits"])
        phase = state_rhs(connected_nodes[0], parameter, b, c)
        phase_norm = sum(value * value for value in phase).sqrt()
        phase = [value / phase_norm for value in phase]
        workers = min(int(manifest["workers"]), os.cpu_count() or 1)
        with ProcessPoolExecutor(max_workers=workers) as executor:
            rows = evaluate(executor, nodes, period_time, parameter, manifest)
            for iteration in range(int(manifest["maximum_newton_updates"]) + 1):
                matching = max(abs(value) for row in rows for value in row["residual"])
                phase_residual = sum(
                    phase[column] * (nodes[0][column] - connected_nodes[0][column])
                    for column in range(3)
                )
                amplitude = half_node_rms(nodes)
                identity = direct_node_rms(nodes, connected_nodes)
                record = {
                    "iteration": iteration,
                    "period_time_decimal": str(period_time),
                    "matching_residual_decimal": str(matching),
                    "matching_residual": float(matching),
                    "phase_residual_decimal": str(abs(phase_residual)),
                    "phase_residual": float(abs(phase_residual)),
                    "half_node_rms_decimal": str(amplitude),
                    "half_node_rms": float(amplitude),
                    "direct_node_rms": identity,
                }
                history.append(record)
                print(json.dumps(record, sort_keys=True), flush=True)
                if max(matching, abs(phase_residual)) <= tolerance:
                    termination_reason = "converged"
                    break
                if iteration == int(manifest["maximum_newton_updates"]):
                    break
                corrections, period_delta = reduced_fixed_parameter_correction(
                    rows, phase, phase_residual
                )
                current_residual = max(matching, abs(phase_residual))
                accepted = False
                for factor_value in manifest["damping"]["factors"]:
                    factor = Decimal(str(factor_value))
                    trial_nodes = [
                        [value + factor * delta for value, delta in zip(node, correction)]
                        for node, correction in zip(nodes, corrections)
                    ]
                    trial_period = period_time + factor * period_delta
                    trial_rows = evaluate(executor, trial_nodes, trial_period, parameter, manifest)
                    trial_matching = max(
                        abs(value) for row in trial_rows for value in row["residual"]
                    )
                    trial_phase = abs(
                        sum(
                            phase[column]
                            * (trial_nodes[0][column] - connected_nodes[0][column])
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
                        "direct_node_rms": direct_node_rms(trial_nodes, connected_nodes),
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
                        rows = trial_rows
                        accepted = True
                        break
                if not accepted:
                    termination_reason = "backtracking_failed"
                    break
        amplitude = half_node_rms(nodes)
        identity = direct_node_rms(nodes, connected_nodes)
        spectrum = transverse_spectrum(
            [row["transition"] for row in rows],
            manifest["cyclic_shifts"],
            int(manifest["decimal_digits"]),
        )

    acceptance = manifest["acceptance"]
    checks = {
        "correction": max(history[-1]["matching_residual"], history[-1]["phase_residual"])
        <= float(acceptance["maximum_residual"]),
        "primitive": float(amplitude) >= float(acceptance["minimum_primitive_half_node_rms"]),
        "shared_phase_identity": identity <= float(acceptance["maximum_shared_phase_node_rms"]),
        "period_identity": abs(float(period_time - connected_period))
        <= float(acceptance["maximum_period_difference"]),
        "cyclic_spectrum": spectrum["cyclic_spread"]
        <= float(acceptance["maximum_cyclic_spread"]),
        "neutral_spectrum": spectrum["maximum_neutral_residual"]
        <= float(acceptance["maximum_neutral_residual"]),
    }
    output = {
        "schema": manifest["output_schema"],
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "connection_receipt_sha256": sha256_bytes(connection_bytes),
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
        "target_a_decimal": str(parameter),
        "source_node_shift": shift,
        "initial_phase_residual": history[0]["phase_residual"],
        "initial_direct_node_rms": history[0]["direct_node_rms"],
        "period_time_decimal": str(period_time),
        "connected_period_difference": abs(float(period_time - connected_period)),
        "half_node_rms_decimal": str(amplitude),
        "shared_phase_node_rms": identity,
        "spectrum": spectrum,
        "history": history,
        "trial_history": trial_history,
        "termination_reason": termination_reason,
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
