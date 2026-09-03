#!/usr/bin/env python3
"""Correct a long periodic parent with Decimal cyclic block elimination."""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, localcontext
from pathlib import Path

from audit_jones_period768_decimal_independent import rk_three_eighths
from audit_jones_period768_decimal_multiplier import (
    matmul,
    matvec,
    profile_spectrum,
    serializable_spectrum,
)
from audit_jones_period768_decimal_richardson import richardson
from audit_jones_period768_decimal_segments import dec, rk4
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period768-decimal-parent-correction-manifest.v1"
METHODS = {
    "classical_rk4": rk4,
    "rk4_three_eighths": rk_three_eighths,
}


def state_rhs(state, a, b, c):
    x, y, z = state
    return [-y - z, x + a * y, b + z * (x - c)]


def integrate_task(task):
    with localcontext() as context:
        context.prec = int(task["digits"])
        a, b, c = map(dec, (task["a"], task["b"], task["c"]))
        duration = Decimal(task["period_time"]) / Decimal(task["segment_count"])
        node = [Decimal(value) for value in task["node"]]
        identity = [
            Decimal(1), Decimal(0), Decimal(0),
            Decimal(0), Decimal(1), Decimal(0),
            Decimal(0), Decimal(0), Decimal(1),
        ]
        result = METHODS[task["method"]](
            node + identity,
            duration,
            int(task["steps"]),
            a,
            b,
            c,
        )
        return {
            "index": task["index"],
            "endpoint": [str(value) for value in result[:3]],
            "transition": [str(value) for value in result[3:]],
            "duration_column": [
                str(value / Decimal(task["segment_count"]))
                for value in state_rhs(result[:3], a, b, c)
            ],
        }


def solve_linear(matrix, right):
    size = len(right)
    rows = [list(matrix[index]) + [right[index]] for index in range(size)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(rows[row][column]))
        if rows[pivot][column] == 0:
            raise ArithmeticError("singular Decimal Newton system")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]
        rows[column] = [value / divisor for value in rows[column]]
        for row in range(size):
            if row == column:
                continue
            factor = rows[row][column]
            if factor == 0:
                continue
            rows[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(rows[row], rows[column])
            ]
    return [rows[row][-1] for row in range(size)]


def identity_matrix():
    return [
        Decimal(1), Decimal(0), Decimal(0),
        Decimal(0), Decimal(1), Decimal(0),
        Decimal(0), Decimal(0), Decimal(1),
    ]


def vector_add(*vectors):
    return [sum(values) for values in zip(*vectors)]


def vector_scale(vector, scalar):
    return [scalar * value for value in vector]


def evaluate(executor, nodes, period_time, manifest, steps, method):
    count = len(nodes)
    tasks = [
        {
            "index": index,
            "digits": manifest["decimal_digits"],
            "a": manifest["target_a"],
            "b": manifest["fixed_b"],
            "c": manifest["fixed_c"],
            "period_time": str(period_time),
            "segment_count": count,
            "node": [str(value) for value in node],
            "steps": steps,
            "method": method,
        }
        for index, node in enumerate(nodes)
    ]
    rows = list(executor.map(integrate_task, tasks, chunksize=1))
    rows.sort(key=lambda row: row["index"])
    transitions = [[Decimal(value) for value in row["transition"]] for row in rows]
    duration_columns = [
        [Decimal(value) for value in row["duration_column"]] for row in rows
    ]
    residuals = []
    for index, row in enumerate(rows):
        endpoint = [Decimal(value) for value in row["endpoint"]]
        residuals.append(
            [
                endpoint[column] - nodes[(index + 1) % count][column]
                for column in range(3)
            ]
        )
    return transitions, duration_columns, residuals


def newton_correction(transitions, duration_columns, residuals, phase, phase_residual):
    propagation = identity_matrix()
    period_column = [Decimal(0)] * 3
    forcing = [Decimal(0)] * 3
    for transition, duration_column, residual in zip(
        transitions, duration_columns, residuals
    ):
        propagation = matmul(transition, propagation)
        period_column = vector_add(
            matvec(transition, period_column), duration_column
        )
        forcing = vector_add(matvec(transition, forcing), residual)
    system = []
    identity = identity_matrix()
    for row in range(3):
        system.append(
            [
                propagation[3 * row + column] - identity[3 * row + column]
                for column in range(3)
            ]
            + [period_column[row]]
        )
    system.append(list(phase) + [Decimal(0)])
    solution = solve_linear(system, [-value for value in forcing] + [-phase_residual])
    state_correction = solution[:3]
    period_correction = solution[3]
    corrections = []
    current = state_correction
    for transition, duration_column, residual in zip(
        transitions, duration_columns, residuals
    ):
        corrections.append(current)
        current = vector_add(
            matvec(transition, current),
            vector_scale(duration_column, period_correction),
            residual,
        )
    return corrections, period_correction


def correct_profile(executor, source_nodes, source_period, phase, manifest, steps):
    nodes = [row.copy() for row in source_nodes]
    period_time = source_period
    tolerance = Decimal(str(manifest["acceptance"]["maximum_matching_residual"]))
    phase_tolerance = Decimal(str(manifest["acceptance"]["maximum_phase_residual"]))
    history = []
    transitions = None
    maximum_updates = int(manifest["maximum_newton_updates"])
    for iteration in range(maximum_updates + 1):
        transitions, duration_columns, residuals = evaluate(
            executor,
            nodes,
            period_time,
            manifest,
            steps,
            manifest["method"],
        )
        matching_residual = max(abs(value) for row in residuals for value in row)
        phase_residual = sum(
            phase[column] * (nodes[0][column] - source_nodes[0][column])
            for column in range(3)
        )
        history.append(
            {
                "iteration": iteration,
                "matching_residual_decimal": str(matching_residual),
                "matching_residual": float(matching_residual),
                "phase_residual_decimal": str(abs(phase_residual)),
                "phase_residual": float(abs(phase_residual)),
            }
        )
        if matching_residual <= tolerance and abs(phase_residual) <= phase_tolerance:
            break
        if iteration == maximum_updates:
            break
        corrections, period_correction = newton_correction(
            transitions,
            duration_columns,
            residuals,
            phase,
            phase_residual,
        )
        nodes = [
            vector_add(node, correction)
            for node, correction in zip(nodes, corrections)
        ]
        period_time += period_correction
    node_displacement = max(
        abs(value - source)
        for node, source_node in zip(nodes, source_nodes)
        for value, source in zip(node, source_node)
    )
    return {
        "converged": bool(
            history[-1]["matching_residual"] <= float(tolerance)
            and history[-1]["phase_residual"] <= float(phase_tolerance)
        ),
        "nodes": nodes,
        "period_time": period_time,
        "transitions": transitions,
        "history": history,
        "maximum_source_node_displacement": node_displacement,
        "source_period_displacement": abs(period_time - source_period),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--qualification", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported Decimal parent-correction manifest")
    qualification_bytes = args.qualification.read_bytes()
    audit_bytes = args.audit.read_bytes()
    if sha256_bytes(qualification_bytes) != manifest["qualification_receipt_sha256"]:
        raise SystemExit("qualification receipt hash mismatch")
    if sha256_bytes(audit_bytes) != manifest["audit_receipt_sha256"]:
        raise SystemExit("audit receipt hash mismatch")
    qualification = json.loads(qualification_bytes)
    audit = json.loads(audit_bytes)
    if qualification.get("schema") != manifest["qualification_schema"]:
        raise SystemExit("qualification schema mismatch")
    if audit.get("schema") != manifest["audit_schema"] or audit.get("passed"):
        raise SystemExit("bound parent-side audit is not the failed source")
    if list(name for name, passed in audit["checks"].items() if not passed) != ["stable_side"]:
        raise SystemExit("parent-side source did not fail only stable-side classification")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    parent = qualification["results"][manifest["qualification_solver"]][manifest["family"]]
    manifest["target_a"] = qualification["target_a"]
    manifest["fixed_b"] = qualification["fixed_b"]
    manifest["fixed_c"] = qualification["fixed_c"]
    started = time.perf_counter()
    with localcontext() as context:
        context.prec = int(manifest["decimal_digits"])
        source_nodes = [[dec(value) for value in row] for row in parent["nodes"]]
        source_period = dec(parent["period_time"])
        a, b, c = map(
            dec,
            (manifest["target_a"], manifest["fixed_b"], manifest["fixed_c"]),
        )
        phase = state_rhs(source_nodes[0], a, b, c)
        phase_norm = sum(value * value for value in phase).sqrt()
        phase = [value / phase_norm for value in phase]
        workers = min(int(manifest["workers"]), os.cpu_count() or 1)
        profiles = []
        with ProcessPoolExecutor(max_workers=workers) as executor:
            for steps in manifest["step_counts"]:
                corrected = correct_profile(
                    executor,
                    source_nodes,
                    source_period,
                    phase,
                    manifest,
                    int(steps),
                )
                spectrum = profile_spectrum(
                    corrected["transitions"], manifest["cyclic_shifts"], context.prec
                )
                profiles.append(
                    {
                        "steps_per_segment": int(steps),
                        "converged": corrected["converged"],
                        "period_time_decimal": str(corrected["period_time"]),
                        "period_time": float(corrected["period_time"]),
                        "maximum_source_node_displacement_decimal": str(
                            corrected["maximum_source_node_displacement"]
                        ),
                        "maximum_source_node_displacement": float(
                            corrected["maximum_source_node_displacement"]
                        ),
                        "source_period_displacement_decimal": str(
                            corrected["source_period_displacement"]
                        ),
                        "source_period_displacement": float(
                            corrected["source_period_displacement"]
                        ),
                        "history": corrected["history"],
                        "spectrum": serializable_spectrum(spectrum),
                    }
                )
        flip_values = [Decimal(row["spectrum"]["flip_median_decimal"]) for row in profiles]
        neutral_values = [
            Decimal(row["spectrum"]["neutral_median_decimal"]) for row in profiles
        ]
        raw_ratio = abs(
            (flip_values[0] - flip_values[1]) / (flip_values[1] - flip_values[2])
        )
        first_flip = richardson(flip_values[0], flip_values[1], manifest["method_order"])
        second_flip = richardson(flip_values[1], flip_values[2], manifest["method_order"])
        first_neutral = richardson(
            neutral_values[0], neutral_values[1], manifest["method_order"]
        )
        second_neutral = richardson(
            neutral_values[1], neutral_values[2], manifest["method_order"]
        )

    acceptance = manifest["acceptance"]
    checks = {
        "correction": all(row["converged"] for row in profiles),
        "source_neighborhood": all(
            row["maximum_source_node_displacement"]
            <= float(acceptance["maximum_source_node_displacement"])
            and row["source_period_displacement"]
            <= float(acceptance["maximum_source_period_displacement"])
            for row in profiles
        ),
        "raw_convergence": float(acceptance["minimum_raw_convergence_ratio"])
        <= float(raw_ratio)
        <= float(acceptance["maximum_raw_convergence_ratio"]),
        "richardson_flip_convergence": float(abs(first_flip - second_flip))
        <= float(acceptance["maximum_successive_richardson_flip_difference"]),
        "richardson_neutral_convergence": float(abs(first_neutral - second_neutral))
        <= float(acceptance["maximum_successive_richardson_neutral_difference"]),
        "neutral": float(abs(second_neutral - Decimal(1)))
        <= float(acceptance["maximum_extrapolated_neutral_residual"]),
        "cyclic": profiles[-1]["spectrum"]["flip_cyclic_spread"]
        <= float(acceptance["maximum_fine_cyclic_spread"]),
        "characteristic": profiles[-1]["spectrum"]["maximum_characteristic_residual"]
        <= float(acceptance["maximum_fine_characteristic_residual"]),
    }
    output = {
        "schema": "butterfly.jones-period768-decimal-parent-correction-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "qualification_receipt_sha256": sha256_bytes(qualification_bytes),
        "audit_receipt_sha256": sha256_bytes(audit_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "workers": workers,
        },
        "target_a": qualification["target_a"],
        "event_a": qualification["event_a"],
        "a_offset": qualification["a_offset"],
        "segment_count": len(source_nodes),
        "decimal_digits": manifest["decimal_digits"],
        "method": manifest["method"],
        "profiles": profiles,
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
