#!/usr/bin/env python3
"""Qualify step-size and short-horizon parity for the Jones gap sprinkler."""

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
    RosslerParameters,
    SolverConfig,
    classify_fundamental_period,
    collect_crossings,
    cycle_crossing_distances,
    infer_local_critical_point_robust,
    infer_return_map_branches_robust,
    sprinkler_survivors,
    survivor_return_pairs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.qualify_jones_gap_sprinkler import _physical_local_result, _section


SCHEMA = "butterfly.jones-gap-sprinkler-parity-manifest.v1"


def _ensemble(section, options: dict) -> np.ndarray:
    x_values = np.linspace(
        options["x_range"][0], options["x_range"][1], options["x_count"]
    )
    z_values = np.linspace(
        options["z_range"][0], options["z_range"][1], options["z_count"]
    )
    x_grid, z_grid = np.meshgrid(x_values, z_values, indexing="ij")
    return np.column_stack(
        (x_grid.ravel(), np.full(x_grid.size, section.offset), z_grid.ravel())
    )


def _coordinate_summary(result, manifest: dict) -> dict:
    variants = tuple(
        {**manifest["oracle_common"], **variant["options"]}
        for variant in manifest["oracle_variants"]
    )
    output = {}
    for coordinate in manifest["coordinates"]:
        name = coordinate["name"]
        source_values, target_values = survivor_return_pairs(
            result, int(coordinate["axis"])
        )
        prediction = coordinate["frozen_prediction"]
        if len(source_values) < int(manifest["acceptance"]["minimum_return_pairs"]):
            output[name] = {
                "pair_count": len(source_values),
                "source_domain": None,
                "local_critical": {
                    "resolved": False,
                    "normalized_location": None,
                    "reason": "insufficient survivor return pairs",
                },
                "global_branch_oracle": {
                    "resolved": False,
                    "branch_count": None,
                    "reason": "insufficient survivor return pairs",
                },
                "physical_prediction": {
                    "physical_location": None,
                    "absolute_prediction_error": float("inf"),
                    "prediction_passed": False,
                },
            }
            continue
        lower = float(np.min(source_values))
        upper = float(np.max(source_values))
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
        output[name] = {
            "pair_count": len(source_values),
            "source_domain": [lower, upper],
            "local_critical": local,
            "global_branch_oracle": global_oracle,
            "physical_prediction": _physical_local_result(
                source_values, local, prediction
            ),
        }
    return output


def _short_horizon_audit(
    parameters,
    section,
    reference,
    initial,
    manifest: dict,
    solver: SolverConfig,
) -> list[dict]:
    audit = manifest["short_horizon_audit"]
    ids = np.asarray(audit["trajectory_ids"], dtype=int)
    capture = manifest["capture"]
    fixed = sprinkler_survivors(
        parameters,
        initial[ids],
        section,
        reference,
        dt=float(audit["dt"]),
        horizon=float(audit["horizon"]),
        capture_coordinate_axes=tuple(capture["coordinate_axes"]),
        capture_coordinate_scales=tuple(capture["coordinate_scales"]),
        capture_radius=float(audit["disabled_capture_radius"]),
        required_capture_crossings=int(audit["disabled_capture_crossings"]),
        checkpoint_times=(float(audit["horizon"]),),
        midpoint_window=(0.0, float(audit["horizon"])),
        escape_radius=float(manifest["ensemble"]["escape_radius"]),
    )
    axes = np.asarray(capture["coordinate_axes"], dtype=int)
    scales = np.asarray(capture["coordinate_scales"], dtype=float)
    rows = []
    for local_id, trajectory_id in enumerate(ids):
        selected = fixed.all_midpoint_trajectory_ids == local_id
        order = np.argsort(fixed.all_midpoint_times[selected])
        fixed_times = fixed.all_midpoint_times[selected][order]
        fixed_states = fixed.all_midpoint_states[selected][order]
        adaptive = collect_crossings(
            parameters,
            initial[trajectory_id],
            section,
            transient=0.0,
            observation_horizon=float(audit["horizon"]),
            max_crossings=int(audit["max_crossings"]),
            config=solver,
        )
        retained = adaptive.times > 0.5 * float(audit["dt"])
        adaptive_times = adaptive.times[retained]
        adaptive_states = adaptive.states[retained]
        count = min(
            len(fixed_times),
            len(adaptive_times),
            int(audit["comparison_crossings"]),
        )
        if count:
            delta = (
                adaptive_states[:count, axes] - fixed_states[:count, axes]
            ) / scales
            state_error = float(np.max(np.linalg.norm(delta, axis=1)))
            time_error = float(
                np.max(np.abs(adaptive_times[:count] - fixed_times[:count]))
            )
        else:
            state_error = time_error = float("inf")
        rows.append(
            {
                "trajectory_id": int(trajectory_id),
                "comparison_crossings": count,
                "maximum_scaled_state_error": state_error,
                "maximum_time_error": time_error,
                "dop853_success": adaptive.integration_success,
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--states-output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported Jones gap parity manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    fixed_parameters = manifest["fixed_parameters"]
    parameters = RosslerParameters(
        a=float(fixed_parameters["a"]),
        b=float(fixed_parameters["b"]),
        c=float(fixed_parameters["c"]),
    )
    section = _section(parameters)
    reference_options = manifest["attractor_reference"]
    solver = SolverConfig(**reference_options["solver"])
    started = time.perf_counter()
    references = []
    for case in reference_options["cases"]:
        crossings = collect_crossings(
            parameters,
            case["initial_state"],
            section,
            transient=float(reference_options["transient"]),
            observation_horizon=float(reference_options["observation_horizon"]),
            max_crossings=int(reference_options["max_crossings"]),
            config=solver,
        )
        recurrence = classify_fundamental_period(
            crossings.states, **reference_options["recurrence"]
        )
        references.append((case["id"], crossings, recurrence))
    calibration = references[0][1].states
    validation = references[1][1].states
    capture = manifest["capture"]
    forward = cycle_crossing_distances(
        validation,
        calibration,
        coordinate_axes=tuple(capture["coordinate_axes"]),
        coordinate_scales=tuple(capture["coordinate_scales"]),
    )
    reverse = cycle_crossing_distances(
        calibration,
        validation,
        coordinate_axes=tuple(capture["coordinate_axes"]),
        coordinate_scales=tuple(capture["coordinate_scales"]),
    )
    reference_distance = max(float(np.max(forward)), float(np.max(reverse)))
    acceptance = manifest["acceptance"]
    reference_passed = bool(
        all(crossings.integration_success for _, crossings, _ in references)
        and all(
            len(crossings.times) >= int(acceptance["minimum_reference_crossings"])
            for _, crossings, _ in references
        )
        and all(
            recurrence.label == OrbitLabel.UNRESOLVED
            for _, _, recurrence in references
        )
        and reference_distance <= float(capture["radius"])
    )

    initial = _ensemble(section, manifest["ensemble"])
    attractor_count = int(manifest["attractor_false_negative"]["sample_count"])
    attractor_indices = np.rint(
        np.linspace(0, len(validation) - 1, attractor_count)
    ).astype(int)
    profile_rows = []
    state_payload = {
        "calibration_reference": calibration,
        "validation_reference": validation,
    }
    for profile in manifest["step_profiles"]:
        result = sprinkler_survivors(
            parameters,
            initial,
            section,
            calibration,
            dt=float(profile["dt"]),
            horizon=float(manifest["ensemble"]["horizon"]),
            capture_coordinate_axes=tuple(capture["coordinate_axes"]),
            capture_coordinate_scales=tuple(capture["coordinate_scales"]),
            capture_radius=float(capture["radius"]),
            required_capture_crossings=int(capture["required_crossings"]),
            checkpoint_times=manifest["ensemble"]["checkpoint_times"],
            midpoint_window=tuple(manifest["ensemble"]["midpoint_window"]),
            escape_radius=float(manifest["ensemble"]["escape_radius"]),
        )
        false_negative = sprinkler_survivors(
            parameters,
            validation[attractor_indices],
            section,
            calibration,
            dt=float(profile["dt"]),
            horizon=float(manifest["attractor_false_negative"]["horizon"]),
            capture_coordinate_axes=tuple(capture["coordinate_axes"]),
            capture_coordinate_scales=tuple(capture["coordinate_scales"]),
            capture_radius=float(capture["radius"]),
            required_capture_crossings=int(capture["required_crossings"]),
            checkpoint_times=manifest["attractor_false_negative"][
                "checkpoint_times"
            ],
            midpoint_window=(
                0.0,
                float(manifest["attractor_false_negative"]["horizon"]),
            ),
            escape_radius=float(manifest["ensemble"]["escape_radius"]),
        )
        coordinates = _coordinate_summary(result, manifest)
        profile_rows.append(
            {
                "name": profile["name"],
                "dt": float(profile["dt"]),
                "survivor_counts": result.survivor_counts.tolist(),
                "final_survivor_count": len(result.survivor_ids),
                "failed_count": int(np.count_nonzero(result.failed)),
                "midpoint_crossing_count": len(result.midpoint_times),
                "attractor_control_survivor_counts": false_negative.survivor_counts.tolist(),
                "attractor_control_failed_count": int(
                    np.count_nonzero(false_negative.failed)
                ),
                "coordinates": coordinates,
            }
        )
        key = profile["name"].replace("-", "_")
        state_payload[f"{key}_survivor_ids"] = result.survivor_ids
        state_payload[f"{key}_midpoint_trajectory_ids"] = result.midpoint_trajectory_ids
        state_payload[f"{key}_midpoint_times"] = result.midpoint_times
        state_payload[f"{key}_midpoint_states"] = result.midpoint_states

    coarse, fine = profile_rows
    survivor_fraction_difference = float(
        np.max(
            np.abs(
                np.asarray(coarse["survivor_counts"], dtype=float)
                - np.asarray(fine["survivor_counts"], dtype=float)
            )
            / len(initial)
        )
    )
    location_comparisons = {}
    for coordinate in manifest["coordinates"]:
        name = coordinate["name"]
        coarse_location = coarse["coordinates"][name]["physical_prediction"][
            "physical_location"
        ]
        fine_location = fine["coordinates"][name]["physical_prediction"][
            "physical_location"
        ]
        delta = (
            abs(float(coarse_location) - float(fine_location))
            if coarse_location is not None and fine_location is not None
            else float("inf")
        )
        maximum = float(coordinate["maximum_step_size_location_delta"])
        location_comparisons[name] = {
            "coarse": coarse_location,
            "fine": fine_location,
            "absolute_delta": delta,
            "maximum": maximum,
            "passed": delta <= maximum,
        }

    audit_rows = _short_horizon_audit(
        parameters, section, calibration, initial, manifest, solver
    )
    audit = manifest["short_horizon_audit"]
    audit_passed = all(
        row["dop853_success"]
        and row["comparison_crossings"] >= int(audit["comparison_crossings"])
        and row["maximum_scaled_state_error"]
        <= float(acceptance["maximum_short_horizon_scaled_state_error"])
        and row["maximum_time_error"]
        <= float(acceptance["maximum_short_horizon_time_error"])
        for row in audit_rows
    )
    profiles_passed = all(
        row["failed_count"] == 0
        and row["final_survivor_count"]
        >= int(acceptance["minimum_final_survivors"])
        and row["survivor_counts"][-1] < row["survivor_counts"][0]
        and row["attractor_control_survivor_counts"][-1]
        <= int(acceptance["maximum_attractor_control_survivors"])
        and row["attractor_control_failed_count"] == 0
        and all(
            value["pair_count"] >= int(acceptance["minimum_return_pairs"])
            and value["local_critical"]["resolved"]
            and value["physical_prediction"]["prediction_passed"]
            for value in row["coordinates"].values()
        )
        for row in profile_rows
    )
    step_parity_passed = bool(
        survivor_fraction_difference
        <= float(acceptance["maximum_survivor_fraction_difference"])
        and all(value["passed"] for value in location_comparisons.values())
    )
    passed = bool(
        reference_passed and profiles_passed and step_parity_passed and audit_passed
    )

    args.states_output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.states_output, **state_payload)
    states_sha256 = hashlib.sha256(args.states_output.read_bytes()).hexdigest()
    output = {
        "schema": "butterfly.jones-gap-sprinkler-parity.v1",
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
                    "id": identifier,
                    "crossing_count": len(crossings.times),
                    "integration_success": crossings.integration_success,
                    "recurrence": asdict(recurrence),
                }
                for identifier, crossings, recurrence in references
            ],
            "symmetric_maximum_scaled_distance": reference_distance,
            "passed": reference_passed,
        },
        "profiles": profile_rows,
        "survivor_fraction_difference": survivor_fraction_difference,
        "location_comparisons": location_comparisons,
        "short_horizon_audit": audit_rows,
        "gates": {
            "reference_passed": reference_passed,
            "profiles_passed": profiles_passed,
            "step_parity_passed": step_parity_passed,
            "short_horizon_audit_passed": audit_passed,
            "passed": passed,
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
                "profile_survivor_counts": {
                    row["name"]: row["survivor_counts"] for row in profile_rows
                },
                "profile_attractor_controls": {
                    row["name"]: row["attractor_control_survivor_counts"]
                    for row in profile_rows
                },
                "profile_local_locations": {
                    row["name"]: {
                        name: value["physical_prediction"]["physical_location"]
                        for name, value in row["coordinates"].items()
                    }
                    for row in profile_rows
                },
                "survivor_fraction_difference": survivor_fraction_difference,
                "location_comparisons": location_comparisons,
                "short_horizon_audit": audit_rows,
                "gates": output["gates"],
                "output": str(args.output),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
