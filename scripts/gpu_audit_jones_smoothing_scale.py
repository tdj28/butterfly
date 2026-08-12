#!/usr/bin/env python3
"""Audit a shallow Jones/Barrio critical across smoothing and nested support."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import math
import os
import platform
from pathlib import Path

import numpy as np
import scipy

from butterfly import infer_return_map_branches
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.gpu_scan_jones_two_critical_residuals import (
    cycle_state_count,
    integrate_gpu,
    return_coordinate_axis,
    section_kind,
    sha256_file,
    torch,
    triton,
)


SCHEMA = "butterfly.jones-smoothing-scale-audit-manifest.v1"


def nested_pairs(record: dict, *, axis: int, z_count: int, x_stride: int, z_stride: int):
    """Return pairs from the declared rectangular stride subset of GPU seeds."""

    source, target = [], []
    for seed_id, states in zip(record["seed_ids"], record["states"], strict=True):
        x_index, z_index = divmod(int(seed_id), int(z_count))
        if x_index % x_stride or z_index % z_stride:
            continue
        values = np.asarray(states, dtype=float)[:, axis]
        if len(values) >= 2:
            source.append(values[:-1])
            target.append(values[1:])
    if not source:
        return np.empty(0), np.empty(0)
    return np.concatenate(source), np.concatenate(target)


def transition_summary(counts: list[int | None], smoothing: list[float]) -> dict:
    """Summarize a monotone resolved three-to-two smoothing transition."""

    resolved = [(index, count) for index, count in enumerate(counts) if count is not None]
    threes = [index for index, count in resolved if count == 3]
    twos = [index for index, count in resolved if count == 2]
    allowed = all(count in (2, 3) for _, count in resolved)
    monotone = bool(allowed and threes and twos and max(threes) < min(twos))
    if not monotone:
        return {
            "resolved": False,
            "lower_index": None,
            "upper_index": None,
            "smoothing_bounds": None,
            "reason": "no monotone resolved three-to-two transition",
        }
    lower, upper = max(threes), min(twos)
    return {
        "resolved": True,
        "lower_index": lower,
        "upper_index": upper,
        "smoothing_bounds": [float(smoothing[lower]), float(smoothing[upper])],
        "reason": "monotone resolved three-to-two transition",
    }


def _support_row(record, support, manifest, coordinate_axis):
    source, target = nested_pairs(
        record,
        axis=coordinate_axis,
        z_count=int(manifest["ensemble"]["z_count"]),
        x_stride=int(support["x_stride"]),
        z_stride=int(support["z_stride"]),
    )
    smoothing = [float(value) for value in manifest["smoothing_values"]]
    results = []
    if len(source) >= int(support["minimum_return_pairs"]):
        for index, value in enumerate(smoothing):
            options = {
                **manifest["oracle_common"],
                "smoothing": value,
                "random_seed": int(manifest["oracle_common"]["random_seed"]) + index,
            }
            results.append(asdict(infer_return_map_branches(source, target, **options)))
    counts = [row["branch_count"] if row["resolved"] else None for row in results]
    transition = transition_summary(counts, smoothing)
    normalized_second_criticals = []
    if len(source):
        width = float(np.ptp(source))
        lower = float(np.min(source))
        for row in results:
            if row["resolved"] and row["branch_count"] == 3:
                normalized_second_criticals.append(
                    (float(row["critical_points"][1]) - lower) / width
                )
    return {
        "name": support["name"],
        "x_stride": int(support["x_stride"]),
        "z_stride": int(support["z_stride"]),
        "pair_count": len(source),
        "source_domain": [float(np.min(source)), float(np.max(source))] if len(source) else None,
        "smoothing_values": smoothing,
        "branch_counts": counts,
        "transition": transition,
        "normalized_second_criticals": normalized_second_criticals,
        "results": results,
    }


def _combine_candidate(candidate, rows_by_profile, acceptance):
    rows = [row for profile in rows_by_profile for row in profile if row["id"] == candidate["id"]]
    supports = [support for row in rows for support in row["supports"]]
    all_transitions = bool(supports) and all(support["transition"]["resolved"] for support in supports)
    lower_indices = [support["transition"]["lower_index"] for support in supports if support["transition"]["resolved"]]
    upper_indices = [support["transition"]["upper_index"] for support in supports if support["transition"]["resolved"]]
    criticals = [value for support in supports for value in support["normalized_second_criticals"]]
    transition_index_span = max(
        max(lower_indices, default=0) - min(lower_indices, default=0),
        max(upper_indices, default=0) - min(upper_indices, default=0),
    )
    critical_span = max(criticals, default=math.inf) - min(criticals, default=-math.inf)
    pair_gate = bool(supports) and all(
        support["pair_count"] >= int(
            next(
                item["minimum_return_pairs"]
                for item in acceptance["support_requirements"]
                if item["name"] == support["name"]
            )
        )
        for support in supports
    )
    passed = bool(
        pair_gate
        and all_transitions
        and transition_index_span <= int(acceptance["maximum_transition_index_span"])
        and critical_span <= float(acceptance["maximum_normalized_second_critical_span"])
    )
    return {
        "id": candidate["id"],
        "grid_index": candidate.get("grid_index"),
        "parameters": candidate["parameters"],
        "pair_gate": pair_gate,
        "all_transitions_resolved": all_transitions,
        "transition_index_span": transition_index_span,
        "normalized_second_critical_span": critical_span,
        "passed": passed,
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
        raise SystemExit("unsupported smoothing-scale audit manifest")
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
    rows_by_profile = []
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
        rows = []
        for index, candidate in enumerate(candidates):
            rows.append(
                {
                    "id": candidate["id"],
                    "failed_count": int(run["failed_counts"][index]),
                    "survivor_counts": run["survivor_counts"][index].tolist(),
                    "supports": [
                        _support_row(run["records"][index], support, manifest, coordinate_axis)
                        for support in manifest["nested_support"]
                    ],
                }
            )
        rows_by_profile.append(rows)
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

    acceptance = {
        **manifest["acceptance"],
        "support_requirements": manifest["nested_support"],
    }
    combined = [_combine_candidate(candidate, rows_by_profile, acceptance) for candidate in candidates]
    passed_count = sum(row["passed"] for row in combined)
    passed = passed_count >= int(manifest["acceptance"]["minimum_qualified_candidates"])
    props = torch.cuda.get_device_properties(0)
    output = {
        "schema": "butterfly.jones-smoothing-scale-audit.v1",
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
        "qualified_candidate_count": passed_count,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    print(json.dumps({"output": str(args.output), "qualified": passed_count, "passed": passed}, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
