#!/usr/bin/env python3
"""Scan angle and c for nonlinear stable/unstable manifold matches."""

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
from scipy.integrate import solve_ivp

from butterfly import RosslerParameters, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes

try:
    from scripts.scan_jones_homoclinic_unstable_angles import eigenspaces
except ModuleNotFoundError:  # Direct ``python scripts/...`` execution.
    from scan_jones_homoclinic_unstable_angles import eigenspaces


SCHEMA = "butterfly.jones-homoclinic-manifold-match-scan-manifest.v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_source_receipts(manifest: dict) -> list[dict]:
    validated = []
    for binding in manifest["source_receipts"]:
        path = Path(binding["path"])
        if sha256_file(path) != binding["sha256"]:
            raise SystemExit(f"source receipt hash mismatch: {path}")
        receipt = json.loads(path.read_bytes())
        if receipt.get("schema") != binding["schema"]:
            raise SystemExit(f"source receipt schema mismatch: {path}")
        if receipt.get("experiment_id") != binding["experiment_id"]:
            raise SystemExit(f"source receipt experiment mismatch: {path}")
        if receipt.get("passed") is not True or receipt.get("candidate_count") != 0:
            raise SystemExit(f"source receipt status mismatch: {path}")
        if "expected_classification" in binding and (
            receipt.get("classification") != binding["expected_classification"]
        ):
            raise SystemExit(f"source receipt classification mismatch: {path}")
        if "expected_closest_match" in binding:
            expected = binding["expected_closest_match"]
            observed = receipt.get("closest_match", {})
            for field in ("c", "angle_index", "chord_mismatch"):
                if observed.get(field) != expected[field]:
                    raise SystemExit(f"source closest-match binding mismatch: {path}: {field}")
        validated.append(receipt)
    return validated


def align_local_geometry(
    parameters: RosslerParameters,
    reference_stable: np.ndarray,
    reference_plane: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    equilibrium, eigenvalues, stable, plane = eigenspaces(parameters)
    if float(np.dot(stable, reference_stable)) < 0.0:
        stable = -stable
    u_matrix, _singular, vt_matrix = np.linalg.svd(plane.T @ reference_plane)
    rotation = u_matrix @ vt_matrix
    if np.linalg.det(rotation) < 0.0:
        u_matrix[:, -1] *= -1.0
        rotation = u_matrix @ vt_matrix
    aligned_plane = plane @ rotation
    return equilibrium, eigenvalues, stable, aligned_plane


def stable_manifold_targets(
    parameters: RosslerParameters,
    equilibrium: np.ndarray,
    stable: np.ndarray,
    manifest: dict,
) -> list[dict]:
    radius = float(manifest["matching_radius"])
    local = manifest["stable_manifold"]
    solver = manifest["solver"]

    def rhs(time_value, state):
        return rossler_rhs(time_value, state, parameters)

    def radius_event(_time_value, state):
        return float(np.linalg.norm(state - equilibrium) - radius)

    radius_event.direction = 0.0
    radius_event.terminal = True
    targets = []
    for branch_sign in (-1, 1):
        initial = equilibrium + branch_sign * float(local["seed_radius"]) * stable
        result = solve_ivp(
            rhs,
            (0.0, -float(local["maximum_backward_time"])),
            initial,
            method=solver["method"],
            rtol=float(solver["rtol"]),
            atol=float(solver["atol"]),
            max_step=float(local["maximum_step"]),
            events=radius_event,
        )
        if not result.success or not len(result.t_events[0]):
            targets.append(
                {
                    "branch_sign": branch_sign,
                    "status": "failed",
                    "integration_success": bool(result.success),
                    "nfev": int(result.nfev),
                }
            )
            continue
        state = np.asarray(result.y_events[0][0], dtype=np.float64)
        targets.append(
            {
                "branch_sign": branch_sign,
                "status": "completed",
                "integration_success": bool(result.success),
                "backward_time": float(result.t_events[0][0]),
                "state": state.tolist(),
                "radius_residual": float(abs(np.linalg.norm(state - equilibrium) - radius)),
                "nfev": int(result.nfev),
            }
        )
    return targets


def tangent_basis(target: np.ndarray, equilibrium: np.ndarray) -> np.ndarray:
    radial = target - equilibrium
    radial /= np.linalg.norm(radial)
    axes = np.eye(3)
    seed = axes[int(np.argmin(np.abs(axes @ radial)))]
    first = seed - float(np.dot(seed, radial)) * radial
    first /= np.linalg.norm(first)
    second = np.cross(radial, first)
    second /= np.linalg.norm(second)
    return np.column_stack((first, second))


def scan_task(task: tuple[int, int, float, float, dict, list[dict], list, list]) -> dict:
    c_index, angle_index, c_value, angle, manifest, targets, equilibrium_list, plane_list = task
    parameters = RosslerParameters(
        a=float(manifest["fixed_parameters"]["a"]),
        b=float(manifest["fixed_parameters"]["b"]),
        c=c_value,
    )
    equilibrium = np.asarray(equilibrium_list, dtype=np.float64)
    plane = np.asarray(plane_list, dtype=np.float64)
    direction = np.cos(angle) * plane[:, 0] + np.sin(angle) * plane[:, 1]
    initial = equilibrium + float(manifest["unstable_seed_radius"]) * direction
    radius = float(manifest["matching_radius"])
    solver = manifest["solver"]

    def rhs(time_value, state):
        return rossler_rhs(time_value, state, parameters)

    def exit_event(_time_value, state):
        return float(np.linalg.norm(state - equilibrium) - radius)

    exit_event.direction = 1.0
    exit_event.terminal = True
    departure = solve_ivp(
        rhs,
        (0.0, float(manifest["maximum_exit_time"])),
        initial,
        method=solver["method"],
        rtol=float(solver["rtol"]),
        atol=float(solver["atol"]),
        max_step=float(solver["max_step"]),
        events=exit_event,
    )
    base = {
        "c_index": c_index,
        "angle_index": angle_index,
        "c": c_value,
        "angle": angle,
        "departure_success": bool(departure.success),
        "departure_nfev": int(departure.nfev),
    }
    if not departure.success or not len(departure.t_events[0]):
        return {**base, "status": "exit_failed"}

    exit_state = np.asarray(departure.y_events[0][0], dtype=np.float64)
    ignore_time = float(manifest["minimum_return_time_after_exit"])
    ignored = solve_ivp(
        rhs,
        (0.0, ignore_time),
        exit_state,
        method=solver["method"],
        rtol=float(solver["rtol"]),
        atol=float(solver["atol"]),
        max_step=float(solver["max_step"]),
    )
    if not ignored.success:
        return {
            **base,
            "status": "ignore_integration_failed",
            "exit_time": float(departure.t_events[0][0]),
            "ignore_success": False,
            "ignore_nfev": int(ignored.nfev),
        }
    ignored_state = np.asarray(ignored.y[:, -1], dtype=np.float64)
    ignored_radius = float(np.linalg.norm(ignored_state - equilibrium))
    if ignored_radius <= radius:
        return {
            **base,
            "status": "inside_at_return_gate",
            "exit_time": float(departure.t_events[0][0]),
            "ignore_success": True,
            "ignore_nfev": int(ignored.nfev),
            "radius_at_return_gate": ignored_radius,
        }

    def return_event(_time_value, state):
        return float(np.linalg.norm(state - equilibrium) - radius)

    return_event.direction = -1.0
    return_event.terminal = True

    def divergence_event(_time_value, state):
        return float(np.linalg.norm(state - equilibrium) - float(manifest["divergence_radius"]))

    divergence_event.direction = 1.0
    divergence_event.terminal = True
    returned = solve_ivp(
        rhs,
        (ignore_time, float(manifest["return_horizon"])),
        ignored_state,
        method=solver["method"],
        rtol=float(solver["rtol"]),
        atol=float(solver["atol"]),
        max_step=float(solver["max_step"]),
        events=(return_event, divergence_event),
    )
    base.update(
        {
            "exit_time": float(departure.t_events[0][0]),
            "ignore_success": True,
            "ignore_nfev": int(ignored.nfev),
            "radius_at_return_gate": ignored_radius,
            "return_success": bool(returned.success),
            "return_nfev": int(returned.nfev),
            "diverged": bool(len(returned.t_events[1])),
            "return_stop_time": float(returned.t[-1]),
        }
    )
    if not returned.success or not len(returned.t_events[0]):
        return {**base, "status": "no_inward_crossing"}

    return_state = np.asarray(returned.y_events[0][0], dtype=np.float64)
    completed_targets = [target for target in targets if target["status"] == "completed"]
    differences = [
        return_state - np.asarray(target["state"], dtype=np.float64)
        for target in completed_targets
    ]
    distances = [float(np.linalg.norm(difference)) for difference in differences]
    selected_index = int(np.argmin(distances))
    selected = completed_targets[selected_index]
    difference = differences[selected_index]
    target_state = np.asarray(selected["state"], dtype=np.float64)
    basis = tangent_basis(target_state, equilibrium)
    residual = basis.T @ difference
    mismatch = distances[selected_index]
    candidate = mismatch <= float(manifest["candidate"]["maximum_chord_mismatch"])
    return {
        **base,
        "status": "candidate" if candidate else "completed",
        "candidate": candidate,
        "inward_crossing_time_after_exit": float(returned.t_events[0][0]),
        "return_state": return_state.tolist(),
        "return_radius_residual": float(abs(np.linalg.norm(return_state - equilibrium) - radius)),
        "stable_branch_sign": int(selected["branch_sign"]),
        "stable_target_state": target_state.tolist(),
        "chord_mismatch": mismatch,
        "normalized_chord_mismatch": mismatch / radius,
        "tangent_residual": residual.tolist(),
        "tangent_residual_norm": float(np.linalg.norm(residual)),
    }


def nominate_cells(rows: list[dict], c_count: int, angle_count: int) -> list[dict]:
    lookup = {(row["c_index"], row["angle_index"]): row for row in rows}
    cells = []
    for c_index in range(c_count - 1):
        for angle_index in range(angle_count):
            corners = [
                lookup[(c_index, angle_index)],
                lookup[(c_index, (angle_index + 1) % angle_count)],
                lookup[(c_index + 1, angle_index)],
                lookup[(c_index + 1, (angle_index + 1) % angle_count)],
            ]
            if not all(row["status"] in {"completed", "candidate"} for row in corners):
                continue
            branch_signs = {row["stable_branch_sign"] for row in corners}
            if len(branch_signs) != 1:
                continue
            residuals = np.asarray([row["tangent_residual"] for row in corners])
            if all(float(np.min(residuals[:, axis])) <= 0.0 <= float(np.max(residuals[:, axis])) for axis in (0, 1)):
                cells.append(
                    {
                        "lower_c_index": c_index,
                        "lower_angle_index": angle_index,
                        "corner_indices": [
                            [row["c_index"], row["angle_index"]] for row in corners
                        ],
                        "stable_branch_sign": next(iter(branch_signs)),
                        "maximum_corner_chord_mismatch": max(row["chord_mismatch"] for row in corners),
                        "minimum_corner_chord_mismatch": min(row["chord_mismatch"] for row in corners),
                    }
                )
    return cells


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported homoclinic manifold-match manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    source_receipts = validate_source_receipts(manifest)

    fixed = manifest["fixed_parameters"]
    c_grid = manifest["c_grid"]
    c_values = np.linspace(
        float(c_grid["minimum"]),
        float(c_grid["maximum"]),
        int(c_grid["count"]),
        dtype=np.float64,
    )
    reference_parameters = RosslerParameters(
        a=float(fixed["a"]), b=float(fixed["b"]), c=float(c_grid["reference"])
    )
    _reference_equilibrium, _reference_values, reference_stable, reference_plane = eigenspaces(
        reference_parameters
    )
    parameter_rows = []
    tasks = []
    angle_count = int(manifest["angle_count"])
    offset = float(manifest["angle_offset_fraction"])
    angles = 2.0 * np.pi * (np.arange(angle_count, dtype=np.float64) + offset) / angle_count
    for c_index, c_value_raw in enumerate(c_values):
        c_value = float(c_value_raw)
        parameters = RosslerParameters(a=float(fixed["a"]), b=float(fixed["b"]), c=c_value)
        equilibrium, eigenvalues, stable, plane = align_local_geometry(
            parameters, reference_stable, reference_plane
        )
        targets = stable_manifold_targets(parameters, equilibrium, stable, manifest)
        parameter_rows.append(
            {
                "c_index": c_index,
                "c": c_value,
                "equilibrium": equilibrium.tolist(),
                "eigenvalues": [
                    {"real": float(value.real), "imag": float(value.imag)} for value in eigenvalues
                ],
                "stable_unit_vector": stable.tolist(),
                "unstable_plane_basis": plane.tolist(),
                "stable_targets": targets,
            }
        )
        for angle_index, angle in enumerate(angles):
            tasks.append(
                (
                    c_index,
                    angle_index,
                    c_value,
                    float(angle),
                    manifest,
                    targets,
                    equilibrium.tolist(),
                    plane.tolist(),
                )
            )

    workers = min(int(manifest["workers"]), os.cpu_count() or 1)
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as executor:
        rows = list(executor.map(scan_task, tasks))
    elapsed = time.perf_counter() - started
    completed = [row for row in rows if row["status"] in {"completed", "candidate"}]
    candidates = [row for row in completed if row["candidate"]]
    closest = min(completed, key=lambda row: row["chord_mismatch"]) if completed else None
    nominated_cells = nominate_cells(rows, len(c_values), angle_count)
    acceptance = manifest["acceptance"]
    checks = {
        "source_receipts_passed": all(receipt["passed"] for receipt in source_receipts),
        "stable_targets_complete": all(
            target["status"] == "completed"
            and target["radius_residual"] <= float(acceptance["maximum_sphere_residual"])
            for parameter_row in parameter_rows
            for target in parameter_row["stable_targets"]
        ),
        "saddle_focus_signatures": all(
            sum(value["real"] > 0.0 and abs(value["imag"]) > 0.0 for value in row["eigenvalues"])
            == 2
            and sum(value["real"] < 0.0 and abs(value["imag"]) < 1e-12 for value in row["eigenvalues"])
            == 1
            for row in parameter_rows
        ),
        "row_count": len(rows) == len(c_values) * angle_count,
        "exit_fraction": sum(row.get("departure_success", False) for row in rows) / len(rows)
        >= float(acceptance["minimum_exit_fraction"]),
        "return_crossing_fraction": len(completed) / len(rows)
        >= float(acceptance["minimum_return_crossing_fraction"]),
        "finite_observables": all(
            np.isfinite(row["chord_mismatch"])
            and np.all(np.isfinite(row["tangent_residual"]))
            for row in completed
        ),
        "return_sphere_residuals": all(
            row["return_radius_residual"] <= float(acceptance["maximum_sphere_residual"])
            for row in completed
        ),
    }
    output = {
        "schema": manifest["output_schema"],
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "source_receipts": [
            {
                "experiment_id": binding["experiment_id"],
                "sha256": binding["sha256"],
            }
            for binding in manifest["source_receipts"]
        ],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "workers": workers,
        },
        "fixed_parameters": fixed,
        "c_values": c_values.tolist(),
        "angles": angles.tolist(),
        "matching_radius": manifest["matching_radius"],
        "parameter_geometry": parameter_rows,
        "rows": rows,
        "completed_return_count": len(completed),
        "candidate_count": len(candidates),
        "candidate_indices": [
            [row["c_index"], row["angle_index"]] for row in candidates
        ],
        "closest_match": closest,
        "nominated_cell_count": len(nominated_cells),
        "nominated_cells": nominated_cells,
        "classification": (
            "direct_match_nominated"
            if candidates
            else "signed_cells_nominated"
            if nominated_cells
            else "no_sampled_manifold_match"
        ),
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
