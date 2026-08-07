#!/usr/bin/env python3
"""Independently qualify a period-320 segmented candidate at fixed b."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig, flow_monodromy, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from multiple_shooting_core import (
    correct_fixed_b as correct_segmented_fixed_b,
    integrate_segment,
    seed_variables,
)
from qualify_separated_normal_form import (
    correct_fixed_b as correct_single_fixed_b,
    interpolate_branch,
    nontrivial_modulus,
)
from validate_multiple_shooting_switch import half_closure


def block_floquet(nodes, duration, parameters, solver):
    segment_count = len(nodes)
    segment_duration = duration / segment_count
    block_map = np.zeros((3 * segment_count, 3 * segment_count))
    for index, node in enumerate(nodes):
        _, transition, _ = integrate_segment(
            node, segment_duration, parameters, solver
        )
        target = (index + 1) % segment_count
        block_map[3 * target : 3 * target + 3, 3 * index : 3 * index + 3] = transition
    eigenvalues = np.linalg.eigvals(block_map)
    radii = np.sort(np.abs(eigenvalues))
    clusters = []
    for index in range(3):
        values = radii[index * segment_count : (index + 1) * segment_count]
        root_radius = float(np.median(values))
        clusters.append(
            {
                "root_radius_median": root_radius,
                "root_radius_minimum": float(np.min(values)),
                "root_radius_maximum": float(np.max(values)),
                "floquet_modulus": float(root_radius**segment_count),
            }
        )
    neutral_index = int(
        np.argmin([abs(item["floquet_modulus"] - 1.0) for item in clusters])
    )
    nontrivial = [
        item["floquet_modulus"]
        for index, item in enumerate(clusters)
        if index != neutral_index
    ]
    return {
        "clusters": clusters,
        "neutral_cluster_index": neutral_index,
        "dominant_nontrivial_modulus": float(max(nontrivial)),
    }


def cyclic_node_identity(left, right):
    values = [
        float(np.sqrt(np.mean((left - np.roll(right, shift, axis=0)) ** 2)))
        for shift in range(len(left))
    ]
    best = int(np.argmin(values))
    return {"rms": values[best], "node_shift": best}


def segmented_correction(seed, fixed_b, *, a, c, phase, reference, solver, manifest):
    segment_count = len(seed["nodes"])
    variables = np.r_[np.asarray(seed["nodes"]).ravel(), seed["period_time"]]
    corrected, status = correct_segmented_fixed_b(
        variables,
        fixed_b,
        segment_count=segment_count,
        a=a,
        c=c,
        phase=phase,
        phase_reference=reference,
        solver=solver,
        tolerance=manifest["corrector"]["tolerance"],
        max_evaluations=manifest["corrector"]["max_evaluations"],
    )
    nodes = corrected[: 3 * segment_count].reshape(segment_count, 3)
    return nodes, float(corrected[3 * segment_count]), status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--known-child", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.period320-qualification-manifest.v1":
        raise SystemExit("unsupported period-320 qualification manifest")
    known_bytes = args.known_child.read_bytes()
    candidate_bytes = args.candidate.read_bytes()
    if sha256_bytes(known_bytes) != manifest["known_child_receipt_sha256"]:
        raise SystemExit("known-child receipt hash mismatch")
    if sha256_bytes(candidate_bytes) != manifest["candidate_receipt_sha256"]:
        raise SystemExit("candidate receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    a = float(manifest["fixed_a"])
    c = float(manifest["fixed_c"])
    solver = SolverConfig(**manifest["solver"])
    known = json.loads(known_bytes)
    child_rows = next(
        branch["rows"]
        for branch in known["branches"]
        if branch["direction"] == manifest["known_child_direction"]
    )
    validation_b = float(manifest["block_validation_b"])
    known_seed = interpolate_branch(child_rows, validation_b)
    direct, direct_monodromy = correct_single_fixed_b(
        a=a,
        b=validation_b,
        c=c,
        initial_state=known_seed[0],
        period_time=known_seed[1],
        solver=solver,
        tolerance=manifest["corrector"]["tolerance"],
        max_evaluations=manifest["corrector"]["max_evaluations"],
    )
    validation_variables = seed_variables(
        direct.initial_state,
        direct.period_time,
        validation_b,
        segment_count=manifest["validation_segment_count"],
        a=a,
        c=c,
        solver=solver,
    )
    validation_parameters = RosslerParameters(a=a, b=validation_b, c=c)
    validation_phase = rossler_rhs(0.0, direct.initial_state, validation_parameters)
    validation_phase /= np.linalg.norm(validation_phase)
    validation_nodes, validation_duration, validation_status = segmented_correction(
        {
            "nodes": validation_variables[
                : 3 * manifest["validation_segment_count"]
            ].reshape(manifest["validation_segment_count"], 3),
            "period_time": validation_variables[
                3 * manifest["validation_segment_count"]
            ],
        },
        validation_b,
        a=a,
        c=c,
        phase=validation_phase,
        reference=direct.initial_state,
        solver=solver,
        manifest=manifest,
    )
    direct_modulus = nontrivial_modulus(direct_monodromy)
    validation_floquet = block_floquet(
        validation_nodes, validation_duration, validation_parameters, solver
    )
    validation_floquet["direct_nontrivial_modulus"] = direct_modulus
    validation_floquet["absolute_modulus_error"] = abs(
        validation_floquet["dominant_nontrivial_modulus"] - direct_modulus
    )
    validation_floquet["correction"] = validation_status

    candidate = json.loads(candidate_bytes)
    source_rows = [
        row
        for row in candidate["accepted_candidates"]
        if float(row["step_length"]) == manifest["source_step_length"]
    ]
    if {row["direction"] for row in source_rows} != {-1, 1}:
        raise SystemExit("candidate receipt lacks both frozen source directions")
    target_b = float(manifest["target_b"])
    target_parameters = RosslerParameters(a=a, b=target_b, c=c)
    reference = np.asarray(candidate["attempts"][0]["initial_state"])
    phase = rossler_rhs(0.0, reference, target_parameters)
    phase /= np.linalg.norm(phase)
    corrected_rows = []
    for seed in sorted(source_rows, key=lambda row: row["direction"]):
        nodes, duration, status = segmented_correction(
            seed,
            target_b,
            a=a,
            c=c,
            phase=phase,
            reference=reference,
            solver=solver,
            manifest=manifest,
        )
        floquet = block_floquet(nodes, duration, target_parameters, solver)
        corrected_rows.append(
            {
                "direction": seed["direction"],
                "status": status,
                "period_time": duration,
                "half_period_closure": half_closure(
                    nodes[0], duration, target_parameters, solver
                ),
                "half_node_rms": float(
                    np.sqrt(np.mean((nodes[: len(nodes) // 2] - nodes[len(nodes) // 2 :]) ** 2))
                ),
                "floquet": floquet,
                "nodes": nodes.tolist(),
            }
        )
    identity = cyclic_node_identity(
        np.asarray(corrected_rows[0]["nodes"]),
        np.asarray(corrected_rows[1]["nodes"]),
    )
    acceptance = manifest["acceptance"]
    output = {
        "schema": "butterfly.period320-qualification.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "block_floquet_validation": validation_floquet,
        "target_b": target_b,
        "corrected_candidates": corrected_rows,
        "opposite_sign_identity": identity,
    }
    output["passed"] = bool(
        validation_status["success"]
        and validation_floquet["absolute_modulus_error"]
        <= acceptance["max_validation_modulus_error"]
        and identity["rms"] <= acceptance["max_identity_rms"]
        and all(
            row["status"]["success"]
            and row["status"]["matching_residual"]
            <= acceptance["max_matching_residual"]
            and row["half_period_closure"]
            >= acceptance["minimum_half_period_closure"]
            and row["half_node_rms"] >= acceptance["minimum_half_node_rms"]
            and row["floquet"]["dominant_nontrivial_modulus"]
            <= acceptance["maximum_stable_modulus"]
            for row in corrected_rows
        )
    )
    atomic_write(args.output, canonical_json(output))
    printed = {**output}
    printed["corrected_candidates"] = [
        {key: value for key, value in row.items() if key != "nodes"}
        for row in corrected_rows
    ]
    print(json.dumps(printed, sort_keys=True))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
