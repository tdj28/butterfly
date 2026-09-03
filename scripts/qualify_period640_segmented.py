#!/usr/bin/env python3
"""Qualify both period-640 switch signs at one fixed parameter."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from compare_segmented_orbit_identity import segmented_dense
from multiple_shooting_core import correct_fixed_b
from qualify_period320_multiple_shooting import block_floquet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    supported_schemas = {
        "butterfly.period640-segmented-qualification-manifest.v1",
        "butterfly.segmented-child-qualification-manifest.v1",
    }
    if manifest.get("schema") not in supported_schemas:
        raise SystemExit("unsupported segmented child qualification manifest")
    candidate_bytes = args.candidate.read_bytes()
    if sha256_bytes(candidate_bytes) != manifest["candidate_receipt_sha256"]:
        raise SystemExit("candidate receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    candidate = json.loads(candidate_bytes)
    source_rows = [
        row
        for row in candidate["accepted_candidates"]
        if float(row["step_length"]) == manifest["source_step_length"]
    ]
    if {row["direction"] for row in source_rows} != {-1, 1}:
        raise SystemExit("candidate lacks both frozen source signs")
    source_rows.sort(key=lambda row: row["direction"])
    target_b = float(manifest["target_b"])
    a = float(manifest["fixed_a"])
    c = float(manifest["fixed_c"])
    solver = SolverConfig(**manifest["solver"])
    parameters = RosslerParameters(a=a, b=target_b, c=c)
    reference = np.asarray(candidate["attempts"][0]["initial_state"], dtype=float)
    phase = rossler_rhs(0.0, reference, parameters)
    phase /= np.linalg.norm(phase)
    corrected_rows = []
    for seed in source_rows:
        nodes = np.asarray(seed["nodes"], dtype=float)
        segment_count = len(nodes)
        variables = np.r_[nodes.ravel(), seed["period_time"]]
        corrected, status = correct_fixed_b(
            variables,
            target_b,
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
        duration = float(corrected[3 * segment_count])
        corrected_rows.append(
            {
                "direction": seed["direction"],
                "status": status,
                "period_time": duration,
                "half_node_rms": float(
                    np.sqrt(
                        np.mean(
                            (nodes[: segment_count // 2]
                            - nodes[segment_count // 2 :])
                            ** 2
                        )
                    )
                ),
                "floquet": block_floquet(nodes, duration, parameters, solver),
                "nodes": nodes.tolist(),
            }
        )
    dense = []
    endpoint_errors = []
    for row in corrected_rows:
        evaluate, endpoint_error = segmented_dense(
            np.asarray(row["nodes"]), row["period_time"], parameters, solver
        )
        dense.append(evaluate)
        endpoint_errors.append(endpoint_error)
    phases = np.linspace(0.0, 1.0, manifest["phase_samples"], endpoint=False)
    left_states = dense[0](phases)

    def rms(shift):
        return float(
            np.sqrt(np.mean((left_states - dense[1]((phases + shift) % 1.0)) ** 2))
        )

    shifts = np.linspace(0.0, 1.0, manifest["coarse_shifts"], endpoint=False)
    values = np.asarray([rms(shift) for shift in shifts])
    best = int(np.argmin(values))
    center = float(shifts[best])
    half_width = 1.0 / manifest["coarse_shifts"]
    history = []
    for stage in range(manifest["refinement_stages"]):
        stage_shifts = center + np.linspace(
            -half_width, half_width, manifest["refinement_points"]
        )
        stage_values = np.asarray([rms(shift % 1.0) for shift in stage_shifts])
        stage_best = int(np.argmin(stage_values))
        center = float(stage_shifts[stage_best])
        spacing = 2.0 * half_width / (manifest["refinement_points"] - 1)
        history.append(
            {
                "stage": stage + 1,
                "phase_shift": float(center % 1.0),
                "rms": float(stage_values[stage_best]),
                "grid_spacing": spacing,
            }
        )
        half_width = spacing
    identity = {
        "phase_shift": float(center % 1.0),
        "rms": rms(center % 1.0),
        "coarse_phase_shift": float(shifts[best]),
        "coarse_rms": float(values[best]),
        "refinement_history": history,
    }
    moduli = [row["floquet"]["dominant_nontrivial_modulus"] for row in corrected_rows]
    acceptance = manifest["acceptance"]
    output = {
        "schema": manifest.get(
            "output_schema", "butterfly.period640-segmented-qualification.v1"
        ),
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "target_b": target_b,
        "corrected_candidates": corrected_rows,
        "identity": identity,
        "maximum_segment_endpoint_error": max(endpoint_errors),
        "period_difference": abs(
            corrected_rows[0]["period_time"] - corrected_rows[1]["period_time"]
        ),
        "modulus_difference": abs(moduli[0] - moduli[1]),
    }
    output["passed"] = bool(
        identity["rms"] <= acceptance["max_identity_rms"]
        and output["maximum_segment_endpoint_error"]
        <= acceptance["max_segment_endpoint_error"]
        and output["period_difference"] <= acceptance["max_period_difference"]
        and output["modulus_difference"] <= acceptance["max_modulus_difference"]
        and all(
            row["status"]["success"]
            and row["status"]["matching_residual"]
            <= acceptance["max_matching_residual"]
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
