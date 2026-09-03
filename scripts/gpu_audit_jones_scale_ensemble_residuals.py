#!/usr/bin/env python3
"""Fresh-GPU Jones/Barrio residual audit across scale, support, and step."""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
from pathlib import Path

import numpy as np
import scipy

from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.audit_jones_scale_ensemble_residual import (
    point_assignment,
    sha256_file,
    signed_residual_bracket_cells,
)
from scripts.gpu_audit_jones_smoothing_scale import _support_row
from scripts.gpu_scan_jones_two_critical_residuals import (
    cycle_state_count,
    integrate_gpu,
    return_coordinate_axis,
    section_kind,
    torch,
    triton,
)


SCHEMA = "butterfly.jones-scale-ensemble-gpu-residual-manifest.v1"


def _profile_row(candidate, record, run, index, manifest, profile, coordinate_axis):
    supports = []
    orbit_values = np.asarray(candidate["section_states"], dtype=float)[:, coordinate_axis]
    for support in manifest["nested_support"]:
        support_row = _support_row(record, support, manifest, coordinate_axis)
        assignments = []
        for result in support_row["results"]:
            if result.get("resolved") and result.get("branch_count") == 3:
                assignments.append(
                    point_assignment(
                        orbit_values,
                        result["critical_points"],
                        support_row["source_domain"],
                    )
                )
            else:
                assignments.append(
                    {"resolved": False, "reason": "requires resolved three-branch result"}
                )
        support_row["assignments"] = assignments
        supports.append(support_row)
    return {
        "id": candidate["id"],
        "profile": profile["name"],
        "dt": profile["dt"],
        "failed_count": int(run["failed_counts"][index]),
        "survivor_counts": run["survivor_counts"][index].tolist(),
        "supports": supports,
    }


def combine_candidate(candidate, profile_rows, manifest):
    """Combine all scale/support/step reconstructions for one candidate."""

    rows = [row for profile in profile_rows for row in profile if row["id"] == candidate["id"]]
    reconstructions = {}
    criticals = [[], []]
    pair_gate = True
    failed_gate = all(row["failed_count"] == 0 for row in rows)
    for row in rows:
        for support in row["supports"]:
            minimum_pairs = int(
                next(
                    item["minimum_return_pairs"]
                    for item in manifest["nested_support"]
                    if item["name"] == support["name"]
                )
            )
            pair_gate &= support["pair_count"] >= minimum_pairs
            lower, upper = map(float, support["source_domain"] or (math.nan, math.nan))
            width = upper - lower
            for smoothing_index, (result, assignment) in enumerate(
                zip(support["results"], support["assignments"], strict=True)
            ):
                key = f"{row['profile']}/{support['name']}/s{smoothing_index}"
                if (
                    width > 0.0
                    and result.get("resolved")
                    and result.get("branch_count") == 3
                    and assignment.get("resolved")
                ):
                    normalized = [
                        (float(value) - lower) / width for value in result["critical_points"]
                    ]
                    for critical_index, value in enumerate(normalized):
                        criticals[critical_index].append(value)
                    reconstructions[key] = {
                        "profile": row["profile"],
                        "support": support["name"],
                        "smoothing_index": smoothing_index,
                        "smoothing": float(support["smoothing_values"][smoothing_index]),
                        "normalized_critical_points": normalized,
                        **assignment,
                    }
    expected = len(manifest["profiles"]) * len(manifest["nested_support"]) * len(manifest["smoothing_values"])
    complete = len(reconstructions) == expected
    assignments = {tuple(row["orbit_indices"]) for row in reconstructions.values()}
    common_assignment = len(assignments) == 1
    critical_spans = [
        max(values, default=math.inf) - min(values, default=-math.inf)
        for values in criticals
    ]
    maximum_critical_span = max(critical_spans)
    initial_count = int(manifest["ensemble"]["x_count"]) * int(manifest["ensemble"]["z_count"])
    if len(rows) == 2:
        survivor_difference = float(
            np.max(
                np.abs(
                    np.asarray(rows[0]["survivor_counts"], dtype=float)
                    - np.asarray(rows[1]["survivor_counts"], dtype=float)
                )
                / initial_count
            )
        )
    else:
        survivor_difference = math.inf
    maximum_absolute_residual = max(
        (
            abs(value)
            for row in reconstructions.values()
            for value in row["normalized_signed_residuals"]
        ),
        default=math.inf,
    )
    acceptance = manifest["acceptance"]
    eligible = bool(
        failed_gate
        and pair_gate
        and complete
        and common_assignment
        and maximum_critical_span
        <= float(acceptance["maximum_normalized_critical_location_span"])
        and survivor_difference
        <= float(acceptance["maximum_survivor_fraction_difference"])
    )
    return {
        "id": candidate["id"],
        "grid_index": candidate.get("grid_index"),
        "parameters": candidate["parameters"],
        "failed_gate": failed_gate,
        "pair_gate": pair_gate,
        "complete": complete,
        "reconstruction_count": len(reconstructions),
        "common_assignment": common_assignment,
        "common_assignment_indices": list(next(iter(assignments))) if common_assignment else None,
        "normalized_critical_spans": critical_spans,
        "maximum_normalized_critical_span": maximum_critical_span,
        "survivor_fraction_difference": survivor_difference,
        "maximum_absolute_residual": maximum_absolute_residual,
        "direct_gate_passed": bool(
            eligible
            and maximum_absolute_residual
            <= float(acceptance["maximum_direct_absolute_residual"])
        ),
        "eligible": eligible,
        "reconstructions": reconstructions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    candidate_bytes = args.candidates.read_bytes()
    manifest = json.loads(manifest_bytes)
    candidate_document = json.loads(candidate_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported scale-ensemble GPU residual manifest")
    for evidence in manifest["evidence"]:
        if sha256_file(Path(evidence["path"])) != evidence["sha256"]:
            raise SystemExit(f"evidence hash mismatch: {evidence['path']}")
    if sha256_bytes(candidate_bytes) != manifest["candidate_input_sha256"]:
        raise SystemExit("candidate input hash mismatch")
    if len(args.source_commit) != 40:
        raise SystemExit("a full source commit is required")
    observed_commit = git_value("rev-parse", "HEAD")
    if observed_commit is not None and observed_commit != args.source_commit:
        raise SystemExit("source commit mismatch")
    if torch is None or triton is None or not torch.cuda.is_available():
        raise SystemExit("CUDA, PyTorch, and Triton are required")
    candidates = [row for row in candidate_document["candidates"] if row["passed"]]
    if len(candidates) != int(manifest["expected_candidate_count"]):
        raise SystemExit("unexpected candidate count")
    coordinate_name, coordinate_axis = return_coordinate_axis(manifest)
    section_name, section_code = section_kind(manifest)
    state_count = cycle_state_count(manifest)

    profile_outputs = []
    profile_rows = []
    for profile in manifest["profiles"]:
        run = integrate_gpu(
            candidates,
            dt=float(profile["dt"]),
            horizon=float(manifest["ensemble"]["horizon"]),
            checkpoints=manifest["ensemble"]["checkpoint_times"],
            midpoint=manifest["ensemble"]["midpoint_window"],
            ensemble=manifest["ensemble"],
            capture=manifest["capture"],
            gpu_options=manifest["gpu"],
            section_name=section_name,
            section_code=section_code,
            target_cycle_state_count=state_count,
        )
        rows = [
            _profile_row(candidate, run["records"][index], run, index, manifest, profile, coordinate_axis)
            for index, candidate in enumerate(candidates)
        ]
        profile_rows.append(rows)
        profile_outputs.append(
            {
                "name": profile["name"],
                "dt": profile["dt"],
                "elapsed_seconds": run["elapsed_seconds"],
                "state_steps_per_second": run["state_steps_per_second"],
                "rows": rows,
            }
        )
        print(json.dumps({"profile": profile["name"], "completed": True}, sort_keys=True), flush=True)

    combined = [combine_candidate(candidate, profile_rows, manifest) for candidate in candidates]
    eligible = [row for row in combined if row["eligible"]]
    ranked = sorted(eligible, key=lambda row: (row["maximum_absolute_residual"], row["id"]))
    direct = [row for row in ranked if row["direct_gate_passed"]]
    bracket_cells = signed_residual_bracket_cells(combined)
    acceptance = manifest["acceptance"]
    coverage_passed = len(eligible) >= int(acceptance["minimum_eligible_candidates"])
    direct_passed = bool(coverage_passed and direct)
    bracket_passed = bool(
        coverage_passed
        and len(bracket_cells) >= int(acceptance["minimum_signed_bracket_cells"])
    )
    passed = direct_passed or bracket_passed
    props = torch.cuda.get_device_properties(0)
    output = {
        "schema": "butterfly.jones-scale-ensemble-gpu-residual.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "candidate_input_sha256": sha256_bytes(candidate_bytes),
        "source": {
            "declared_commit": args.source_commit,
            "observed_git_commit": observed_commit,
            "branch": git_value("branch", "--show-current"),
            "dirty": bool(git_value("status", "--porcelain")),
        },
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
            "gpu_memory_bytes": props.total_memory,
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        },
        "return_coordinate": {"name": coordinate_name, "axis": coordinate_axis},
        "section": {"kind": section_name, "gpu_code": section_code},
        "profiles": profile_outputs,
        "combined_candidates": combined,
        "eligible_candidate_count": len(eligible),
        "coverage_passed": coverage_passed,
        "ranked_candidate_ids": [row["id"] for row in ranked],
        "selected_candidate": ranked[0] if ranked else None,
        "direct_candidate_ids": [row["id"] for row in direct],
        "direct_candidate_passed": direct_passed,
        "signed_residual_bracket_cells": bracket_cells,
        "signed_residual_bracket_passed": bracket_passed,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {
                "output": str(args.output),
                "eligible": len(eligible),
                "direct": len(direct),
                "brackets": len(bracket_cells),
                "passed": passed,
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
