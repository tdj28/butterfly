#!/usr/bin/env python3
"""Test a blind PIM branch class against a precomputed UPO lobe atlas."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from analyze_upo_lobe_pim_overlap import _distance_summary
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def _lobe_points(receipt, amplitude_indices, axis, upper):
    allowed = set(int(value) for value in amplitude_indices)
    selected = []
    for trace in receipt["traces"]:
        if trace["amplitude_index"] not in allowed:
            continue
        count = int(trace["retained_pre_capture_returns"])
        states = np.asarray(trace["states"][:count], dtype=float)
        if len(states):
            selected.append(states[states[:, axis] < upper])
    nonempty = [values for values in selected if len(values)]
    return np.concatenate(nonempty) if nonempty else np.empty((0, 3), dtype=float)


def _line_pass(branch_count, left_count, fine_distance, coarse_distance, acceptance):
    if branch_count == 2:
        return left_count <= int(
            acceptance["maximum_two_branch_left_lobe_points_per_line"]
        )
    if branch_count == 3:
        return bool(
            left_count >= int(acceptance["minimum_three_branch_left_lobe_points_per_line"])
            and fine_distance is not None
            and coarse_distance is not None
            and fine_distance["maximum"]
            <= float(acceptance["maximum_fine_directed_distance"])
            and coarse_distance["maximum"]
            <= float(acceptance["maximum_coarse_directed_distance"])
        )
    return False


def _read_hashed(path, expected):
    payload = Path(path).read_bytes()
    observed = sha256_bytes(payload)
    if observed != expected:
        raise SystemExit(f"source hash mismatch: {path}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.midpoint-lobe-pim-association-manifest.v1":
        raise SystemExit("unsupported midpoint lobe/PIM association manifest")
    lobe_source = manifest["source_lobe_receipt"]
    pim_source = manifest["source_pim_receipt"]
    states_source = manifest["source_pim_states"]
    lobe_bytes = _read_hashed(lobe_source["path"], lobe_source["sha256"])
    pim_bytes = _read_hashed(pim_source["path"], pim_source["sha256"])
    states_bytes = _read_hashed(states_source["path"], states_source["sha256"])
    lobe_receipt = json.loads(lobe_bytes)
    pim_receipt = json.loads(pim_bytes)
    if pim_receipt["states_artifact_sha256"] != sha256_bytes(states_bytes):
        raise SystemExit("PIM receipt/state hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    case = next(row for row in pim_receipt["cases"] if row["id"] == manifest["pim_case_id"])
    branch_count = case["observed_saddle_branch_count"]
    profile_counts = [row["observed_saddle_branch_count"] for row in case["profiles"]]
    if branch_count not in manifest["allowed_branch_counts"] or any(
        value != branch_count for value in profile_counts
    ):
        raise SystemExit("PIM branch class is absent or inconsistent")
    axis = int(manifest["left_lobe"]["coordinate_axis"])
    upper = float(manifest["left_lobe"]["upper_bound"])
    axes = np.asarray(manifest["distance"]["coordinate_axes"], dtype=int)
    scales = np.asarray(manifest["distance"]["coordinate_scales"], dtype=float)
    fine = _lobe_points(
        lobe_receipt, manifest["lobe_seed_grid"]["fine_indices"], axis, upper
    )
    coarse = _lobe_points(
        lobe_receipt, manifest["lobe_seed_grid"]["coarse_indices"], axis, upper
    )
    started = time.perf_counter()
    rows = []
    with np.load(states_source["path"]) as archive:
        for horizon in manifest["pim_horizons"]:
            prefix = f"{manifest['pim_case_id']}__horizon-{int(horizon)}__"
            keys = sorted(key for key in archive.files if key.startswith(prefix))
            if len(keys) != int(manifest["pim_access_line_count"]):
                raise SystemExit("unexpected PIM access-line count")
            for key in keys:
                states = np.asarray(archive[key], dtype=float)[
                    int(manifest["pim_burn_in_returns"]) :
                ]
                left = states[states[:, axis] < upper]
                fine_distance = _distance_summary(fine, left, axes, scales)
                coarse_distance = _distance_summary(coarse, left, axes, scales)
                rows.append(
                    {
                        "horizon": int(horizon),
                        "access_line": key.removeprefix(prefix),
                        "pim_left_lobe_count": len(left),
                        "pim_minimum_y": float(np.min(states[:, axis])),
                        "fine_directed_distance": fine_distance,
                        "coarse_directed_distance": coarse_distance,
                        "passed": _line_pass(
                            branch_count,
                            len(left),
                            fine_distance,
                            coarse_distance,
                            manifest["acceptance"],
                        ),
                    }
                )
    acceptance = manifest["acceptance"]
    lobe_support_passed = bool(
        len(fine) >= int(acceptance["minimum_fine_lobe_points"])
        and len(coarse) >= int(acceptance["minimum_coarse_lobe_points"])
    )
    association_class = (
        "two_branch_and_lobe_excluded"
        if branch_count == 2
        else "three_branch_and_lobe_included"
    )
    receipt = {
        "schema": "butterfly.midpoint-lobe-pim-association-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_lobe_receipt_sha256": sha256_bytes(lobe_bytes),
        "source_pim_receipt_sha256": sha256_bytes(pim_bytes),
        "source_pim_states_sha256": sha256_bytes(states_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "observed_saddle_branch_count": branch_count,
        "association_class": association_class,
        "fine_lobe_point_count": len(fine),
        "coarse_lobe_point_count": len(coarse),
        "access_lines": rows,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": bool(lobe_support_passed and rows and all(row["passed"] for row in rows)),
        "scientific_scope": (
            "first prospective branch/lobe association at one midpoint, not an "
            "exact manifold intersection or continuous topology-change curve"
        ),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
