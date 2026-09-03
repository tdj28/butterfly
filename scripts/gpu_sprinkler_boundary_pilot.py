#!/usr/bin/env python3
"""Discover transverse saddle-topology brackets with the qualified GPU sprinkler."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import platform
import time

import numpy as np
import scipy

from butterfly import (
    OrbitLabel,
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    classify_fundamental_period,
    collect_crossings,
    infer_lower_support_slope_robust,
    infer_ordered_transition_bracket,
    infer_return_map_branches_robust,
    scrambled_sobol_section_states,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from gpu_sprinkler_qualify import integrate_gpu, pairs

try:
    import torch
    import triton
except ImportError as error:  # pragma: no cover - GPU worker only
    raise SystemExit("PyTorch and Triton are required") from error


def expanded_cases(manifest: dict) -> list[dict]:
    cases = [dict(case, role="control") for case in manifest["controls"]]
    for slice_config in manifest["slices"]:
        c_value = float(slice_config["c"])
        for a_value in slice_config["a_values"]:
            cases.append(
                {
                    "id": f"c{c_value:.4f}-a{float(a_value):.6f}".replace(".", "p"),
                    "role": "target",
                    "slice_id": slice_config["id"],
                    "a": float(a_value),
                    "c": c_value,
                    "stable_period": int(slice_config["stable_period"]),
                    "expected_saddle_branch_count": None,
                }
            )
    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("case IDs must be unique")
    return cases


def prepare_case(case: dict, manifest: dict, solver: SolverConfig):
    parameters = RosslerParameters(
        a=float(case["a"]), b=float(manifest["fixed_parameters"]["b"]), c=float(case["c"])
    )
    section = barrio_rossler_section(parameters)
    reference = manifest["cycle_reference"]
    crossings = collect_crossings(
        parameters,
        manifest["cycle_initial_state"],
        section,
        transient=float(reference["transient"]),
        observation_horizon=float(reference["observation_horizon"]),
        max_crossings=int(reference["max_crossings"]),
        config=solver,
    )
    classification = classify_fundamental_period(
        crossings.states, **reference["recurrence"]
    )
    period = int(case["stable_period"])
    cycle = crossings.states[-period:]
    return parameters, section, cycle, classification


def coordinate_summary(gpu: dict, coordinate: dict, manifest: dict) -> dict:
    axis = int(coordinate["axis"])
    source, target = pairs(gpu["states"], gpu["survivor_ids"], axis)
    acceptance = manifest["acceptance"]
    maximum_crossings = int(manifest["gpu"]["max_recorded_crossings"])
    saturated = sum(
        len(gpu["states"][int(trajectory_id)]) >= maximum_crossings
        for trajectory_id in gpu["survivor_ids"]
    )
    if len(source) < int(acceptance["minimum_return_pairs"]):
        branch = {"resolved": False, "branch_count": None, "reason": "too few pairs"}
        slope = {"resolved": False, "slope_sign": None, "reason": "too few pairs"}
    elif saturated:
        branch = {
            "resolved": False,
            "branch_count": None,
            "reason": "recording buffer saturation",
        }
        slope = {
            "resolved": False,
            "slope_sign": None,
            "reason": "recording buffer saturation",
        }
    else:
        branch = asdict(
            infer_return_map_branches_robust(
                source,
                target,
                variants=manifest["oracle_variants"],
                common_options=manifest["oracle_common"],
                minimum_variant_consensus=float(
                    acceptance["minimum_oracle_variant_consensus"]
                ),
                maximum_normalized_critical_point_span=float(
                    acceptance["maximum_within_run_normalized_critical_span"]
                ),
            )
        )
        slope = asdict(
            infer_lower_support_slope_robust(
                source,
                target,
                variants=manifest["oracle_variants"],
                minimum_bin_points=int(manifest["oracle_common"]["minimum_bin_points"]),
                minimum_absolute_slope=float(
                    manifest["boundary_slope"]["minimum_absolute_normalized_slope"]
                ),
            )
        )
    sign = slope.get("slope_sign")
    predicted = (
        manifest["boundary_slope"]["sign_to_branch_count"].get(str(sign))
        if sign is not None
        else None
    )
    resolved = bool(
        branch.get("resolved")
        and slope.get("resolved")
        and predicted == branch.get("branch_count")
    )
    return {
        "pair_count": len(source),
        "source_minimum": float(np.min(source)) if len(source) else None,
        "source_maximum": float(np.max(source)) if len(source) else None,
        "recording_buffer_saturated_survivors": int(saturated),
        "branch_oracle": branch,
        "lower_support_slope": slope,
        "slope_predicted_branch_count": predicted,
        "resolved_joint_observation": resolved,
    }


def run_profile(
    case: dict,
    profile: dict,
    parameters,
    section,
    cycle,
    classification,
    manifest: dict,
) -> dict:
    ensemble = manifest["ensemble"]
    initial = scrambled_sobol_section_states(
        section,
        first_coordinate_range=tuple(ensemble["y_range"]),
        second_coordinate_range=tuple(ensemble["z_range"]),
        sample_power=int(profile["sample_power"]),
        scramble_seed=int(profile["scramble_seed"]),
    )
    gpu = integrate_gpu(
        parameters,
        initial,
        section,
        cycle,
        dt=float(profile.get("dt", ensemble["dt"])),
        horizon=float(ensemble["horizon"]),
        checkpoints=ensemble["checkpoint_times"],
        midpoint=tuple(ensemble["midpoint_window"]),
        capture=manifest["capture"],
        escape_radius=float(ensemble["escape_radius"]),
        chunk_steps=int(manifest["gpu"]["chunk_steps"]),
        max_crossings=int(manifest["gpu"]["max_recorded_crossings"]),
    )
    coordinates = {
        coordinate["name"]: coordinate_summary(gpu, coordinate, manifest)
        for coordinate in manifest["coordinates"]
    }
    decisions = {
        value["branch_oracle"].get("branch_count")
        for value in coordinates.values()
        if value["resolved_joint_observation"]
    }
    all_coordinates_resolved = all(
        value["resolved_joint_observation"] for value in coordinates.values()
    )
    joint_branch_count = (
        next(iter(decisions)) if all_coordinates_resolved and len(decisions) == 1 else None
    )
    stable_cycle = bool(
        classification.label == OrbitLabel.PERIODIC
        and classification.fundamental_period == int(case["stable_period"])
    )
    passed_numerics = bool(
        stable_cycle
        and not np.any(gpu["failed"])
        and len(gpu["survivor_ids"])
        >= int(manifest["acceptance"]["minimum_final_survivors"])
    )
    return {
        "id": profile["id"],
        "sample_power": int(profile["sample_power"]),
        "sample_count": len(initial),
        "scramble_seed": int(profile["scramble_seed"]),
        "dt": float(profile.get("dt", ensemble["dt"])),
        "survivor_counts": gpu["survivor_counts"].tolist(),
        "final_survivor_count": len(gpu["survivor_ids"]),
        "failed_count": int(np.count_nonzero(gpu["failed"])),
        "elapsed_seconds": gpu["elapsed_seconds"],
        "state_steps_per_second": gpu["state_steps_per_second"],
        "coordinates": coordinates,
        "passed_numerics": passed_numerics,
        "joint_branch_count": joint_branch_count if passed_numerics else None,
    }


def summarize_case(case: dict, classification, runs: list[dict]) -> dict:
    labels = [run["joint_branch_count"] for run in runs]
    resolved = all(label is not None for label in labels) and len(set(labels)) == 1
    observed = labels[0] if resolved else None
    expected = case.get("expected_saddle_branch_count")
    control_passed = case["role"] != "control" or (
        resolved and observed == int(expected)
    )
    return {
        **case,
        "cycle_classification": asdict(classification),
        "runs": runs,
        "resolved_across_profiles": resolved,
        "observed_branch_count": observed,
        "control_passed": control_passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.gpu-sprinkler-boundary-pilot-manifest.v1":
        raise SystemExit("unsupported manifest")
    if len(args.source_commit) != 40 or any(
        value not in "0123456789abcdef" for value in args.source_commit.lower()
    ):
        raise SystemExit("a full source commit is required")
    observed_commit = git_value("rev-parse", "HEAD")
    if observed_commit is not None and observed_commit != args.source_commit:
        raise SystemExit("source commit mismatch")
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is unavailable")

    solver = SolverConfig(**manifest["reference_solver"])
    profiles = manifest["runs"]
    case_rows = []
    started = time.perf_counter()
    for case in expanded_cases(manifest):
        parameters, section, cycle, classification = prepare_case(case, manifest, solver)
        applicable = [
            profile
            for profile in profiles
            if not profile.get("case_ids") or case["id"] in profile["case_ids"]
        ]
        stable_cycle = bool(
            classification.label == OrbitLabel.PERIODIC
            and classification.fundamental_period == int(case["stable_period"])
            and len(cycle) == int(case["stable_period"])
        )
        runs = (
            [
                run_profile(
                    case,
                    profile,
                    parameters,
                    section,
                    cycle,
                    classification,
                    manifest,
                )
                for profile in applicable
            ]
            if stable_cycle
            else []
        )
        row = summarize_case(case, classification, runs)
        case_rows.append(row)
        print(
            json.dumps(
                {
                    "case": case["id"],
                    "cycle": classification.fundamental_period,
                    "run_labels": [run["joint_branch_count"] for run in runs],
                    "observed": row["observed_branch_count"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    slice_results = []
    by_id = {row["id"]: row for row in case_rows}
    for slice_config in manifest["slices"]:
        c_value = float(slice_config["c"])
        case_ids = [
            f"c{c_value:.4f}-a{float(a):.6f}".replace(".", "p")
            for a in slice_config["a_values"]
        ]
        labels = [by_id[case_id]["observed_branch_count"] for case_id in case_ids]
        bracket = infer_ordered_transition_bracket(slice_config["a_values"], labels)
        slice_results.append(
            {
                "id": slice_config["id"],
                "c": c_value,
                "case_ids": case_ids,
                "labels": labels,
                "bracket": asdict(bracket),
            }
        )

    controls_passed = all(
        row["control_passed"] for row in case_rows if row["role"] == "control"
    )
    passed = controls_passed and all(
        result["bracket"]["resolved"] for result in slice_results
    )
    properties = torch.cuda.get_device_properties(0)
    output = {
        "schema": "butterfly.gpu-sprinkler-boundary-pilot.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": {
            "declared_commit": args.source_commit,
            "observed_git_commit": observed_commit,
            "branch": git_value("branch", "--show-current"),
            "dirty": bool(git_value("status", "--porcelain")),
        },
        "cases": case_rows,
        "slices": slice_results,
        "controls_passed": controls_passed,
        "passed": passed,
        "elapsed_seconds": time.perf_counter() - started,
        "environment": {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "triton": triton.__version__,
            "gpu_name": torch.cuda.get_device_name(0),
            "gpu_memory_bytes": properties.total_memory,
            "gpu_compute_capability": [properties.major, properties.minor],
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        },
        "scientific_scope": (
            "GPU sprinkler discovery of finite transverse branch-opening brackets; "
            "not PIM validation, a continuous TBA curve, or a manifold-event diagnosis"
        ),
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": sha256_bytes(output_bytes),
                "passed": passed,
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
