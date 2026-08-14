#!/usr/bin/env python3
"""Correct the candidate period-768 flip as a Decimal augmented orbit."""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, localcontext
from pathlib import Path

from audit_jones_period768_decimal_multiplier import matmul, matvec
from correct_jones_period768_decimal_parent import (
    identity_matrix,
    solve_linear,
    state_rhs,
    vector_add,
    vector_scale,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period768-decimal-augmented-correction-manifest.v1"


def augmented_rhs(value, a, b, c):
    """Rössler orbit and exact first/second variational equations in Decimal."""

    x, y, z = value[:3]
    transition = value[3:12]
    parameter_state = value[12:15]
    tangent = value[15:18]
    state_tangent = value[18:27]
    parameter_tangent = value[27:30]

    def jacobian_action(vector):
        vx, vy, vz = vector
        return [-vy - vz, vx + a * vy, z * vx + (x - c) * vz]

    derivative = [-y - z, x + a * y, b + z * (x - c)]
    for column in range(3):
        derivative.extend(
            jacobian_action([transition[column], transition[3 + column], transition[6 + column]])
        )
    # The loop above emits columns; restore row-major order used by matvec.
    transition_derivative = derivative[3:]
    derivative[3:] = [
        transition_derivative[3 * column + row]
        for row in range(3)
        for column in range(3)
    ]

    parameter_state_derivative = jacobian_action(parameter_state)
    parameter_state_derivative[1] += y
    derivative.extend(parameter_state_derivative)

    tangent_derivative = jacobian_action(tangent)
    derivative.extend(tangent_derivative)

    state_tangent_derivative = []
    for column in range(3):
        transported_column = [
            state_tangent[column],
            state_tangent[3 + column],
            state_tangent[6 + column],
        ]
        column_derivative = jacobian_action(transported_column)
        column_derivative[2] += (
            transition[6 + column] * tangent[0]
            + transition[column] * tangent[2]
        )
        state_tangent_derivative.extend(column_derivative)
    derivative.extend(
        [
            state_tangent_derivative[3 * column + row]
            for row in range(3)
            for column in range(3)
        ]
    )

    parameter_tangent_derivative = jacobian_action(parameter_tangent)
    parameter_tangent_derivative[1] += tangent[1]
    parameter_tangent_derivative[2] += (
        parameter_state[2] * tangent[0]
        + parameter_state[0] * tangent[2]
    )
    derivative.extend(parameter_tangent_derivative)
    return derivative


def rk4_augmented(initial, duration, steps, a, b, c):
    value = initial.copy()
    step = duration / Decimal(steps)
    half = step / Decimal(2)
    sixth = step / Decimal(6)
    for _ in range(steps):
        k1 = augmented_rhs(value, a, b, c)
        k2 = augmented_rhs(
            [v + half * k for v, k in zip(value, k1)], a, b, c
        )
        k3 = augmented_rhs(
            [v + half * k for v, k in zip(value, k2)], a, b, c
        )
        k4 = augmented_rhs(
            [v + step * k for v, k in zip(value, k3)], a, b, c
        )
        value = [
            v + sixth * (d1 + Decimal(2) * d2 + Decimal(2) * d3 + d4)
            for v, d1, d2, d3, d4 in zip(value, k1, k2, k3, k4)
        ]
    return value


def integrate_task(task):
    with localcontext() as context:
        context.prec = int(task["digits"])
        a = Decimal(task["a"])
        b = Decimal(task["b"])
        c = Decimal(task["c"])
        count = int(task["segment_count"])
        duration = Decimal(task["period_time"]) / Decimal(count)
        node = [Decimal(value) for value in task["node"]]
        tangent = [Decimal(value) for value in task["tangent"]]
        zeros = [Decimal(0)] * 3
        initial = node + identity_matrix() + zeros + tangent + [Decimal(0)] * 12
        result = rk4_augmented(
            initial, duration, int(task["steps_per_segment"]), a, b, c
        )
        endpoint = result[:3]
        transported = result[15:18]
        tangent_time = matvec(
            [
                Decimal(0), Decimal(-1), Decimal(-1),
                Decimal(1), a, Decimal(0),
                endpoint[2], Decimal(0), endpoint[0] - c,
            ],
            transported,
        )
        return {
            "index": int(task["index"]),
            "endpoint": [str(value) for value in endpoint],
            "transition": [str(value) for value in result[3:12]],
            "parameter_state": [str(value) for value in result[12:15]],
            "transported": [str(value) for value in transported],
            "state_tangent": [str(value) for value in result[18:27]],
            "parameter_tangent": [str(value) for value in result[27:30]],
            "orbit_time": [str(value / Decimal(count)) for value in state_rhs(endpoint, a, b, c)],
            "tangent_time": [str(value / Decimal(count)) for value in tangent_time],
        }


def evaluate(executor, nodes, tangents, period_time, a, b, c, manifest):
    count = len(nodes)
    tasks = [
        {
            "index": index,
            "digits": manifest["decimal_digits"],
            "a": str(a),
            "b": str(b),
            "c": str(c),
            "period_time": str(period_time),
            "segment_count": count,
            "node": [str(value) for value in nodes[index]],
            "tangent": [str(value) for value in tangents[index]],
            "steps_per_segment": manifest["steps_per_segment"],
        }
        for index in range(count)
    ]
    rows = list(executor.map(integrate_task, tasks, chunksize=1))
    rows.sort(key=lambda row: row["index"])
    evaluated = []
    for index, row in enumerate(rows):
        next_index = (index + 1) % count
        endpoint = [Decimal(value) for value in row["endpoint"]]
        transported = [Decimal(value) for value in row["transported"]]
        expected_tangent = tangents[next_index]
        tangent_sign = Decimal(-1) if next_index == 0 else Decimal(1)
        evaluated.append(
            {
                "transition": [Decimal(value) for value in row["transition"]],
                "parameter_state": [Decimal(value) for value in row["parameter_state"]],
                "state_tangent": [Decimal(value) for value in row["state_tangent"]],
                "parameter_tangent": [Decimal(value) for value in row["parameter_tangent"]],
                "orbit_time": [Decimal(value) for value in row["orbit_time"]],
                "tangent_time": [Decimal(value) for value in row["tangent_time"]],
                "orbit_residual": [
                    endpoint[column] - nodes[next_index][column]
                    for column in range(3)
                ],
                "tangent_residual": [
                    transported[column] - tangent_sign * expected_tangent[column]
                    for column in range(3)
                ],
            }
        )
    return evaluated


def _matrix_add(left, right):
    return [a + b for a, b in zip(left, right)]


def _matrix_column_add(matrix, column, vector):
    result = matrix.copy()
    for row, value in enumerate(vector):
        result[8 * row + column] += value
    return result


def augmented_newton_correction(rows, phase, phase_residual, tangent0, norm_residual):
    """Eliminate all cyclic blocks to an 8-by-8 augmented Newton system."""

    state_map = [Decimal(0)] * 24
    tangent_map = [Decimal(0)] * 24
    for index in range(3):
        state_map[8 * index + index] = Decimal(1)
        tangent_map[8 * index + 3 + index] = Decimal(1)
    state_forcing = [Decimal(0)] * 3
    tangent_forcing = [Decimal(0)] * 3

    def left_multiply(matrix3, matrix3x8):
        return [
            sum(matrix3[3 * row + inner] * matrix3x8[8 * inner + column] for inner in range(3))
            for row in range(3)
            for column in range(8)
        ]

    for row in rows:
        next_state_map = left_multiply(row["transition"], state_map)
        next_state_map = _matrix_column_add(next_state_map, 6, row["orbit_time"])
        next_state_map = _matrix_column_add(next_state_map, 7, row["parameter_state"])
        next_state_forcing = vector_add(
            matvec(row["transition"], state_forcing), row["orbit_residual"]
        )

        next_tangent_map = _matrix_add(
            left_multiply(row["transition"], tangent_map),
            left_multiply(row["state_tangent"], state_map),
        )
        next_tangent_map = _matrix_column_add(next_tangent_map, 6, row["tangent_time"])
        next_tangent_map = _matrix_column_add(next_tangent_map, 7, row["parameter_tangent"])
        next_tangent_forcing = vector_add(
            matvec(row["transition"], tangent_forcing),
            matvec(row["state_tangent"], state_forcing),
            row["tangent_residual"],
        )
        state_map, state_forcing = next_state_map, next_state_forcing
        tangent_map, tangent_forcing = (
            next_tangent_map,
            next_tangent_forcing,
        )

    system = []
    for row in range(3):
        equation = state_map[8 * row : 8 * row + 8]
        equation[row] -= Decimal(1)
        system.append(equation)
    for row in range(3):
        equation = tangent_map[8 * row : 8 * row + 8]
        equation[3 + row] += Decimal(1)
        system.append(equation)
    system.append(list(phase) + [Decimal(0)] * 5)
    system.append(
        [Decimal(0)] * 3
        + [Decimal(2) * value for value in tangent0]
        + [Decimal(0)] * 2
    )
    base = solve_linear(
        system,
        [-value for value in state_forcing]
        + [-value for value in tangent_forcing]
        + [-phase_residual, -norm_residual],
    )

    state_corrections = []
    tangent_corrections = []
    state_correction = base[:3]
    tangent_correction = base[3:6]
    period_correction = base[6]
    parameter_correction = base[7]
    for row in rows:
        state_corrections.append(state_correction)
        tangent_corrections.append(tangent_correction)
        next_state_correction = vector_add(
            matvec(row["transition"], state_correction),
            vector_scale(row["orbit_time"], period_correction),
            vector_scale(row["parameter_state"], parameter_correction),
            row["orbit_residual"],
        )
        next_tangent_correction = vector_add(
            matvec(row["transition"], tangent_correction),
            matvec(row["state_tangent"], state_correction),
            vector_scale(row["tangent_time"], period_correction),
            vector_scale(row["parameter_tangent"], parameter_correction),
            row["tangent_residual"],
        )
        state_correction = next_state_correction
        tangent_correction = next_tangent_correction
    return state_corrections, tangent_corrections, period_correction, parameter_correction


def maximum_residual(rows, key):
    return max(abs(value) for row in rows for value in row[key])


def rms_half_node_separation(nodes):
    half = len(nodes) // 2
    squared = sum(
        (nodes[index + half][column] - nodes[index][column]) ** 2
        for index in range(half)
        for column in range(3)
    )
    return (squared / Decimal(3 * half)).sqrt()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--orbit-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported Decimal augmented-correction manifest")
    event_bytes = args.event.read_bytes()
    audit_bytes = args.orbit_audit.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    if sha256_bytes(audit_bytes) != manifest["orbit_audit_receipt_sha256"]:
        raise SystemExit("orbit-audit receipt hash mismatch")
    event = json.loads(event_bytes)
    audit = json.loads(audit_bytes)
    if event.get("schema") != manifest["event_schema"] or event.get("passed"):
        raise SystemExit("bound event is not the failed source")
    if list(name for name, passed in event["checks"].items() if not passed) != ["independent_flip"]:
        raise SystemExit("source event did not preserve only the independent-flip failure")
    if audit.get("schema") != manifest["orbit_audit_schema"] or audit.get("passed"):
        raise SystemExit("bound orbit correction is not the failed source")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    started = time.perf_counter()
    with localcontext() as context:
        context.prec = int(manifest["decimal_digits"])
        nodes = [[Decimal(repr(float(value))) for value in row] for row in event["nodes"]]
        tangents = [
            [Decimal(repr(float(value))) for value in row]
            for row in event["tangent_nodes"]
        ]
        source_nodes = [row.copy() for row in nodes]
        source_tangents = [row.copy() for row in tangents]
        period_time = Decimal(repr(float(event["period_time"])))
        source_period = period_time
        parameter = Decimal(repr(float(event["corrected_a"])))
        source_parameter = parameter
        b = Decimal(repr(float(event["fixed_b"])))
        c = Decimal(repr(float(event["fixed_c"])))
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
                    executor, nodes, tangents, period_time, parameter, b, c, manifest
                )
                orbit_residual = maximum_residual(rows, "orbit_residual")
                tangent_residual = maximum_residual(rows, "tangent_residual")
                phase_residual = sum(
                    phase[column] * (nodes[0][column] - source_nodes[0][column])
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
            abs(value - source)
            for node, source_node in zip(nodes, source_nodes)
            for value, source in zip(node, source_node)
        )
        maximum_tangent_displacement = max(
            abs(value - source)
            for tangent, source_tangent in zip(tangents, source_tangents)
            for value, source in zip(tangent, source_tangent)
        )
        period_displacement = abs(period_time - source_period)
        parameter_displacement = abs(parameter - source_parameter)
        half_node_rms = rms_half_node_separation(nodes)

    acceptance = manifest["acceptance"]
    lower_a, upper_a = map(Decimal, map(str, manifest["a_bounds"]))
    checks = {
        "correction": max(
            history[-1]["orbit_residual"],
            history[-1]["tangent_residual"],
            history[-1]["phase_residual"],
            history[-1]["normalization_residual"],
        ) <= float(acceptance["maximum_augmented_residual"]),
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
        "schema": "butterfly.jones-period768-decimal-augmented-correction-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "orbit_audit_receipt_sha256": sha256_bytes(audit_bytes),
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
    print(json.dumps({key: value for key, value in output.items() if key not in {"nodes_decimal", "tangent_nodes_decimal"}}, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
