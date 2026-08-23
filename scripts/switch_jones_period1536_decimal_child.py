#!/usr/bin/env python3
"""Switch the exact Decimal period-768 event onto its immediate daughter."""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, localcontext
from pathlib import Path

from audit_jones_period768_decimal_multiplier import (
    characteristic_root,
    determinant,
    matmul,
    matvec,
)
from correct_jones_period768_decimal_parent import (
    identity_matrix,
    solve_linear,
    state_rhs,
    vector_add,
    vector_scale,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period1536-decimal-child-switch-manifest.v1"


def state_parameter_rhs(value, a, b, c):
    """Rössler state, state transition, and a-sensitivity equations."""

    x, y, z = value[:3]
    transition = value[3:12]
    parameter_state = value[12:15]

    def jacobian_action(vector):
        vx, vy, vz = vector
        return [-vy - vz, vx + a * vy, z * vx + (x - c) * vz]

    derivative = [-y - z, x + a * y, b + z * (x - c)]
    columns = []
    for column in range(3):
        columns.extend(
            jacobian_action(
                [
                    transition[column],
                    transition[3 + column],
                    transition[6 + column],
                ]
            )
        )
    derivative.extend(
        [columns[3 * column + row] for row in range(3) for column in range(3)]
    )
    parameter_derivative = jacobian_action(parameter_state)
    parameter_derivative[1] += y
    derivative.extend(parameter_derivative)
    return derivative


def rk_three_eighths(initial, duration, steps, a, b, c):
    value = initial.copy()
    step = duration / Decimal(steps)
    third = step / Decimal(3)
    eighth = step / Decimal(8)
    for _ in range(steps):
        k1 = state_parameter_rhs(value, a, b, c)
        k2 = state_parameter_rhs(
            [v + third * d1 for v, d1 in zip(value, k1)], a, b, c
        )
        k3 = state_parameter_rhs(
            [
                v + step * (-d1 / Decimal(3) + d2)
                for v, d1, d2 in zip(value, k1, k2)
            ],
            a,
            b,
            c,
        )
        k4 = state_parameter_rhs(
            [
                v + step * (d1 - d2 + d3)
                for v, d1, d2, d3 in zip(value, k1, k2, k3)
            ],
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
        a = Decimal(task["a"])
        b = Decimal(task["b"])
        c = Decimal(task["c"])
        count = int(task["segment_count"])
        duration = Decimal(task["period_time"]) / Decimal(count)
        node = [Decimal(value) for value in task["node"]]
        initial = node + identity_matrix() + [Decimal(0)] * 3
        result = rk_three_eighths(
            initial, duration, int(task["steps_per_segment"]), a, b, c
        )
        endpoint = result[:3]
        return {
            "index": int(task["index"]),
            "endpoint": [str(value) for value in endpoint],
            "transition": [str(value) for value in result[3:12]],
            "parameter_state": [str(value) for value in result[12:15]],
            "period_state": [
                str(value / Decimal(count)) for value in state_rhs(endpoint, a, b, c)
            ],
        }


def evaluate(executor, nodes, period_time, parameter, manifest):
    count = len(nodes)
    tasks = [
        {
            "index": index,
            "digits": manifest["decimal_digits"],
            "a": str(parameter),
            "b": str(manifest["fixed_b"]),
            "c": str(manifest["fixed_c"]),
            "period_time": str(period_time),
            "segment_count": count,
            "node": [str(value) for value in node],
            "steps_per_segment": manifest["steps_per_segment"],
        }
        for index, node in enumerate(nodes)
    ]
    rows = list(executor.map(integrate_task, tasks, chunksize=1))
    rows.sort(key=lambda row: row["index"])
    evaluated = []
    for index, row in enumerate(rows):
        endpoint = [Decimal(value) for value in row["endpoint"]]
        evaluated.append(
            {
                "transition": [Decimal(value) for value in row["transition"]],
                "parameter_state": [
                    Decimal(value) for value in row["parameter_state"]
                ],
                "period_state": [Decimal(value) for value in row["period_state"]],
                "residual": [
                    endpoint[column] - nodes[(index + 1) % count][column]
                    for column in range(3)
                ],
            }
        )
    return evaluated


def phase_fixed_child_tangent(nodes, tangents, parameter, b, c):
    """Return the normalized doubled anti-periodic mode and phase direction."""

    phase = state_rhs(nodes[0], parameter, b, c)
    phase_norm = sum(value * value for value in phase).sqrt()
    phase = [value / phase_norm for value in phase]
    doubled_nodes = nodes + [row.copy() for row in nodes]
    child_mode = tangents + [[-value for value in row] for row in tangents]
    flow_mode = [state_rhs(row, parameter, b, c) for row in doubled_nodes]
    coefficient = -sum(
        phase[column] * child_mode[0][column] for column in range(3)
    ) / sum(phase[column] * flow_mode[0][column] for column in range(3))
    mode = [
        [child + coefficient * flow for child, flow in zip(child_row, flow_row)]
        for child_row, flow_row in zip(child_mode, flow_mode)
    ]
    norm = sum(value * value for row in mode for value in row).sqrt()
    return [[value / norm for value in row] for row in mode], phase, coefficient


def reduced_newton_correction(rows, phase, phase_residual, tangent, arclength):
    """Eliminate cyclic node blocks to a five-variable Newton system."""

    mapping = [Decimal(0)] * 15
    for index in range(3):
        mapping[5 * index + index] = Decimal(1)
    forcing = [Decimal(0)] * 3
    maps = []
    forcings = []

    def left_multiply(matrix3, matrix3x5):
        return [
            sum(
                matrix3[3 * row + inner] * matrix3x5[5 * inner + column]
                for inner in range(3)
            )
            for row in range(3)
            for column in range(5)
        ]

    for row in rows:
        maps.append(mapping)
        forcings.append(forcing)
        next_mapping = left_multiply(row["transition"], mapping)
        for state_row in range(3):
            next_mapping[5 * state_row + 3] += row["period_state"][state_row]
            next_mapping[5 * state_row + 4] += row["parameter_state"][state_row]
        next_forcing = vector_add(
            matvec(row["transition"], forcing), row["residual"]
        )
        mapping, forcing = next_mapping, next_forcing

    system = []
    for row in range(3):
        equation = mapping[5 * row : 5 * row + 5]
        equation[row] -= Decimal(1)
        system.append(equation)
    system.append(list(phase) + [Decimal(0), Decimal(0)])
    arclength_row = [Decimal(0)] * 5
    arclength_forcing = Decimal(0)
    for tangent_row, node_map, node_forcing in zip(tangent, maps, forcings):
        for column in range(5):
            arclength_row[column] += sum(
                tangent_row[state_row] * node_map[5 * state_row + column]
                for state_row in range(3)
            )
        arclength_forcing += sum(
            tangent_row[state_row] * node_forcing[state_row]
            for state_row in range(3)
        )
    system.append(arclength_row)
    base = solve_linear(
        system,
        [-value for value in forcing]
        + [-phase_residual, -arclength - arclength_forcing],
    )
    corrections = [
        [
            sum(node_map[5 * row + column] * base[column] for column in range(5))
            + node_forcing[row]
            for row in range(3)
        ]
        for node_map, node_forcing in zip(maps, forcings)
    ]
    return corrections, base[3], base[4]


def transverse_spectrum(transitions, shifts, digits):
    identity = identity_matrix()
    products = []
    for shift in shifts:
        monodromy = identity
        ordered = transitions[shift:] + transitions[:shift]
        for transition in ordered:
            monodromy = matmul(transition, monodromy)
        neutral, residual, _ = characteristic_root(monodromy, Decimal(1), digits)
        trace = monodromy[0] + monodromy[4] + monodromy[8]
        remaining_sum = trace - neutral
        remaining_product = determinant(monodromy) / neutral
        discriminant = remaining_sum * remaining_sum - Decimal(4) * remaining_product
        if discriminant < 0:
            raise ArithmeticError("complex transverse pair is unsupported")
        root = discriminant.sqrt()
        transverse = [
            (remaining_sum + root) / Decimal(2),
            (remaining_sum - root) / Decimal(2),
        ]
        dominant = max(transverse, key=abs)
        products.append(
            {
                "cyclic_shift": int(shift),
                "neutral_decimal": str(neutral),
                "neutral_residual": float(abs(neutral - Decimal(1))),
                "characteristic_residual": float(residual),
                "transverse_decimal": [str(value) for value in transverse],
                "dominant_transverse_decimal": str(dominant),
                "dominant_transverse_modulus": float(abs(dominant)),
            }
        )
    moduli = [row["dominant_transverse_modulus"] for row in products]
    return {
        "products": products,
        "dominant_modulus": sum(moduli) / len(moduli),
        "cyclic_spread": max(moduli) - min(moduli),
        "maximum_neutral_residual": max(
            row["neutral_residual"] for row in products
        ),
        "maximum_characteristic_residual": max(
            row["characteristic_residual"] for row in products
        ),
    }


def correct_candidate(executor, event_nodes, event_period, event_a, tangent, phase, direction, step, manifest):
    signed_tangent = [
        [Decimal(direction) * value for value in row] for row in tangent
    ]
    predictor = [
        [node_value + Decimal(str(step)) * tangent_value for node_value, tangent_value in zip(node, tangent_row)]
        for node, tangent_row in zip(event_nodes, signed_tangent)
    ]
    nodes = [row.copy() for row in predictor]
    period_time = event_period * Decimal(2)
    parameter = event_a
    tolerance = Decimal(str(manifest["acceptance"]["maximum_matching_residual"]))
    history = []
    rows = None
    for iteration in range(int(manifest["maximum_newton_updates"]) + 1):
        rows = evaluate(executor, nodes, period_time, parameter, manifest)
        matching = max(abs(value) for row in rows for value in row["residual"])
        phase_residual = sum(
            phase[column] * (nodes[0][column] - event_nodes[0][column])
            for column in range(3)
        )
        arclength = sum(
            tangent_value * (node_value - predictor_value)
            for node, predictor_node, tangent_row in zip(nodes, predictor, signed_tangent)
            for node_value, predictor_value, tangent_value in zip(
                node, predictor_node, tangent_row
            )
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
        print(
            json.dumps(
                {**history[-1], "step_length": step, "direction": direction},
                sort_keys=True,
            ),
            flush=True,
        )
        if max(matching, abs(phase_residual), abs(arclength)) <= tolerance:
            break
        if iteration == int(manifest["maximum_newton_updates"]):
            break
        corrections, period_delta, parameter_delta = reduced_newton_correction(
            rows, phase, phase_residual, signed_tangent, arclength
        )
        nodes = [
            vector_add(node, correction)
            for node, correction in zip(nodes, corrections)
        ]
        period_time += period_delta
        parameter += parameter_delta

    half = len(nodes) // 2
    half_rms = (
        sum(
            (nodes[index + half][column] - nodes[index][column]) ** 2
            for index in range(half)
            for column in range(3)
        )
        / Decimal(3 * half)
    ).sqrt()
    transitions = [row["transition"] for row in rows]
    spectrum = transverse_spectrum(
        transitions, manifest["cyclic_shifts"], int(manifest["decimal_digits"])
    )
    return {
        "step_length": float(step),
        "direction": int(direction),
        "history": history,
        "a_decimal": str(parameter),
        "a": float(parameter),
        "parameter_displacement_decimal": str(parameter - event_a),
        "parameter_displacement": float(parameter - event_a),
        "period_time_decimal": str(period_time),
        "period_time": float(period_time),
        "period_ratio": float(period_time / event_period),
        "half_node_rms_decimal": str(half_rms),
        "half_node_rms": float(half_rms),
        "spectrum": spectrum,
        "nodes_decimal": [[str(value) for value in row] for row in nodes],
    }


def scaling_exponent(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["step_length"], []).append(row)
    ordered = sorted(grouped)
    amplitudes = [
        sum(row["half_node_rms"] for row in grouped[step]) / len(grouped[step])
        for step in ordered
    ]
    displacements = [
        sum(abs(row["parameter_displacement"]) for row in grouped[step])
        / len(grouped[step])
        for step in ordered
    ]
    exponent = math.log(displacements[-1] / displacements[0]) / math.log(
        amplitudes[-1] / amplitudes[0]
    )
    return {
        "step_lengths": ordered,
        "mean_half_node_rms": amplitudes,
        "mean_absolute_parameter_displacement": displacements,
        "parameter_amplitude_exponent": exponent,
    }


def selected_event_profile(event: dict, steps_per_segment: int) -> dict:
    """Select the exact discrete event profile bound to the requested map."""

    profiles = event.get("profiles")
    if profiles is None and "profile" in event:
        profiles = [event["profile"]]
    selected = [
        row
        for row in profiles or []
        if int(row["steps_per_segment"]) == int(steps_per_segment)
    ]
    if len(selected) != 1:
        raise ValueError("event profile is not uniquely selected")
    return selected[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--criticality-audit", type=Path, required=True)
    parser.add_argument("--nomination", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    event_bytes = args.event.read_bytes()
    audit_bytes = args.criticality_audit.read_bytes()
    manifest = json.loads(manifest_bytes)
    event = json.loads(event_bytes)
    audit = json.loads(audit_bytes)
    nomination_bytes = None
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported Decimal child-switch manifest")
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    if sha256_bytes(audit_bytes) != manifest["criticality_audit_receipt_sha256"]:
        raise SystemExit("criticality audit receipt hash mismatch")
    if event.get("schema") != manifest["event_schema"] or not event.get("passed"):
        raise SystemExit("a passed Decimal event is required")
    if (
        audit.get("schema") != manifest["criticality_audit_schema"]
        or audit.get("passed")
        or audit.get("parent_classification") != "stable"
        or audit.get("child_classification") != "stable"
        or [name for name, passed in audit["checks"].items() if not passed]
        != ["resolved_criticality"]
    ):
        raise SystemExit("the preserved stable/stable audit is required")
    if "nomination_receipt_sha256" in manifest:
        if args.nomination is None:
            raise SystemExit("the bound lower-resolution nomination is required")
        nomination_bytes = args.nomination.read_bytes()
        if sha256_bytes(nomination_bytes) != manifest["nomination_receipt_sha256"]:
            raise SystemExit("nomination receipt hash mismatch")
        nomination = json.loads(nomination_bytes)
        if (
            nomination.get("schema") != manifest["nomination_schema"]
            or not nomination.get("passed")
            or nomination.get("branch_side") != "lower_a"
            or nomination.get("local_criticality_classification")
            != "supercritical"
        ):
            raise SystemExit("the bound supercritical nomination changed")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    try:
        profile = selected_event_profile(event, int(manifest["steps_per_segment"]))
    except ValueError as error:
        raise SystemExit(str(error)) from error
    started = time.perf_counter()
    with localcontext() as context:
        context.prec = int(manifest["decimal_digits"])
        parent_nodes = [
            [Decimal(value) for value in row] for row in event["nodes_decimal"]
        ]
        parent_tangents = [
            [Decimal(value) for value in row]
            for row in event["tangent_nodes_decimal"]
        ]
        event_period = Decimal(profile["period_time_decimal"])
        event_a = Decimal(profile["a_decimal"])
        b = Decimal(str(manifest["fixed_b"]))
        c = Decimal(str(manifest["fixed_c"]))
        tangent, phase, coefficient = phase_fixed_child_tangent(
            parent_nodes, parent_tangents, event_a, b, c
        )
        event_nodes = parent_nodes + [row.copy() for row in parent_nodes]
        workers = min(int(manifest["workers"]), os.cpu_count() or 1)
        candidates = []
        with ProcessPoolExecutor(max_workers=workers) as executor:
            for step in manifest["step_lengths"]:
                for direction in manifest["directions"]:
                    candidates.append(
                        correct_candidate(
                            executor,
                            event_nodes,
                            event_period,
                            event_a,
                            tangent,
                            phase,
                            int(direction),
                            float(step),
                            manifest,
                        )
                    )

    scaling = scaling_exponent(candidates)
    acceptance = manifest["acceptance"]
    displacements = [row["parameter_displacement"] for row in candidates]
    same_side = all(value > 0.0 for value in displacements) or all(
        value < 0.0 for value in displacements
    )
    side = "higher_a" if all(value > 0.0 for value in displacements) else (
        "lower_a" if all(value < 0.0 for value in displacements) else "mixed"
    )
    local_criticality = (
        "subcritical"
        if side == manifest["parent_stable_side"]
        else "supercritical" if side in {"higher_a", "lower_a"} else "unresolved"
    )
    expected_child_stability = (
        "unstable" if local_criticality == "subcritical" else "stable"
    )
    child_stabilities = [
        "stable"
        if row["spectrum"]["dominant_modulus"]
        <= 1.0 - float(acceptance["stability_margin"])
        else "unstable"
        if row["spectrum"]["dominant_modulus"]
        >= 1.0 + float(acceptance["stability_margin"])
        else "neutral"
        for row in candidates
    ]
    paired_groups = {}
    for row in candidates:
        paired_groups.setdefault(row["step_length"], []).append(row)
    maximum_direction_a_relative_spread = max(
        (max(abs(row["parameter_displacement"]) for row in group)
         - min(abs(row["parameter_displacement"]) for row in group))
        / max(abs(row["parameter_displacement"]) for row in group)
        for group in paired_groups.values()
    )
    maximum_direction_amplitude_relative_spread = max(
        (max(row["half_node_rms"] for row in group)
         - min(row["half_node_rms"] for row in group))
        / max(row["half_node_rms"] for row in group)
        for group in paired_groups.values()
    )
    checks = {
        "correction": all(
            max(
                row["history"][-1]["matching_residual"],
                row["history"][-1]["phase_residual"],
                row["history"][-1]["arclength_residual"],
            )
            <= float(acceptance["maximum_matching_residual"])
            for row in candidates
        ),
        "primitive": min(row["half_node_rms"] for row in candidates)
        >= float(acceptance["minimum_half_node_rms"]),
        "parameter_displacement": min(abs(value) for value in displacements)
        >= float(acceptance["minimum_parameter_displacement"])
        and max(abs(value) for value in displacements)
        <= float(acceptance["maximum_parameter_displacement"]),
        "same_side": same_side,
        "direction_a_agreement": maximum_direction_a_relative_spread
        <= float(acceptance["maximum_direction_relative_spread"]),
        "direction_amplitude_agreement": maximum_direction_amplitude_relative_spread
        <= float(acceptance["maximum_direction_relative_spread"]),
        "quadratic_opening": float(acceptance["minimum_scaling_exponent"])
        <= scaling["parameter_amplitude_exponent"]
        <= float(acceptance["maximum_scaling_exponent"]),
        "period_ratio": max(abs(row["period_ratio"] - 2.0) for row in candidates)
        <= float(acceptance["maximum_period_ratio_error"]),
        "cyclic_spectrum": max(row["spectrum"]["cyclic_spread"] for row in candidates)
        <= float(acceptance["maximum_cyclic_spread"]),
        "neutral_spectrum": max(
            row["spectrum"]["maximum_neutral_residual"] for row in candidates
        ) <= float(acceptance["maximum_neutral_residual"]),
        "child_stability": all(
            value == expected_child_stability for value in child_stabilities
        ),
        "resolved_criticality": local_criticality in {"supercritical", "subcritical"},
    }
    output = {
        "schema": manifest["output_schema"],
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "criticality_audit_receipt_sha256": sha256_bytes(audit_bytes),
        "nomination_receipt_sha256": (
            sha256_bytes(nomination_bytes) if nomination_bytes is not None else None
        ),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "workers": workers,
        },
        "decimal_digits": manifest["decimal_digits"],
        "method": "rk4_three_eighths",
        "steps_per_segment": manifest["steps_per_segment"],
        "fixed_b": manifest["fixed_b"],
        "fixed_c": manifest["fixed_c"],
        "event_a_decimal": str(event_a),
        "event_period_decimal": str(event_period),
        "phase_fix_coefficient_decimal": str(coefficient),
        "candidates": candidates,
        "scaling": scaling,
        "branch_side": side,
        "parent_stable_side": manifest["parent_stable_side"],
        "child_stabilities": child_stabilities,
        "local_criticality_classification": local_criticality,
        "maximum_direction_a_relative_spread": maximum_direction_a_relative_spread,
        "maximum_direction_amplitude_relative_spread": maximum_direction_amplitude_relative_spread,
        "checks": checks,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(checks.values()),
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    printed = {**output, "candidates": [
        {key: value for key, value in row.items() if key != "nodes_decimal"}
        for row in candidates
    ]}
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
