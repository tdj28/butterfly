#!/usr/bin/env python3
"""Extend the independent augmented event to 8,192 RK4 3/8 steps."""

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

from audit_jones_period768_decimal_richardson import richardson
from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from multiple_shooting_core import base_system
from correct_jones_period768_decimal_parent import state_rhs
from refine_jones_period768_decimal_augmented import (
    convergence_ratio,
    correct_profile,
)
from switch_augmented_flip_child import phase_fixed_child_tangent
from switch_jones_period12_segmented_child import doubled_event_variables


SCHEMA = "butterfly.jones-period768-decimal-augmented-8192-manifest.v1"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--independent", type=Path, required=True)
    parser.add_argument("--switch", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported 8192-step augmented manifest")
    independent_bytes = args.independent.read_bytes()
    switch_bytes = args.switch.read_bytes()
    if sha256_bytes(independent_bytes) != manifest["independent_receipt_sha256"]:
        raise SystemExit("independent receipt hash mismatch")
    if sha256_bytes(switch_bytes) != manifest["switch_receipt_sha256"]:
        raise SystemExit("switch receipt hash mismatch")
    independent = json.loads(independent_bytes)
    switch = json.loads(switch_bytes)
    if (
        independent.get("schema") != manifest["independent_schema"]
        or not independent.get("passed")
    ):
        raise SystemExit("bound independent event is not passed")
    if switch.get("schema") != manifest["switch_schema"] or switch.get("passed"):
        raise SystemExit("bound switch is not the preserved failed source")
    if not (
        len(switch.get("accepted_candidates", [])) == 6
        and switch["event_matching_residual"]
        > float(manifest["acceptance"]["maximum_dop853_event_matching_residual"])
        and switch["secondary_null_residual"]
        <= float(manifest["acceptance"]["maximum_secondary_null_residual"])
    ):
        raise SystemExit("switch failure pattern changed")
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
        source_nodes = [
            [Decimal(value) for value in row]
            for row in independent["nodes_decimal"]
        ]
        source_tangents = [
            [Decimal(value) for value in row]
            for row in independent["tangent_nodes_decimal"]
        ]
        source_profile = independent["profiles"][-1]
        source_period = Decimal(source_profile["period_time_decimal"])
        source_a = Decimal(source_profile["a_decimal"])
        b = Decimal(str(manifest["fixed_b"]))
        c = Decimal(str(manifest["fixed_c"]))
        phase = state_rhs(source_nodes[0], source_a, b, c)
        phase_norm = sum(value * value for value in phase).sqrt()
        phase = [value / phase_norm for value in phase]

        workers = min(int(manifest["workers"]), os.cpu_count() or 1)
        with ProcessPoolExecutor(max_workers=workers) as executor:
            corrected = correct_profile(
                executor,
                source_nodes,
                source_tangents,
                source_period,
                source_a,
                source_nodes,
                source_tangents,
                source_period,
                phase,
                b,
                c,
                manifest,
                int(manifest["steps_per_segment"]),
            )
        nodes = corrected["nodes"]
        tangents = corrected["tangents"]
        period_time = corrected["period"]
        parameter = corrected["parameter"]
        previous_profiles = independent["profiles"][-2:]
        a_values = [Decimal(row["a_decimal"]) for row in previous_profiles] + [
            parameter
        ]
        period_values = [
            Decimal(row["period_time_decimal"]) for row in previous_profiles
        ] + [period_time]
        a_ratio = convergence_ratio(a_values)
        period_ratio = convergence_ratio(period_values)
        extrapolated_a = richardson(
            a_values[1], a_values[2], manifest["method_order"]
        )
        extrapolated_period = richardson(
            period_values[1], period_values[2], manifest["method_order"]
        )
        previous_extrapolated_a = Decimal(independent["extrapolated_a_decimal"])
        previous_extrapolated_period = Decimal(
            independent["extrapolated_period_decimal"]
        )

    event = {
        "nodes": [[float(value) for value in row] for row in nodes],
        "tangent_nodes": [[float(value) for value in row] for row in tangents],
        "period_time": float(period_time),
        "corrected_a": float(parameter),
    }
    event_variables = doubled_event_variables(event)
    solver = SolverConfig(**manifest["dop853_solver"])
    parameters = RosslerParameters(
        a=float(parameter), b=float(manifest["fixed_b"]), c=float(manifest["fixed_c"])
    )
    dop_phase = rossler_rhs(0.0, event_variables[:3], parameters)
    dop_phase /= np.linalg.norm(dop_phase)
    event_residual, event_jacobian = base_system(
        event_variables,
        segment_count=2 * len(nodes),
        a=None,
        c=float(manifest["fixed_c"]),
        phase=dop_phase,
        phase_reference=event_variables[:3],
        solver=solver,
        continuation_parameter="a",
        fixed_b=float(manifest["fixed_b"]),
        sparse_jacobian=True,
    )
    secondary_tangent, phase_coefficient = phase_fixed_child_tangent(
        event, parameters, dop_phase
    )
    event_matching_residual = float(np.linalg.norm(event_residual[:-1]))
    secondary_null_residual = float(np.linalg.norm(event_jacobian @ secondary_tangent))

    acceptance = manifest["acceptance"]
    lower_a, upper_a = map(Decimal, map(str, manifest["a_bounds"]))
    checks = {
        "correction": corrected["converged"],
        "a_convergence": float(acceptance["minimum_convergence_ratio"])
        <= float(a_ratio)
        <= float(acceptance["maximum_convergence_ratio"]),
        "period_convergence": float(acceptance["minimum_convergence_ratio"])
        <= float(period_ratio)
        <= float(acceptance["maximum_convergence_ratio"]),
        "richardson_a": abs(extrapolated_a - previous_extrapolated_a)
        <= Decimal(str(acceptance["maximum_successive_richardson_a_difference"])),
        "richardson_period": abs(extrapolated_period - previous_extrapolated_period)
        <= Decimal(
            str(acceptance["maximum_successive_richardson_period_difference"])
        ),
        "a_bounds": lower_a <= parameter <= upper_a and lower_a <= extrapolated_a <= upper_a,
        "source_neighborhood": (
            corrected["maximum_source_node_displacement"]
            <= float(acceptance["maximum_source_node_displacement"])
            and corrected["maximum_source_tangent_displacement"]
            <= float(acceptance["maximum_source_tangent_displacement"])
            and corrected["source_period_displacement"]
            <= float(acceptance["maximum_source_period_displacement"])
        ),
        "primitive_half_separation": corrected["half_node_rms_separation"]
        >= float(acceptance["minimum_half_node_rms_separation"]),
        "dop853_event_matching": event_matching_residual
        <= float(acceptance["maximum_dop853_event_matching_residual"]),
        "secondary_null": secondary_null_residual
        <= float(acceptance["maximum_secondary_null_residual"]),
    }
    output = {
        "schema": "butterfly.jones-period768-decimal-augmented-8192-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "independent_receipt_sha256": sha256_bytes(independent_bytes),
        "switch_receipt_sha256": sha256_bytes(switch_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "workers": workers,
        },
        "decimal_digits": manifest["decimal_digits"],
        "method": manifest["method"],
        "steps_per_segment": manifest["steps_per_segment"],
        "profile": {
            key: value
            for key, value in corrected.items()
            if key not in {"nodes", "tangents", "period", "parameter"}
        },
        "a_increment_convergence_ratio_decimal": str(a_ratio),
        "a_increment_convergence_ratio": float(a_ratio),
        "period_increment_convergence_ratio_decimal": str(period_ratio),
        "period_increment_convergence_ratio": float(period_ratio),
        "extrapolated_a_decimal": str(extrapolated_a),
        "extrapolated_a": float(extrapolated_a),
        "successive_richardson_a_difference": float(
            abs(extrapolated_a - previous_extrapolated_a)
        ),
        "extrapolated_period_decimal": str(extrapolated_period),
        "extrapolated_period": float(extrapolated_period),
        "successive_richardson_period_difference": float(
            abs(extrapolated_period - previous_extrapolated_period)
        ),
        "dop853_event_matching_residual": event_matching_residual,
        "secondary_null_residual": secondary_null_residual,
        "phase_fix_coefficient": phase_coefficient,
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
            {key: value for key, value in output.items() if key not in {"nodes_decimal", "tangent_nodes_decimal"}},
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
