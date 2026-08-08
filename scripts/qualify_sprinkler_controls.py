#!/usr/bin/env python3
"""Qualify a reference sprinkler sampler on two published Rössler saddles."""
from __future__ import annotations

import argparse
import json
import platform
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import scipy

from butterfly import (
    OrbitLabel,
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    classify_fundamental_period,
    collect_crossings,
    cycle_crossing_distances,
    infer_return_map_branches,
    sprinkler_survivors,
    survivor_return_pairs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def _captured_by_crossings(states, cycle, capture):
    distances = cycle_crossing_distances(
        states,
        cycle,
        coordinate_axes=tuple(capture["coordinate_axes"]),
        coordinate_scales=tuple(capture["coordinate_scales"]),
    )
    streak = 0
    for distance in distances:
        streak = streak + 1 if distance <= capture["radius"] else 0
        if streak >= capture["required_crossings"]:
            return True
    return False


def _evenly_spaced(values, count):
    values = np.asarray(values, dtype=int)
    if len(values) <= count:
        return values
    indices = np.rint(np.linspace(0, len(values) - 1, count)).astype(int)
    return values[indices]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.sprinkler-controls-manifest.v1":
        raise SystemExit("unsupported sprinkler-controls manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    solver = SolverConfig(**manifest["reference_solver"])
    fixed = manifest["fixed_parameters"]
    capture = manifest["capture"]
    ensemble = manifest["ensemble"]
    acceptance = manifest["acceptance"]
    rows = []
    started = time.perf_counter()
    for case in manifest["cases"]:
        parameters = RosslerParameters(
            a=float(case["a"]), b=float(fixed["b"]), c=float(fixed["c"])
        )
        section = barrio_rossler_section(parameters)
        cycle_crossings = collect_crossings(
            parameters,
            manifest["cycle_initial_state"],
            section,
            transient=float(manifest["cycle_reference"]["transient"]),
            observation_horizon=float(
                manifest["cycle_reference"]["observation_horizon"]
            ),
            max_crossings=int(manifest["cycle_reference"]["max_crossings"]),
            config=solver,
        )
        cycle_classification = classify_fundamental_period(
            cycle_crossings.states, **manifest["cycle_reference"]["recurrence"]
        )
        cycle_period = int(case["stable_period"])
        cycle = cycle_crossings.states[-cycle_period:]

        y_values = np.linspace(
            ensemble["y_range"][0], ensemble["y_range"][1], ensemble["y_count"]
        )
        z_values = np.linspace(
            ensemble["z_range"][0], ensemble["z_range"][1], ensemble["z_count"]
        )
        y_grid, z_grid = np.meshgrid(y_values, z_values, indexing="ij")
        initial = np.column_stack(
            (
                np.full(y_grid.size, section.offset),
                y_grid.ravel(),
                z_grid.ravel(),
            )
        )
        result = sprinkler_survivors(
            parameters,
            initial,
            section,
            cycle,
            dt=float(ensemble["dt"]),
            horizon=float(ensemble["horizon"]),
            capture_coordinate_axes=tuple(capture["coordinate_axes"]),
            capture_coordinate_scales=tuple(capture["coordinate_scales"]),
            capture_radius=float(capture["radius"]),
            required_capture_crossings=int(capture["required_crossings"]),
            checkpoint_times=ensemble["checkpoint_times"],
            midpoint_window=tuple(ensemble["midpoint_window"]),
            escape_radius=float(ensemble["escape_radius"]),
        )

        coordinates = {}
        for coordinate in manifest["coordinates"]:
            source_values, target_values = survivor_return_pairs(
                result, int(coordinate["axis"])
            )
            if len(source_values) >= acceptance["minimum_return_pairs"]:
                oracle = asdict(
                    infer_return_map_branches(
                        source_values, target_values, **manifest["oracle"]
                    )
                )
            else:
                oracle = {
                    "resolved": False,
                    "branch_count": None,
                    "critical_points": (),
                    "conditional_spread_ratio": None,
                    "domain_coverage": None,
                    "bootstrap_consensus": None,
                    "bootstrap_counts": (),
                    "reason": "insufficient survivor return pairs",
                }
            coordinates[coordinate["name"]] = {
                "pair_count": len(source_values),
                "source": source_values.tolist(),
                "target": target_values.tolist(),
                "oracle": oracle,
            }

        captured_ids = np.flatnonzero(np.isfinite(result.capture_times))
        audit_ids = np.concatenate(
            (
                _evenly_spaced(
                    result.survivor_ids, manifest["precision_audit"]["per_class"]
                ),
                _evenly_spaced(
                    captured_ids, manifest["precision_audit"]["per_class"]
                ),
            )
        )
        expected_captured = np.isin(audit_ids, captured_ids)
        audit_rows = []
        for trajectory_id, expected in zip(
            audit_ids, expected_captured, strict=True
        ):
            audit_crossings = collect_crossings(
                parameters,
                initial[trajectory_id],
                section,
                transient=0.0,
                observation_horizon=float(ensemble["horizon"]),
                max_crossings=int(manifest["precision_audit"]["max_crossings"]),
                config=solver,
            )
            observed = _captured_by_crossings(
                audit_crossings.states, cycle, capture
            )
            audit_rows.append(
                {
                    "trajectory_id": int(trajectory_id),
                    "fixed_step_captured": bool(expected),
                    "dop853_captured": observed,
                    "match": bool(expected == observed),
                    "crossing_count": len(audit_crossings.times),
                    "integration_success": audit_crossings.integration_success,
                }
            )
        expected_branch_count = int(case["expected_saddle_branch_count"])
        case_passed = bool(
            cycle_crossings.integration_success
            and cycle_classification.label == OrbitLabel.PERIODIC
            and cycle_classification.fundamental_period == cycle_period
            and not np.any(result.failed)
            and len(result.survivor_ids) >= acceptance["minimum_final_survivors"]
            and result.survivor_counts[-1] < result.survivor_counts[0]
            and all(
                value["pair_count"] >= acceptance["minimum_return_pairs"]
                and value["oracle"]["resolved"]
                and value["oracle"]["branch_count"] == expected_branch_count
                for value in coordinates.values()
            )
            and sum(row["match"] for row in audit_rows)
            / max(len(audit_rows), 1)
            >= acceptance["minimum_precision_audit_agreement"]
        )
        row = {
            "id": case["id"],
            "parameters": asdict(parameters),
            "expected_saddle_branch_count": expected_branch_count,
            "cycle_reference": {
                "classification": asdict(cycle_classification),
                "crossing_count": len(cycle_crossings.times),
                "states": cycle.tolist(),
            },
            "ensemble_size": len(initial),
            "survivor_counts": result.survivor_counts.tolist(),
            "final_survivor_count": len(result.survivor_ids),
            "failed_count": int(np.count_nonzero(result.failed)),
            "midpoint_crossing_count": len(result.midpoint_times),
            "coordinates": coordinates,
            "precision_audit": audit_rows,
            "passed": case_passed,
        }
        rows.append(row)
        print(
            json.dumps(
                {
                    "id": row["id"],
                    "survivor_counts": row["survivor_counts"],
                    "midpoint_crossing_count": row["midpoint_crossing_count"],
                    "branch_counts": {
                        name: value["oracle"]["branch_count"]
                        for name, value in coordinates.items()
                    },
                    "precision_matches": sum(
                        audit["match"] for audit in audit_rows
                    ),
                    "precision_total": len(audit_rows),
                    "passed": case_passed,
                },
                sort_keys=True,
            ),
            flush=True,
        )

    output = {
        "schema": "butterfly.sprinkler-controls.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "elapsed_seconds": time.perf_counter() - started,
        "cases": rows,
        "passed": all(row["passed"] for row in rows),
    }
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {
                "experiment_id": manifest["experiment_id"],
                "passed": output["passed"],
                "elapsed_seconds": output["elapsed_seconds"],
                "output": str(args.output),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
