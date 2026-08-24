#!/usr/bin/env python3
"""Scan saddle-focus unstable-manifold angles for close equilibrium returns."""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar

from butterfly import RosslerParameters, rossler_equilibria, rossler_jacobian, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-homoclinic-unstable-angle-scan-manifest.v1"


def eigenspaces(parameters: RosslerParameters):
    equilibrium = rossler_equilibria(parameters)[0]
    values, vectors = np.linalg.eig(rossler_jacobian(equilibrium, parameters))
    stable_index = int(np.argmin(values.real))
    unstable_index = int(np.argmax(values.imag))
    stable = np.asarray(vectors[:, stable_index].real, dtype=np.float64)
    stable /= np.linalg.norm(stable)
    plane = np.column_stack(
        (
            np.asarray(vectors[:, unstable_index].real, dtype=np.float64),
            np.asarray(vectors[:, unstable_index].imag, dtype=np.float64),
        )
    )
    plane, _ = np.linalg.qr(plane)
    return equilibrium, values, stable, plane


def scan_angle(task: tuple[int, float, dict]) -> dict:
    index, angle, manifest = task
    parameters = RosslerParameters(**manifest["parameters"])
    equilibrium, _values, stable, plane = eigenspaces(parameters)
    direction = np.cos(angle) * plane[:, 0] + np.sin(angle) * plane[:, 1]
    initial = equilibrium + float(manifest["seed_radius"]) * direction
    solver = manifest["solver"]
    exit_radius = float(manifest["exit_radius"])

    def rhs(time_value, state):
        return rossler_rhs(time_value, state, parameters)

    def exit_event(_time_value, state):
        return float(np.linalg.norm(state - equilibrium) - exit_radius)

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
    if not departure.success or not len(departure.t_events[0]):
        return {
            "index": index,
            "angle": angle,
            "status": "exit_failed",
            "departure_success": bool(departure.success),
            "departure_nfev": int(departure.nfev),
        }

    exit_time = float(departure.t_events[0][0])
    exit_state = np.asarray(departure.y_events[0][0], dtype=np.float64)
    divergence_radius = float(manifest["divergence_radius"])

    def divergence_event(_time_value, state):
        return float(np.linalg.norm(state - equilibrium) - divergence_radius)

    divergence_event.direction = 1.0
    divergence_event.terminal = True
    horizon = float(manifest["return_horizon"])
    returning = solve_ivp(
        rhs,
        (0.0, horizon),
        exit_state,
        method=solver["method"],
        rtol=float(solver["rtol"]),
        atol=float(solver["atol"]),
        max_step=float(solver["max_step"]),
        events=divergence_event,
        dense_output=True,
    )
    stop_time = float(returning.t[-1])
    start_time = float(manifest["minimum_return_time_after_exit"])
    if stop_time <= start_time or returning.sol is None:
        return {
            "index": index,
            "angle": angle,
            "status": "return_integration_failed",
            "departure_success": bool(departure.success),
            "return_success": bool(returning.success),
            "diverged": bool(len(returning.t_events[0])),
            "exit_time": exit_time,
            "return_stop_time": stop_time,
            "departure_nfev": int(departure.nfev),
            "return_nfev": int(returning.nfev),
        }

    sample_step = float(manifest["return_sample_step"])
    sample_count = max(3, int(np.ceil((stop_time - start_time) / sample_step)) + 1)
    sample_times = np.linspace(start_time, stop_time, sample_count)
    sample_states = returning.sol(sample_times).T
    sample_distances = np.linalg.norm(sample_states - equilibrium, axis=1)
    minimum_index = int(np.argmin(sample_distances))
    left_index = max(0, minimum_index - 1)
    right_index = min(sample_count - 1, minimum_index + 1)

    def distance(time_value: float) -> float:
        return float(np.linalg.norm(returning.sol(time_value) - equilibrium))

    if left_index < right_index:
        refined = minimize_scalar(
            distance,
            bounds=(float(sample_times[left_index]), float(sample_times[right_index])),
            method="bounded",
            options={"xatol": float(manifest["minimum_time_refinement_tolerance"])},
        )
        minimum_time = float(refined.x)
        minimum_distance = float(refined.fun)
    else:
        minimum_time = float(sample_times[minimum_index])
        minimum_distance = float(sample_distances[minimum_index])
    minimum_state = np.asarray(returning.sol(minimum_time), dtype=np.float64)
    displacement = minimum_state - equilibrium
    direction_cosine = abs(float(np.dot(displacement, stable))) / max(
        minimum_distance, np.finfo(np.float64).tiny
    )
    transverse_ratio = float(np.sqrt(max(0.0, 1.0 - direction_cosine**2)))
    candidate = (
        minimum_distance <= float(manifest["candidate"]["maximum_return_distance"])
        and transverse_ratio <= float(manifest["candidate"]["maximum_stable_transverse_ratio"])
    )
    return {
        "index": index,
        "angle": angle,
        "status": "candidate" if candidate else "completed",
        "candidate": candidate,
        "departure_success": bool(departure.success),
        "return_success": bool(returning.success),
        "diverged": bool(len(returning.t_events[0])),
        "exit_time": exit_time,
        "return_stop_time": stop_time,
        "minimum_return_time_after_exit": minimum_time,
        "minimum_return_distance": minimum_distance,
        "stable_direction_cosine": direction_cosine,
        "stable_transverse_ratio": transverse_ratio,
        "minimum_state": minimum_state.tolist(),
        "departure_nfev": int(departure.nfev),
        "return_nfev": int(returning.nfev),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported homoclinic angle-scan manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    parameters = RosslerParameters(**manifest["parameters"])
    equilibrium, eigenvalues, stable, plane = eigenspaces(parameters)
    equilibrium_residual = float(np.linalg.norm(rossler_rhs(0.0, equilibrium, parameters)))
    count = int(manifest["angle_count"])
    offset = float(manifest["angle_offset_fraction"])
    angles = 2.0 * np.pi * (np.arange(count, dtype=np.float64) + offset) / count
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
    acceptance = manifest["acceptance"]
    checks = {
        "equilibrium": equilibrium_residual <= float(acceptance["maximum_equilibrium_residual"]),
        "saddle_focus_signature": bool(
            sum(value.real > 0 and abs(value.imag) > 0 for value in eigenvalues) == 2
            and sum(value.real < 0 and abs(value.imag) < 1e-12 for value in eigenvalues) == 1
        ),
        "row_count": len(rows) == count,
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
        "source": source,
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
        "seed_radius": manifest["seed_radius"],
        "exit_radius": manifest["exit_radius"],
        "return_horizon": manifest["return_horizon"],
        "angles": rows,
        "candidate_count": len(candidates),
        "candidate_indices": [row["index"] for row in candidates],
        "closest_return": closest,
        "most_stable_aligned_return": most_aligned,
        "classification": "sampled_return_nominated" if candidates else "no_sampled_close_stable_return",
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
