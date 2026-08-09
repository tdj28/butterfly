#!/usr/bin/env python3
"""Measure left-lobe overlap between UPO manifolds and PIM saddles."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.spatial import cKDTree

from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def _lobe_points(atlas, case_id, amplitude_indices, axis, upper):
    allowed = set(int(value) for value in amplitude_indices)
    selected = []
    for trace in atlas["traces"]:
        if trace["case_id"] != case_id or trace["amplitude_index"] not in allowed:
            continue
        count = int(trace["retained_pre_capture_returns"])
        states = np.asarray(trace["states"][:count], dtype=float)
        if len(states):
            selected.append(states[states[:, axis] < upper])
    nonempty = [values for values in selected if len(values)]
    return np.concatenate(nonempty) if nonempty else np.empty((0, 3), dtype=float)


def _distance_summary(source, target, axes, scales):
    source = np.asarray(source, dtype=float)
    target = np.asarray(target, dtype=float)
    if not len(source) or not len(target):
        return None
    tree = cKDTree(source[:, axes] / scales)
    distances = tree.query(target[:, axes] / scales, k=1)[0]
    return {
        "minimum": float(np.min(distances)),
        "median": float(np.median(distances)),
        "q90": float(np.quantile(distances, 0.9)),
        "maximum": float(np.max(distances)),
    }


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
    if manifest.get("schema") != "butterfly.upo-lobe-pim-overlap-manifest.v1":
        raise SystemExit("unsupported UPO/PIM overlap manifest")
    atlas_source = manifest["source_atlas_receipt"]
    atlas_bytes = _read_hashed(atlas_source["path"], atlas_source["sha256"])
    atlas = json.loads(atlas_bytes)
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    axes = np.asarray(manifest["distance"]["coordinate_axes"], dtype=int)
    scales = np.asarray(manifest["distance"]["coordinate_scales"], dtype=float)
    left_axis = int(manifest["left_lobe"]["coordinate_axis"])
    upper = float(manifest["left_lobe"]["upper_bound"])
    acceptance = manifest["acceptance"]
    started = time.perf_counter()
    cases = []
    source_hashes = {"atlas_receipt": sha256_bytes(atlas_bytes)}
    for case in manifest["cases"]:
        receipt_bytes = _read_hashed(
            case["pim_receipt"]["path"], case["pim_receipt"]["sha256"]
        )
        states_bytes = _read_hashed(
            case["pim_states"]["path"], case["pim_states"]["sha256"]
        )
        source_hashes[f"{case['id']}_pim_receipt"] = sha256_bytes(receipt_bytes)
        source_hashes[f"{case['id']}_pim_states"] = sha256_bytes(states_bytes)
        receipt = json.loads(receipt_bytes)
        if receipt["states_artifact_sha256"] != sha256_bytes(states_bytes):
            raise SystemExit(f"PIM receipt/state mismatch: {case['id']}")
        fine = _lobe_points(
            atlas,
            case["atlas_case_id"],
            manifest["atlas_seed_grid"]["fine_indices"],
            left_axis,
            upper,
        )
        coarse = _lobe_points(
            atlas,
            case["atlas_case_id"],
            manifest["atlas_seed_grid"]["coarse_indices"],
            left_axis,
            upper,
        )
        rows = []
        with np.load(case["pim_states"]["path"]) as archive:
            for horizon in manifest["pim_horizons"]:
                prefix = f"{case['pim_case_id']}__horizon-{int(horizon)}__"
                keys = sorted(key for key in archive.files if key.startswith(prefix))
                if len(keys) != int(manifest["pim_access_line_count"]):
                    raise SystemExit(f"unexpected PIM access-line count: {case['id']}")
                for key in keys:
                    states = np.asarray(archive[key], dtype=float)[
                        int(manifest["pim_burn_in_returns"]) :
                    ]
                    left = states[states[:, left_axis] < upper]
                    fine_distance = _distance_summary(fine, left, axes, scales)
                    coarse_distance = _distance_summary(coarse, left, axes, scales)
                    if case["expected_left_lobe_support"]:
                        passed = bool(
                            len(left)
                            >= int(acceptance["minimum_left_lobe_points_per_line"])
                            and fine_distance is not None
                            and coarse_distance is not None
                            and fine_distance["maximum"]
                            <= float(acceptance["maximum_fine_directed_distance"])
                            and coarse_distance["maximum"]
                            <= float(acceptance["maximum_coarse_directed_distance"])
                        )
                    else:
                        passed = len(left) <= int(
                            acceptance["maximum_excluded_left_lobe_points_per_line"]
                        )
                    rows.append(
                        {
                            "horizon": int(horizon),
                            "access_line": key.removeprefix(prefix),
                            "pim_state_count": len(states),
                            "pim_left_lobe_count": len(left),
                            "pim_minimum_y": float(np.min(states[:, left_axis])),
                            "fine_directed_distance": fine_distance,
                            "coarse_directed_distance": coarse_distance,
                            "passed": passed,
                        }
                    )
        atlas_passed = bool(
            len(fine) >= int(acceptance["minimum_fine_lobe_points"])
            and len(coarse) >= int(acceptance["minimum_coarse_lobe_points"])
        )
        cases.append(
            {
                "id": case["id"],
                "expected_left_lobe_support": case["expected_left_lobe_support"],
                "fine_lobe_point_count": len(fine),
                "coarse_lobe_point_count": len(coarse),
                "fine_minimum_y": (
                    float(np.min(fine[:, left_axis])) if len(fine) else None
                ),
                "coarse_minimum_y": (
                    float(np.min(coarse[:, left_axis])) if len(coarse) else None
                ),
                "access_lines": rows,
                "passed": atlas_passed and all(row["passed"] for row in rows),
            }
        )
    receipt = {
        "schema": "butterfly.upo-lobe-pim-overlap-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "source_hashes": source_hashes,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "left_lobe_upper_bound": upper,
        "cases": cases,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": bool(cases and all(case["passed"] for case in cases)),
        "scientific_scope": (
            "retrospective hash-bound lobe/saddle overlap diagnostic, not a "
            "prospective parameter-continuation or manifold-intersection proof"
        ),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(
        json.dumps(
            {
                "experiment_id": receipt["experiment_id"],
                "manifest_sha256": receipt["manifest_sha256"],
                "cases": cases,
                "elapsed_seconds": receipt["elapsed_seconds"],
                "passed": receipt["passed"],
            },
            sort_keys=True,
        )
    )
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
