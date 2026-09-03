#!/usr/bin/env python3
"""Refine the Decimal augmented period-768 candidate across resolutions."""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, localcontext
from pathlib import Path

from audit_jones_period768_decimal_richardson import richardson
from correct_jones_period768_decimal_augmented import (
    augmented_newton_correction,
    evaluate,
    maximum_residual,
    rms_half_node_separation,
)
from correct_jones_period768_decimal_parent import state_rhs, vector_add
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-period768-decimal-augmented-refinement-manifest.v1"


def correct_profile(
    executor,
    seed_nodes,
    seed_tangents,
    seed_period,
    seed_a,
    source_nodes,
    source_tangents,
    source_period,
    phase,
    b,
    c,
    manifest,
    steps_per_segment,
):
    nodes = [row.copy() for row in seed_nodes]
    tangents = [row.copy() for row in seed_tangents]
    period_time = seed_period
    parameter = seed_a
    profile_manifest = dict(manifest)
    profile_manifest["steps_per_segment"] = int(steps_per_segment)
    tolerance = Decimal(str(manifest["acceptance"]["maximum_augmented_residual"]))
    history = []
    for iteration in range(int(manifest["maximum_newton_updates"]) + 1):
        rows = evaluate(
            executor,
            nodes,
            tangents,
            period_time,
            parameter,
            b,
            c,
            profile_manifest,
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
        print(
            json.dumps(
                {
                    "steps_per_segment": int(steps_per_segment),
                    **history[-1],
                },
                sort_keys=True,
            ),
            flush=True,
        )
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
            vector_add(node, delta) for node, delta in zip(nodes, state_delta)
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
    return {
        "steps_per_segment": int(steps_per_segment),
        "converged": max(
            history[-1]["orbit_residual"],
            history[-1]["tangent_residual"],
            history[-1]["phase_residual"],
            history[-1]["normalization_residual"],
        )
        <= float(tolerance),
        "a_decimal": str(parameter),
        "a": float(parameter),
        "period_time_decimal": str(period_time),
        "period_time": float(period_time),
        "history": history,
        "maximum_source_node_displacement_decimal": str(maximum_node_displacement),
        "maximum_source_node_displacement": float(maximum_node_displacement),
        "maximum_source_tangent_displacement_decimal": str(maximum_tangent_displacement),
        "maximum_source_tangent_displacement": float(maximum_tangent_displacement),
        "source_period_displacement_decimal": str(abs(period_time - source_period)),
        "source_period_displacement": float(abs(period_time - source_period)),
        "half_node_rms_separation_decimal": str(rms_half_node_separation(nodes)),
        "half_node_rms_separation": float(rms_half_node_separation(nodes)),
        "nodes": nodes,
        "tangents": tangents,
        "period": period_time,
        "parameter": parameter,
    }


def convergence_ratio(values):
    return abs((values[0] - values[1]) / (values[1] - values[2]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--pilot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported Decimal augmented-refinement manifest")
    event_bytes = args.event.read_bytes()
    pilot_bytes = args.pilot.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    if sha256_bytes(pilot_bytes) != manifest["pilot_receipt_sha256"]:
        raise SystemExit("pilot receipt hash mismatch")
    event = json.loads(event_bytes)
    pilot = json.loads(pilot_bytes)
    if event.get("schema") != manifest["event_schema"] or event.get("passed"):
        raise SystemExit("bound event is not the failed source")
    if pilot.get("schema") != manifest["pilot_schema"] or pilot.get("passed"):
        raise SystemExit("bound pilot is not the preserved failed source")
    if pilot.get("checks") != {
        "a_bounds": False,
        "correction": True,
        "primitive_half_separation": True,
        "source_neighborhood": False,
    }:
        raise SystemExit("pilot failure pattern changed")
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
            [Decimal(repr(float(value))) for value in row] for row in event["nodes"]
        ]
        source_tangents = [
            [Decimal(repr(float(value))) for value in row]
            for row in event["tangent_nodes"]
        ]
        source_period = Decimal(repr(float(event["period_time"])))
        source_a = Decimal(repr(float(event["corrected_a"])))
        b = Decimal(repr(float(event["fixed_b"])))
        c = Decimal(repr(float(event["fixed_c"])))
        phase = state_rhs(source_nodes[0], source_a, b, c)
        phase_norm = sum(value * value for value in phase).sqrt()
        phase = [value / phase_norm for value in phase]

        nodes = [[Decimal(value) for value in row] for row in pilot["nodes_decimal"]]
        tangents = [
            [Decimal(value) for value in row]
            for row in pilot["tangent_nodes_decimal"]
        ]
        period_time = Decimal(pilot["period_time_decimal"])
        parameter = Decimal(pilot["corrected_a_decimal"])
        profiles = [
            {
                "steps_per_segment": int(pilot["steps_per_segment"]),
                "converged": bool(pilot["checks"]["correction"]),
                "a_decimal": pilot["corrected_a_decimal"],
                "a": pilot["corrected_a"],
                "period_time_decimal": pilot["period_time_decimal"],
                "period_time": pilot["period_time"],
                "maximum_source_node_displacement": pilot["maximum_source_node_displacement"],
                "maximum_source_tangent_displacement": pilot["maximum_source_tangent_displacement"],
                "source_period_displacement": pilot["source_period_displacement"],
                "half_node_rms_separation": pilot["half_node_rms_separation"],
                "history": pilot["history"],
            }
        ]
        workers = min(int(manifest["workers"]), os.cpu_count() or 1)
        with ProcessPoolExecutor(max_workers=workers) as executor:
            for steps in manifest["new_step_counts"]:
                corrected = correct_profile(
                    executor,
                    nodes,
                    tangents,
                    period_time,
                    parameter,
                    source_nodes,
                    source_tangents,
                    source_period,
                    phase,
                    b,
                    c,
                    manifest,
                    int(steps),
                )
                profiles.append(
                    {key: value for key, value in corrected.items() if key not in {"nodes", "tangents", "period", "parameter"}}
                )
                nodes = corrected["nodes"]
                tangents = corrected["tangents"]
                period_time = corrected["period"]
                parameter = corrected["parameter"]

        a_values = [Decimal(row["a_decimal"]) for row in profiles]
        period_values = [Decimal(row["period_time_decimal"]) for row in profiles]
        a_ratio = convergence_ratio(a_values)
        period_ratio = convergence_ratio(period_values)
        extrapolated_a = richardson(a_values[1], a_values[2], manifest["method_order"])
        extrapolated_period = richardson(
            period_values[1], period_values[2], manifest["method_order"]
        )

    acceptance = manifest["acceptance"]
    lower_a, upper_a = map(Decimal, map(str, manifest["a_bounds"]))
    finest = profiles[-1]
    checks = {
        "correction": all(row["converged"] for row in profiles),
        "a_convergence": Decimal(str(acceptance["minimum_convergence_ratio"]))
        <= a_ratio
        <= Decimal(str(acceptance["maximum_convergence_ratio"])),
        "period_convergence": Decimal(str(acceptance["minimum_convergence_ratio"]))
        <= period_ratio
        <= Decimal(str(acceptance["maximum_convergence_ratio"])),
        "finest_a_bounds": lower_a <= Decimal(finest["a_decimal"]) <= upper_a,
        "extrapolated_a_bounds": lower_a <= extrapolated_a <= upper_a,
        "source_neighborhood": (
            finest["maximum_source_node_displacement"]
            <= float(acceptance["maximum_source_node_displacement"])
            and finest["maximum_source_tangent_displacement"]
            <= float(acceptance["maximum_source_tangent_displacement"])
            and finest["source_period_displacement"]
            <= float(acceptance["maximum_source_period_displacement"])
        ),
        "primitive_half_separation": finest["half_node_rms_separation"]
        >= float(acceptance["minimum_half_node_rms_separation"]),
    }
    output = {
        "schema": "butterfly.jones-period768-decimal-augmented-refinement-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "pilot_receipt_sha256": sha256_bytes(pilot_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "workers": workers,
        },
        "decimal_digits": manifest["decimal_digits"],
        "method": manifest["method"],
        "method_order": manifest["method_order"],
        "step_counts": [row["steps_per_segment"] for row in profiles],
        "profiles": profiles,
        "a_convergence_ratio_decimal": str(a_ratio),
        "a_convergence_ratio": float(a_ratio),
        "period_convergence_ratio_decimal": str(period_ratio),
        "period_convergence_ratio": float(period_ratio),
        "extrapolated_a_decimal": str(extrapolated_a),
        "extrapolated_a": float(extrapolated_a),
        "extrapolated_period_decimal": str(extrapolated_period),
        "extrapolated_period": float(extrapolated_period),
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
