#!/usr/bin/env python3
"""Solve a fixed-c homoclinic manifold match by three-variable shooting."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

from butterfly import RosslerParameters, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
try:
    from scripts.scan_jones_homoclinic_manifold_match import (
        align_local_geometry,
        stable_manifold_targets,
    )
    from scripts.scan_jones_homoclinic_unstable_angles import eigenspaces
except ModuleNotFoundError:  # Direct ``python scripts/...`` execution.
    from scan_jones_homoclinic_manifold_match import (
        align_local_geometry,
        stable_manifold_targets,
    )
    from scan_jones_homoclinic_unstable_angles import eigenspaces


SCHEMA = "butterfly.jones-homoclinic-single-shooting-manifest.v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported homoclinic single-shooting manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    binding = manifest["source_receipt"]
    source_path = Path(binding["path"])
    if sha256_file(source_path) != binding["sha256"]:
        raise SystemExit("source receipt hash mismatch")
    receipt = json.loads(source_path.read_bytes())
    for field in ("schema", "experiment_id", "classification", "candidate_count"):
        if receipt.get(field) != binding[field]:
            raise SystemExit(f"source receipt binding mismatch: {field}")
    if receipt.get("passed") is not True:
        raise SystemExit("passed source receipt required")
    source_closest = receipt["closest_match"]
    for field, value in binding["closest_match"].items():
        if source_closest.get(field) != value:
            raise SystemExit(f"source closest-match binding mismatch: {field}")

    fixed = manifest["fixed_parameters"]
    reference = RosslerParameters(
        a=float(manifest["reference_a"]), b=float(fixed["b"]), c=float(fixed["c"])
    )
    _reference_equilibrium, _reference_values, reference_stable, reference_plane = eigenspaces(
        reference
    )
    center = np.asarray(
        [
            float(manifest["initial_guess"]["angle"]),
            float(manifest["initial_guess"]["a"]),
            float(manifest["initial_guess"]["total_flight_time"]),
        ],
        dtype=np.float64,
    )
    scales = np.asarray(
        [
            float(manifest["search_scales"]["angle"]),
            float(manifest["search_scales"]["a"]),
            float(manifest["search_scales"]["total_flight_time"]),
        ],
        dtype=np.float64,
    )
    lower = np.asarray(manifest["normalized_bounds"]["lower"], dtype=np.float64)
    upper = np.asarray(manifest["normalized_bounds"]["upper"], dtype=np.float64)
    solver = manifest["solver"]
    history = []

    def physical(normalized: np.ndarray) -> np.ndarray:
        return center + scales * normalized

    def evaluate(normalized: np.ndarray, record: bool = True) -> np.ndarray:
        angle, a_value, flight_time = physical(normalized)
        parameters = RosslerParameters(a=float(a_value), b=float(fixed["b"]), c=float(fixed["c"]))
        equilibrium, _values, stable, plane = align_local_geometry(
            parameters, reference_stable, reference_plane
        )
        targets = stable_manifold_targets(parameters, equilibrium, stable, manifest)
        target_rows = [
            target
            for target in targets
            if target["status"] == "completed"
            and target["branch_sign"] == int(manifest["stable_branch_sign"])
        ]
        if len(target_rows) != 1:
            raise RuntimeError("unique completed stable target required")
        target = np.asarray(target_rows[0]["state"], dtype=np.float64)
        direction = np.cos(angle) * plane[:, 0] + np.sin(angle) * plane[:, 1]
        initial = equilibrium + float(manifest["unstable_seed_radius"]) * direction

        def rhs(time_value, state):
            return rossler_rhs(time_value, state, parameters)

        integrated = solve_ivp(
            rhs,
            (0.0, float(flight_time)),
            initial,
            method=solver["method"],
            rtol=float(solver["rtol"]),
            atol=float(solver["atol"]),
            max_step=float(solver["max_step"]),
        )
        if not integrated.success:
            raise RuntimeError("shooting integration failed")
        endpoint = np.asarray(integrated.y[:, -1], dtype=np.float64)
        residual = endpoint - target
        if record:
            history.append(
                {
                    "evaluation": len(history),
                    "normalized_variables": normalized.tolist(),
                    "angle": float(angle),
                    "a": float(a_value),
                    "total_flight_time": float(flight_time),
                    "residual": residual.tolist(),
                    "residual_norm": float(np.linalg.norm(residual)),
                    "endpoint": endpoint.tolist(),
                    "stable_target": target.tolist(),
                    "target_radius_residual": target_rows[0]["radius_residual"],
                    "nfev": int(integrated.nfev),
                }
            )
        return residual

    initial_residual = evaluate(np.zeros(3, dtype=np.float64))
    started = time.perf_counter()
    optimization = manifest["optimization"]
    result = least_squares(
        evaluate,
        np.zeros(3, dtype=np.float64),
        bounds=(lower, upper),
        method="trf",
        ftol=float(optimization["ftol"]),
        xtol=float(optimization["xtol"]),
        gtol=float(optimization["gtol"]),
        diff_step=np.asarray(optimization["normalized_diff_step"], dtype=np.float64),
        max_nfev=int(optimization["maximum_function_evaluations"]),
        verbose=0,
    )
    elapsed = time.perf_counter() - started
    final_variables = physical(result.x)
    final_residual = evaluate(result.x)
    jacobian_singular_values = np.linalg.svd(result.jac, compute_uv=False)
    boundary_margins = np.minimum(result.x - lower, upper - result.x)
    acceptance = manifest["acceptance"]
    root_nominated = bool(
        np.linalg.norm(final_residual) <= float(acceptance["maximum_root_residual"])
        and np.min(boundary_margins) >= float(acceptance["minimum_normalized_boundary_margin"])
    )
    checks = {
        "source_passed": receipt["passed"] is True,
        "initial_residual": np.linalg.norm(initial_residual)
        <= float(acceptance["maximum_initial_residual"]),
        "optimizer_terminated": int(result.status) != 0,
        "evaluation_budget": int(result.nfev)
        <= int(optimization["maximum_function_evaluations"]),
        "finite_result": bool(
            np.all(np.isfinite(result.x))
            and np.all(np.isfinite(final_residual))
            and np.all(np.isfinite(result.jac))
        ),
        "positive_flight_time": float(final_variables[2]) > 0.0,
    }
    output = {
        "schema": manifest["output_schema"],
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "source_receipt": {
            "experiment_id": receipt["experiment_id"],
            "sha256": binding["sha256"],
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "fixed_parameters": fixed,
        "stable_branch_sign": manifest["stable_branch_sign"],
        "matching_radius": manifest["matching_radius"],
        "initial_variables": {
            "angle": float(center[0]),
            "a": float(center[1]),
            "total_flight_time": float(center[2]),
        },
        "initial_residual": initial_residual.tolist(),
        "initial_residual_norm": float(np.linalg.norm(initial_residual)),
        "final_variables": {
            "angle": float(final_variables[0]),
            "a": float(final_variables[1]),
            "total_flight_time": float(final_variables[2]),
        },
        "final_normalized_variables": result.x.tolist(),
        "final_normalized_boundary_margins": boundary_margins.tolist(),
        "final_residual": final_residual.tolist(),
        "final_residual_norm": float(np.linalg.norm(final_residual)),
        "optimizer": {
            "success": bool(result.success),
            "status": int(result.status),
            "message": str(result.message),
            "cost": float(result.cost),
            "optimality": float(result.optimality),
            "nfev": int(result.nfev),
            "njev": None if result.njev is None else int(result.njev),
        },
        "scaled_jacobian_singular_values": jacobian_singular_values.tolist(),
        "history": history,
        "root_nominated": root_nominated,
        "classification": "single_shooting_root_nominated" if root_nominated else "single_shooting_unresolved",
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
