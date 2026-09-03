#!/usr/bin/env python3
"""Refine a receipt-selected unstable-manifold angle neighborhood."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import scipy

from butterfly import RosslerParameters, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
try:
    from scripts.scan_jones_homoclinic_unstable_angles import eigenspaces, scan_angle
except ModuleNotFoundError:  # Direct ``python scripts/...`` execution.
    from scan_jones_homoclinic_unstable_angles import eigenspaces, scan_angle


SCHEMA = "butterfly.jones-homoclinic-unstable-angle-refinement-manifest.v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_bound_source(manifest: dict) -> tuple[dict, dict]:
    binding = manifest["source_receipt"]
    path = Path(binding["path"])
    if sha256_file(path) != binding["sha256"]:
        raise SystemExit("source receipt hash mismatch")
    source = json.loads(path.read_bytes())
    if source.get("schema") != binding["schema"]:
        raise SystemExit("source receipt schema mismatch")
    if source.get("experiment_id") != binding["experiment_id"]:
        raise SystemExit("source receipt experiment mismatch")
    if not source.get("passed"):
        raise SystemExit("passed source receipt required")
    if source.get("classification") != binding["classification"]:
        raise SystemExit("source receipt classification mismatch")
    policy = manifest["selection_policy"]
    selected = source[policy["field"]]
    if int(selected["index"]) != int(policy["expected_source_index"]):
        raise SystemExit("source selection index mismatch")
    if float(selected["angle"]) != float(policy["expected_center_angle"]):
        raise SystemExit("source selection angle mismatch")
    return source, selected


def refinement_angles(center: float, half_width: float, count: int) -> np.ndarray:
    if count < 3 or count % 2 != 1:
        raise ValueError("refinement angle count must be odd and at least three")
    return center + np.linspace(-half_width, half_width, count, dtype=np.float64)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported homoclinic angle-refinement manifest")
    source_code = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source_code["commit"] is None or source_code["dirty"]:
        raise SystemExit("clean source required")

    source_receipt, selected = load_bound_source(manifest)
    parameters = RosslerParameters(**manifest["parameters"])
    equilibrium, eigenvalues, stable, plane = eigenspaces(parameters)
    equilibrium_residual = float(np.linalg.norm(rossler_rhs(0.0, equilibrium, parameters)))
    count = int(manifest["refinement"]["angle_count"])
    center = float(selected["angle"])
    half_width = float(manifest["refinement"]["half_width"])
    angles = refinement_angles(center, half_width, count)
    tasks = [(index, float(angle), manifest) for index, angle in enumerate(angles)]
    workers = min(int(manifest["workers"]), os.cpu_count() or 1)
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as executor:
        rows = list(executor.map(scan_angle, tasks))
    elapsed = time.perf_counter() - started

    completed = [row for row in rows if row["status"] in {"completed", "candidate"}]
    candidates = [row for row in completed if row["candidate"]]
    closest = min(completed, key=lambda row: row["minimum_return_distance"]) if completed else None
    most_aligned = min(completed, key=lambda row: row["stable_transverse_ratio"]) if completed else None
    joint_score_best = (
        min(
            completed,
            key=lambda row: (
                row["minimum_return_distance"]
                / float(manifest["candidate"]["maximum_return_distance"])
            )
            ** 2
            + (
                row["stable_transverse_ratio"]
                / float(manifest["candidate"]["maximum_stable_transverse_ratio"])
            )
            ** 2,
        )
        if completed
        else None
    )
    acceptance = manifest["acceptance"]
    checks = {
        "source_receipt_passed": bool(source_receipt["passed"]),
        "equilibrium": equilibrium_residual <= float(acceptance["maximum_equilibrium_residual"]),
        "saddle_focus_signature": bool(
            sum(value.real > 0 and abs(value.imag) > 0 for value in eigenvalues) == 2
            and sum(value.real < 0 and abs(value.imag) < 1e-12 for value in eigenvalues) == 1
        ),
        "row_count": len(rows) == count,
        "center_included": bool(angles[count // 2] == center),
        "window_covered": bool(
            angles[0] == center - half_width and angles[-1] == center + half_width
        ),
        "exit_fraction": sum(row.get("departure_success", False) for row in rows) / count
        >= float(acceptance["minimum_exit_fraction"]),
        "completed_fraction": len(completed) / count
        >= float(acceptance["minimum_completed_fraction"]),
        "finite_observables": all(
            np.isfinite(row["minimum_return_distance"])
            and np.isfinite(row["stable_transverse_ratio"])
            for row in completed
        ),
    }
    output = {
        "schema": manifest["output_schema"],
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source_code,
        "source_receipt": {
            "experiment_id": source_receipt["experiment_id"],
            "sha256": manifest["source_receipt"]["sha256"],
            "selection_field": manifest["selection_policy"]["field"],
            "selected_index": int(selected["index"]),
            "selected_angle": center,
            "selected_minimum_return_distance": float(selected["minimum_return_distance"]),
            "selected_stable_transverse_ratio": float(selected["stable_transverse_ratio"]),
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "workers": workers,
        },
        "parameters": manifest["parameters"],
        "equilibrium": equilibrium.tolist(),
        "equilibrium_residual": equilibrium_residual,
        "eigenvalues": [{"real": float(v.real), "imag": float(v.imag)} for v in eigenvalues],
        "stable_unit_vector": stable.tolist(),
        "unstable_plane_basis": plane.tolist(),
        "angle_center": center,
        "angle_half_width": half_width,
        "angle_count": count,
        "angle_step": float(angles[1] - angles[0]),
        "seed_radius": manifest["seed_radius"],
        "exit_radius": manifest["exit_radius"],
        "return_horizon": manifest["return_horizon"],
        "angles": rows,
        "candidate_count": len(candidates),
        "candidate_indices": [row["index"] for row in candidates],
        "closest_return": closest,
        "most_stable_aligned_return": most_aligned,
        "best_joint_normalized_return": joint_score_best,
        "classification": "refined_return_nominated" if candidates else "no_refined_close_stable_return",
        "checks": checks,
        "elapsed_seconds": elapsed,
        "passed": all(checks.values()),
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    print(json.dumps(output, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
