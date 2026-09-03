#!/usr/bin/env python3
"""Refine a Decimal period-1536 augmented bracket across resolutions."""

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
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from correct_jones_period768_decimal_parent import state_rhs
from refine_jones_period768_decimal_augmented import (
    convergence_ratio,
    correct_profile,
)


SCHEMA = "butterfly.jones-period1536-decimal-augmented-refinement-manifest.v1"


def line_identity(source_nodes, source_tangents, nodes, tangents) -> dict:
    source_nodes_float = np.asarray(
        [[float(value) for value in row] for row in source_nodes], dtype=float
    )
    nodes_float = np.asarray(
        [[float(value) for value in row] for row in nodes], dtype=float
    )
    source_tangents_float = np.asarray(
        [[float(value) for value in row] for row in source_tangents], dtype=float
    )
    tangents_float = np.asarray(
        [[float(value) for value in row] for row in tangents], dtype=float
    )
    denominators = np.linalg.norm(source_tangents_float, axis=1) * np.linalg.norm(
        tangents_float, axis=1
    )
    cosines = np.abs(
        np.sum(source_tangents_float * tangents_float, axis=1) / denominators
    )
    return {
        "maximum_node_displacement": float(
            np.max(np.abs(nodes_float - source_nodes_float))
        ),
        "minimum_tangent_line_cosine": float(np.min(cosines)),
        "median_tangent_line_cosine": float(np.median(cosines)),
        "base_tangent_line_cosine": float(cosines[0]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--pilot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported period-1536 Decimal refinement manifest")
    pilot_bytes = args.pilot.read_bytes()
    if sha256_bytes(pilot_bytes) != manifest["pilot_receipt_sha256"]:
        raise SystemExit("pilot receipt hash mismatch")
    pilot = json.loads(pilot_bytes)
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
        pilot_nodes = [
            [Decimal(value) for value in row] for row in pilot["nodes_decimal"]
        ]
        pilot_tangents = [
            [Decimal(value) for value in row]
            for row in pilot["tangent_nodes_decimal"]
        ]
        pilot_period = Decimal(pilot["period_time_decimal"])
        pilot_a = Decimal(pilot["corrected_a_decimal"])
        nodes = [row.copy() for row in pilot_nodes]
        tangents = [row.copy() for row in pilot_tangents]
        period_time = pilot_period
        parameter = pilot_a
        b = Decimal(str(manifest["fixed_b"]))
        c = Decimal(str(manifest["fixed_c"]))
        phase = state_rhs(nodes[0], parameter, b, c)
        phase_norm = sum(value * value for value in phase).sqrt()
        phase = [value / phase_norm for value in phase]
        profiles = [
            {
                "steps_per_segment": int(pilot["steps_per_segment"]),
                "converged": bool(pilot["checks"]["correction"]),
                "a_decimal": pilot["corrected_a_decimal"],
                "a": pilot["corrected_a"],
                "period_time_decimal": pilot["period_time_decimal"],
                "period_time": pilot["period_time"],
                "maximum_source_node_displacement": pilot[
                    "maximum_source_node_displacement"
                ],
                "maximum_source_tangent_displacement": pilot[
                    "maximum_source_tangent_displacement"
                ],
                "source_period_displacement": pilot[
                    "source_period_displacement"
                ],
                "half_node_rms_separation": pilot[
                    "half_node_rms_separation"
                ],
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
                    pilot_nodes,
                    pilot_tangents,
                    pilot_period,
                    phase,
                    b,
                    c,
                    manifest,
                    int(steps),
                )
                profiles.append(
                    {
                        key: value
                        for key, value in corrected.items()
                        if key not in {"nodes", "tangents", "period", "parameter"}
                    }
                )
                nodes = corrected["nodes"]
                tangents = corrected["tangents"]
                period_time = corrected["period"]
                parameter = corrected["parameter"]

        a_values = [Decimal(row["a_decimal"]) for row in profiles]
        period_values = [Decimal(row["period_time_decimal"]) for row in profiles]
        a_ratio = convergence_ratio(a_values)
        period_ratio = convergence_ratio(period_values)
        extrapolated_a = richardson(
            a_values[1], a_values[2], int(manifest["method_order"])
        )
        extrapolated_period = richardson(
            period_values[1], period_values[2], int(manifest["method_order"])
        )
        identity = line_identity(pilot_nodes, pilot_tangents, nodes, tangents)

    acceptance = manifest["acceptance"]
    lower_a, upper_a = map(Decimal, map(str, manifest["a_bounds"]))
    finest = profiles[-1]
    checks = {
        "correction": all(row["converged"] for row in profiles),
        "a_convergence": Decimal(str(acceptance["minimum_convergence_ratio"]))
        <= a_ratio
        <= Decimal(str(acceptance["maximum_convergence_ratio"])),
        "period_convergence": Decimal(
            str(acceptance["minimum_convergence_ratio"])
        )
        <= period_ratio
        <= Decimal(str(acceptance["maximum_convergence_ratio"])),
        "extrapolated_a_bounds": lower_a <= extrapolated_a <= upper_a,
        "node_identity": identity["maximum_node_displacement"]
        <= float(acceptance["maximum_node_displacement"]),
        "tangent_line_identity": identity["minimum_tangent_line_cosine"]
        >= float(acceptance["minimum_tangent_line_cosine"]),
        "primitive_half_separation": finest["half_node_rms_separation"]
        >= float(acceptance["minimum_half_node_rms_separation"]),
    }
    output = {
        "schema": "butterfly.jones-period1536-decimal-augmented-refinement-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
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
        "line_identity": identity,
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
