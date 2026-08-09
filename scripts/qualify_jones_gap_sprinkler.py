#!/usr/bin/env python3
"""Fill the EXP-180 Jones-section support hole with a survivor cloud."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import scipy

from butterfly import (
    OrbitLabel,
    PoincareSection,
    RosslerParameters,
    SolverConfig,
    classify_fundamental_period,
    collect_crossings,
    cycle_crossing_distances,
    infer_local_critical_point_robust,
    infer_return_map_branches_robust,
    legacy_rossler_section,
    sprinkler_survivors,
    survivor_return_pairs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-gap-sprinkler-manifest.v1"


def _section(parameters: RosslerParameters) -> PoincareSection:
    base = legacy_rossler_section(parameters)
    return PoincareSection(
        normal=base.normal,
        offset=base.offset,
        direction=-1,
        gate_axis=base.gate_axis,
        gate_upper=base.gate_upper,
        name="legacy-small-equilibrium-half-plane:negative",
    )


def _captured_by_crossings(states, reference, capture) -> bool:
    distances = cycle_crossing_distances(
        states,
        reference,
        coordinate_axes=tuple(capture["coordinate_axes"]),
        coordinate_scales=tuple(capture["coordinate_scales"]),
    )
    streak = 0
    for distance in distances:
        streak = streak + 1 if distance <= float(capture["radius"]) else 0
        if streak >= int(capture["required_crossings"]):
            return True
    return False


def _evenly_spaced(values, count):
    values = np.asarray(values, dtype=int)
    if len(values) <= count:
        return values
    indices = np.rint(np.linspace(0, len(values) - 1, count)).astype(int)
    return values[indices]


def _physical_local_result(source_values, local_result, prediction) -> dict:
    lower = float(np.min(source_values))
    upper = float(np.max(source_values))
    normalized = local_result["normalized_location"]
    physical = (
        lower + float(normalized) * (upper - lower)
        if normalized is not None
        else None
    )
    error = (
        abs(physical - float(prediction["physical_location"]))
        if physical is not None
        else float("inf")
    )
    return {
        "physical_location": physical,
        "predicted_physical_location": float(prediction["physical_location"]),
        "absolute_prediction_error": error,
        "maximum_absolute_prediction_error": float(
            prediction["maximum_absolute_error"]
        ),
        "prediction_passed": error
        <= float(prediction["maximum_absolute_error"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--states-output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported Jones gap-sprinkler manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    fixed = manifest["fixed_parameters"]
    parameters = RosslerParameters(
        a=float(fixed["a"]), b=float(fixed["b"]), c=float(fixed["c"])
    )
    section = _section(parameters)
    reference_options = manifest["attractor_reference"]
    solver = SolverConfig(**reference_options["solver"])
    reference_rows = []
    started = time.perf_counter()
    for reference_case in reference_options["cases"]:
        crossings = collect_crossings(
            parameters,
            reference_case["initial_state"],
            section,
            transient=float(reference_options["transient"]),
            observation_horizon=float(reference_options["observation_horizon"]),
            max_crossings=int(reference_options["max_crossings"]),
            config=solver,
        )
        recurrence = classify_fundamental_period(
            crossings.states, **reference_options["recurrence"]
        )
        reference_rows.append(
            {
                "id": reference_case["id"],
                "crossings": crossings,
                "recurrence": recurrence,
            }
        )
    calibration = reference_rows[0]["crossings"].states
    validation = reference_rows[1]["crossings"].states
    capture = manifest["capture"]
    validation_distances = cycle_crossing_distances(
        validation,
        calibration,
        coordinate_axes=tuple(capture["coordinate_axes"]),
        coordinate_scales=tuple(capture["coordinate_scales"]),
    )
    reverse_distances = cycle_crossing_distances(
        calibration,
        validation,
        coordinate_axes=tuple(capture["coordinate_axes"]),
        coordinate_scales=tuple(capture["coordinate_scales"]),
    )
    reference_distance_maximum = max(
        float(np.max(validation_distances)), float(np.max(reverse_distances))
    )
    minimum_reference_crossings = int(
        manifest["acceptance"]["minimum_reference_crossings"]
    )
    reference_passed = bool(
        all(row["crossings"].integration_success for row in reference_rows)
        and all(
            len(row["crossings"].times) >= minimum_reference_crossings
            for row in reference_rows
        )
        and all(
            row["recurrence"].label == OrbitLabel.UNRESOLVED
            for row in reference_rows
        )
        and reference_distance_maximum <= float(capture["radius"])
    )

    ensemble = manifest["ensemble"]
    x_values = np.linspace(
        ensemble["x_range"][0], ensemble["x_range"][1], ensemble["x_count"]
    )
    z_values = np.linspace(
        ensemble["z_range"][0], ensemble["z_range"][1], ensemble["z_count"]
    )
    x_grid, z_grid = np.meshgrid(x_values, z_values, indexing="ij")
    initial = np.column_stack(
        (
            x_grid.ravel(),
            np.full(x_grid.size, section.offset),
            z_grid.ravel(),
        )
    )
    result = sprinkler_survivors(
        parameters,
        initial,
        section,
        calibration,
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

    variants = tuple(
        {**manifest["oracle_common"], **variant["options"]}
        for variant in manifest["oracle_variants"]
    )
    coordinates = {}
    for coordinate in manifest["coordinates"]:
        name = coordinate["name"]
        source_values, target_values = survivor_return_pairs(
            result, int(coordinate["axis"])
        )
        if len(source_values) >= int(manifest["acceptance"]["minimum_return_pairs"]):
            lower = float(np.min(source_values))
            upper = float(np.max(source_values))
            prediction = coordinate["frozen_prediction"]
            expected_normalized = (
                float(prediction["physical_location"]) - lower
            ) / (upper - lower)
            if 0.0 <= expected_normalized <= 1.0:
                local = asdict(
                    infer_local_critical_point_robust(
                        source_values,
                        target_values,
                        expected_normalized_location=expected_normalized,
                        variants=variants,
                        **manifest["local_critical_rule"],
                    )
                )
            else:
                local = {
                    "resolved": False,
                    "normalized_location": None,
                    "reason": "frozen physical prediction lies outside survivor domain",
                }
            global_oracle = asdict(
                infer_return_map_branches_robust(
                    source_values,
                    target_values,
                    variants=variants,
                    minimum_variant_consensus=1.0,
                    maximum_normalized_critical_point_span=float(
                        manifest["global_oracle_reporting"][
                            "maximum_normalized_critical_point_span"
                        ]
                    ),
                )
            )
            physical = _physical_local_result(source_values, local, prediction)
        else:
            local = {
                "resolved": False,
                "normalized_location": None,
                "reason": "insufficient survivor return pairs",
            }
            global_oracle = {
                "resolved": False,
                "branch_count": None,
                "reason": "insufficient survivor return pairs",
            }
            physical = {
                "physical_location": None,
                "absolute_prediction_error": float("inf"),
                "prediction_passed": False,
            }
        coordinates[name] = {
            "pair_count": len(source_values),
            "source_domain": (
                [float(np.min(source_values)), float(np.max(source_values))]
                if len(source_values)
                else None
            ),
            "local_critical": local,
            "global_branch_oracle": global_oracle,
            "physical_prediction": physical,
        }

    captured_ids = np.flatnonzero(np.isfinite(result.capture_times))
    audit_ids = np.concatenate(
        (
            _evenly_spaced(
                result.survivor_ids, manifest["precision_audit"]["per_class"]
            ),
            _evenly_spaced(captured_ids, manifest["precision_audit"]["per_class"]),
        )
    )
    expected_captured = np.isin(audit_ids, captured_ids)
    audit_rows = []
    for trajectory_id, expected in zip(audit_ids, expected_captured, strict=True):
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
            audit_crossings.states, calibration, capture
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

    args.states_output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.states_output,
        calibration_reference=calibration,
        validation_reference=validation,
        survivor_ids=result.survivor_ids,
        survivor_initial_states=result.survivor_initial_states,
        survivor_final_states=result.survivor_final_states,
        midpoint_trajectory_ids=result.midpoint_trajectory_ids,
        midpoint_times=result.midpoint_times,
        midpoint_states=result.midpoint_states,
        capture_times=result.capture_times,
    )
    states_sha256 = hashlib.sha256(args.states_output.read_bytes()).hexdigest()
    acceptance = manifest["acceptance"]
    precision_agreement = sum(row["match"] for row in audit_rows) / max(
        len(audit_rows), 1
    )
    passed = bool(
        reference_passed
        and not np.any(result.failed)
        and len(result.survivor_ids) >= int(acceptance["minimum_final_survivors"])
        and result.survivor_counts[-1] < result.survivor_counts[0]
        and all(
            value["pair_count"] >= int(acceptance["minimum_return_pairs"])
            and value["local_critical"]["resolved"]
            and value["physical_prediction"]["prediction_passed"]
            for value in coordinates.values()
        )
        and precision_agreement
        >= float(acceptance["minimum_precision_audit_agreement"])
    )
    output = {
        "schema": "butterfly.jones-gap-sprinkler.v1",
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
        "reference": {
            "rows": [
                {
                    "id": row["id"],
                    "crossing_count": len(row["crossings"].times),
                    "integration_success": row["crossings"].integration_success,
                    "recurrence": asdict(row["recurrence"]),
                }
                for row in reference_rows
            ],
            "symmetric_maximum_scaled_distance": reference_distance_maximum,
            "passed": reference_passed,
        },
        "ensemble_size": len(initial),
        "survivor_counts": result.survivor_counts.tolist(),
        "final_survivor_count": len(result.survivor_ids),
        "failed_count": int(np.count_nonzero(result.failed)),
        "midpoint_crossing_count": len(result.midpoint_times),
        "coordinates": coordinates,
        "precision_audit": {
            "rows": audit_rows,
            "agreement": precision_agreement,
        },
        "states_artifact": str(args.states_output),
        "states_artifact_sha256": states_sha256,
        "passed": passed,
    }
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {
                "experiment_id": manifest["experiment_id"],
                "reference_passed": reference_passed,
                "survivor_counts": output["survivor_counts"],
                "final_survivor_count": output["final_survivor_count"],
                "pair_counts": {
                    name: value["pair_count"] for name, value in coordinates.items()
                },
                "local_locations": {
                    name: value["physical_prediction"]["physical_location"]
                    for name, value in coordinates.items()
                },
                "global_branch_counts": {
                    name: value["global_branch_oracle"]["branch_count"]
                    for name, value in coordinates.items()
                },
                "precision_agreement": precision_agreement,
                "passed": passed,
                "output": str(args.output),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
