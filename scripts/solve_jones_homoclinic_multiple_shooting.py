#!/usr/bin/env python3
"""Solve Jones's fixed-c homoclinic endpoint match by segmented shooting."""

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
from scipy.optimize import OptimizeResult, least_squares

from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes

try:
    from scripts.multiple_shooting_core import integrate_segment
    from scripts.scan_jones_homoclinic_manifold_match import (
        align_local_geometry,
        stable_manifold_targets,
    )
    from scripts.scan_jones_homoclinic_unstable_angles import eigenspaces
except ModuleNotFoundError:  # Direct ``python scripts/...`` execution.
    from multiple_shooting_core import integrate_segment
    from scan_jones_homoclinic_manifold_match import (
        align_local_geometry,
        stable_manifold_targets,
    )
    from scan_jones_homoclinic_unstable_angles import eigenspaces


SCHEMA = "butterfly.jones-homoclinic-multiple-shooting-manifest.v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def variable_layout(segment_count: int) -> dict[str, int]:
    if segment_count < 2:
        raise ValueError("multiple shooting requires at least two segments")
    node_count = segment_count - 1
    node_size = 3 * node_count
    return {
        "node_count": node_count,
        "node_size": node_size,
        "time_index": node_size,
        "a_index": node_size + 1,
        "angle_index": node_size + 2,
        "variable_count": node_size + 3,
    }


def block_norms(residual: np.ndarray) -> np.ndarray:
    residual = np.asarray(residual, dtype=np.float64)
    if residual.ndim != 1 or residual.size % 3:
        raise ValueError("matching residual must contain three-vectors")
    return np.linalg.norm(residual.reshape(-1, 3), axis=1)


def interleave_split_nodes(
    source_nodes: np.ndarray, midpoint_nodes: np.ndarray
) -> np.ndarray:
    """Return internal nodes after splitting every bound source arc in half."""
    source_nodes = np.asarray(source_nodes, dtype=np.float64)
    midpoint_nodes = np.asarray(midpoint_nodes, dtype=np.float64)
    if source_nodes.ndim != 2 or source_nodes.shape[1:] != (3,):
        raise ValueError("source nodes must have shape (segment_count - 1, 3)")
    if midpoint_nodes.shape != (len(source_nodes) + 1, 3):
        raise ValueError("one midpoint is required for every source segment")
    rows = []
    for index, midpoint in enumerate(midpoint_nodes):
        rows.append(midpoint)
        if index < len(source_nodes):
            rows.append(source_nodes[index])
    return np.asarray(rows, dtype=np.float64)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported homoclinic multiple-shooting manifest")
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
    source_receipt = json.loads(source_path.read_bytes())
    for field in ("schema", "experiment_id", "passed", "classification"):
        if source_receipt.get(field) != binding[field]:
            raise SystemExit(f"source receipt binding mismatch: {field}")
    source_failed_checks = source_receipt.get("failed_checks")
    if source_failed_checks is None:
        source_failed_checks = sorted(
            key for key, value in source_receipt.get("checks", {}).items() if value is False
        )
    if source_failed_checks != binding["failed_checks"]:
        raise SystemExit("source failed-check binding mismatch")
    for field, expected in binding["expected"].items():
        if source_receipt.get(field) != expected:
            raise SystemExit(f"source value binding mismatch: {field}")

    fixed = manifest["fixed_parameters"]
    reference = RosslerParameters(
        a=float(manifest["reference_a"]), b=float(fixed["b"]), c=float(fixed["c"])
    )
    _reference_equilibrium, _reference_values, reference_stable, reference_plane = (
        eigenspaces(reference)
    )
    stable_branch_sign = int(manifest["stable_branch_sign"])
    solver = SolverConfig(**manifest["solver"])
    segment_count = int(manifest["segment_count"])
    layout = variable_layout(segment_count)
    seed = source_receipt["final_variables"]
    seed_angle = float(seed["angle"])
    seed_a = float(seed["a"])
    seed_time = float(seed["total_flight_time"])

    def geometry(a_value: float, angle: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        parameters = RosslerParameters(a=a_value, b=float(fixed["b"]), c=float(fixed["c"]))
        equilibrium, _values, stable, plane = align_local_geometry(
            parameters, reference_stable, reference_plane
        )
        target_rows = [
            row
            for row in stable_manifold_targets(
                parameters, equilibrium, stable, manifest
            )
            if row["status"] == "completed"
            and row["branch_sign"] == stable_branch_sign
        ]
        if len(target_rows) != 1:
            raise RuntimeError("unique completed stable target required")
        direction = np.cos(angle) * plane[:, 0] + np.sin(angle) * plane[:, 1]
        angle_derivative = float(manifest["unstable_seed_radius"]) * (
            -np.sin(angle) * plane[:, 0] + np.cos(angle) * plane[:, 1]
        )
        initial = equilibrium + float(manifest["unstable_seed_radius"]) * direction
        target = np.asarray(target_rows[0]["state"], dtype=np.float64)
        return initial, target, angle_derivative

    seed_initial, _seed_target, _seed_angle_derivative = geometry(seed_a, seed_angle)
    seed_parameters = RosslerParameters(
        a=seed_a, b=float(fixed["b"]), c=float(fixed["c"])
    )
    seed_mode = manifest.get("seed_mode", "sequential_source_trajectory")
    if seed_mode == "sequential_source_trajectory":
        seed_segment_time = seed_time / segment_count
        seed_nodes = []
        current = seed_initial
        for _index in range(segment_count - 1):
            current, _transition, _sensitivity = integrate_segment(
                current,
                seed_segment_time,
                seed_parameters,
                solver,
                continuation_parameter="a",
            )
            seed_nodes.append(current)
        seed_nodes = np.asarray(seed_nodes, dtype=np.float64)
    elif seed_mode == "split_bound_segments":
        source_segment_count = int(binding["segment_count"])
        if segment_count != 2 * source_segment_count:
            raise SystemExit("split seed requires exactly twice the source segments")
        source_nodes = np.asarray(source_receipt["final_nodes"], dtype=np.float64)
        if source_nodes.shape != (source_segment_count - 1, 3):
            raise SystemExit("bound source-node shape mismatch")
        source_starts = np.vstack((seed_initial, source_nodes))
        half_segment_time = seed_time / segment_count
        midpoint_nodes = []
        for start in source_starts:
            midpoint, _transition, _sensitivity = integrate_segment(
                start,
                half_segment_time,
                seed_parameters,
                solver,
                continuation_parameter="a",
            )
            midpoint_nodes.append(midpoint)
        seed_nodes = interleave_split_nodes(source_nodes, midpoint_nodes)
    elif seed_mode == "bound_nodes":
        source_segment_count = int(binding["segment_count"])
        if segment_count != source_segment_count:
            raise SystemExit("bound-node seed requires unchanged segment count")
        seed_nodes = np.asarray(source_receipt["final_nodes"], dtype=np.float64)
        if seed_nodes.shape != (segment_count - 1, 3):
            raise SystemExit("bound source-node shape mismatch")
    else:
        raise SystemExit("unsupported multiple-shooting seed mode")
    initial_variables = np.r_[
        np.asarray(seed_nodes, dtype=np.float64).ravel(), seed_time, seed_a, seed_angle
    ]

    global_center = np.asarray(
        [
            float(manifest["search_center"]["total_flight_time"]),
            float(manifest["search_center"]["a"]),
            float(manifest["search_center"]["angle"]),
        ]
    )
    global_scales = np.asarray(
        [
            float(manifest["search_scales"]["total_flight_time"]),
            float(manifest["search_scales"]["a"]),
            float(manifest["search_scales"]["angle"]),
        ]
    )
    normalized_lower = np.asarray(manifest["normalized_bounds"]["lower"], dtype=float)
    normalized_upper = np.asarray(manifest["normalized_bounds"]["upper"], dtype=float)
    lower = np.full(layout["variable_count"], -np.inf)
    upper = np.full(layout["variable_count"], np.inf)
    global_indices = np.asarray(
        [layout["time_index"], layout["a_index"], layout["angle_index"]]
    )
    lower[global_indices] = global_center + global_scales * normalized_lower
    upper[global_indices] = global_center + global_scales * normalized_upper
    if not np.all((initial_variables > lower) & (initial_variables < upper)):
        raise SystemExit("source seed lies outside frozen bounds")

    a_step = float(manifest["derivatives"]["a_absolute_step"])
    history: list[dict] = []
    cached_point = None
    cached_residual = None
    cached_jacobian = None
    cached_details = None

    def compute(variables: np.ndarray):
        nonlocal cached_point, cached_residual, cached_jacobian, cached_details
        variables = np.asarray(variables, dtype=np.float64)
        if cached_point is not None and np.array_equal(variables, cached_point):
            return cached_residual, cached_jacobian, cached_details
        nodes = variables[: layout["node_size"]].reshape(layout["node_count"], 3)
        total_time = float(variables[layout["time_index"]])
        a_value = float(variables[layout["a_index"]])
        angle = float(variables[layout["angle_index"]])
        parameters = RosslerParameters(
            a=a_value, b=float(fixed["b"]), c=float(fixed["c"])
        )
        initial, target, initial_angle_derivative = geometry(a_value, angle)
        initial_plus, target_plus, _ = geometry(a_value + a_step, angle)
        initial_minus, target_minus, _ = geometry(a_value - a_step, angle)
        initial_a_derivative = (initial_plus - initial_minus) / (2.0 * a_step)
        target_a_derivative = (target_plus - target_minus) / (2.0 * a_step)
        segment_time = total_time / segment_count
        residual = np.empty(3 * segment_count)
        jacobian = np.zeros((3 * segment_count, layout["variable_count"]))
        endpoints = []
        for index in range(segment_count):
            start = initial if index == 0 else nodes[index - 1]
            endpoint, transition, sensitivity = integrate_segment(
                start,
                segment_time,
                parameters,
                solver,
                continuation_parameter="a",
            )
            destination = target if index + 1 == segment_count else nodes[index]
            row = slice(3 * index, 3 * index + 3)
            residual[row] = endpoint - destination
            if index > 0:
                current_node = slice(3 * (index - 1), 3 * index)
                jacobian[row, current_node] = transition
            if index + 1 < segment_count:
                next_node = slice(3 * index, 3 * index + 3)
                jacobian[row, next_node] -= np.eye(3)
            jacobian[row, layout["time_index"]] = (
                rossler_rhs(segment_time, endpoint, parameters) / segment_count
            )
            jacobian[row, layout["a_index"]] = sensitivity
            if index == 0:
                jacobian[row, layout["a_index"]] += transition @ initial_a_derivative
                jacobian[row, layout["angle_index"]] = (
                    transition @ initial_angle_derivative
                )
            if index + 1 == segment_count:
                jacobian[row, layout["a_index"]] -= target_a_derivative
            endpoints.append(endpoint)
        norms = block_norms(residual)
        details = {
            "block_norms": norms,
            "maximum_block_norm": float(np.max(norms)),
            "residual_norm": float(np.linalg.norm(residual)),
            "endpoint": np.asarray(endpoints[-1]).tolist(),
            "stable_target": target.tolist(),
        }
        history.append(
            {
                "evaluation": len(history),
                "total_flight_time": total_time,
                "a": a_value,
                "angle": angle,
                "residual_norm": details["residual_norm"],
                "maximum_block_norm": details["maximum_block_norm"],
            }
        )
        cached_point = variables.copy()
        cached_residual = residual
        cached_jacobian = jacobian
        cached_details = details
        return residual, jacobian, details

    initial_residual, _initial_jacobian, initial_details = compute(initial_variables)
    optimization = manifest["optimization"]
    started = time.perf_counter()
    if optimization.get("accept_initial_root", False):
        if (
            initial_details["maximum_block_norm"]
            > float(manifest["acceptance"]["maximum_root_block_residual"])
        ):
            raise SystemExit("bound initial seed does not satisfy the frozen root gate")
        result = OptimizeResult(
            x=initial_variables,
            success=True,
            status=4,
            message="Bound initial seed satisfies the frozen root gate.",
            cost=0.5 * float(np.dot(initial_residual, initial_residual)),
            optimality=float(np.linalg.norm(_initial_jacobian.T @ initial_residual, ord=np.inf)),
            nfev=1,
            njev=1,
        )
    else:
        result = least_squares(
            lambda value: compute(value)[0],
            initial_variables,
            jac=lambda value: compute(value)[1],
            bounds=(lower, upper),
            method="trf",
            x_scale="jac",
            ftol=float(optimization["ftol"]),
            xtol=float(optimization["xtol"]),
            gtol=float(optimization["gtol"]),
            max_nfev=int(optimization["maximum_function_evaluations"]),
            verbose=0,
        )
    elapsed = time.perf_counter() - started
    final_residual, final_jacobian, final_details = compute(result.x)
    final_nodes = result.x[: layout["node_size"]].reshape(layout["node_count"], 3)
    final_time = float(result.x[layout["time_index"]])
    final_a = float(result.x[layout["a_index"]])
    final_angle = float(result.x[layout["angle_index"]])
    normalized_globals = (
        np.asarray([final_time, final_a, final_angle]) - global_center
    ) / global_scales
    boundary_margins = np.minimum(
        normalized_globals - normalized_lower, normalized_upper - normalized_globals
    )

    replay_initial, replay_target, _ = geometry(final_a, final_angle)
    replay_parameters = RosslerParameters(
        a=final_a, b=float(fixed["b"]), c=float(fixed["c"])
    )
    replay_times = np.linspace(final_time / segment_count, final_time, segment_count)
    replay = solve_ivp(
        lambda time_value, state: rossler_rhs(time_value, state, replay_parameters),
        (0.0, final_time),
        replay_initial,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
        t_eval=replay_times,
    )
    if not replay.success:
        raise RuntimeError("direct replay integration failed")
    direct_node_discrepancies = np.linalg.norm(
        replay.y[:, :-1].T - final_nodes, axis=1
    )
    direct_endpoint_residual = replay.y[:, -1] - replay_target
    singular_values = np.linalg.svd(final_jacobian, compute_uv=False)
    acceptance = manifest["acceptance"]
    root_nominated = bool(
        final_details["maximum_block_norm"]
        <= float(acceptance["maximum_root_block_residual"])
        and np.min(boundary_margins)
        >= float(acceptance["minimum_normalized_boundary_margin"])
    )
    source_root_differences = {
        "a": abs(final_a - seed_a),
        "angle": abs(final_angle - seed_angle),
        "total_flight_time": abs(final_time - seed_time),
    }
    checks = {
        "source_status_bound": bool(
            source_receipt["passed"] is binding["passed"]
            and source_failed_checks == binding["failed_checks"]
        ),
        "initial_residual": bool(
            initial_details["maximum_block_norm"]
            <= float(acceptance["maximum_initial_block_residual"])
        ),
        "optimizer_terminated_or_root_gate": bool(
            int(result.status) != 0
            or (
                manifest["acceptance"].get("allow_root_gate_as_termination", False)
                and root_nominated
            )
        ),
        "evaluation_budget": int(result.nfev)
        <= int(optimization["maximum_function_evaluations"]),
        "finite_result": bool(
            np.all(np.isfinite(result.x))
            and np.all(np.isfinite(final_residual))
            and np.all(np.isfinite(final_jacobian))
        ),
        "positive_flight_time": final_time > 0.0,
        "segment_count": len(final_details["block_norms"]) == segment_count,
    }
    source_agreement = acceptance.get("source_root_agreement")
    if source_agreement is not None:
        checks["source_root_agreement"] = bool(
            source_root_differences["a"] <= float(source_agreement["maximum_a_difference"])
            and source_root_differences["angle"]
            <= float(source_agreement["maximum_angle_difference"])
            and source_root_differences["total_flight_time"]
            <= float(source_agreement["maximum_total_flight_time_difference"])
        )
    output = {
        "schema": manifest["output_schema"],
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "source_receipt": {
            "experiment_id": source_receipt["experiment_id"],
            "sha256": binding["sha256"],
            "passed": source_receipt["passed"],
            "failed_checks": source_failed_checks,
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "fixed_parameters": fixed,
        "stable_branch_sign": stable_branch_sign,
        "matching_radius": manifest["matching_radius"],
        "segment_count": segment_count,
        "seed_mode": seed_mode,
        "seed_variables": {
            "angle": seed_angle,
            "a": seed_a,
            "total_flight_time": seed_time,
        },
        "initial_residual_norm": float(np.linalg.norm(initial_residual)),
        "initial_maximum_block_residual": initial_details["maximum_block_norm"],
        "final_variables": {
            "angle": final_angle,
            "a": final_a,
            "total_flight_time": final_time,
        },
        "final_normalized_variables": normalized_globals.tolist(),
        "final_normalized_boundary_margins": boundary_margins.tolist(),
        "source_root_differences": source_root_differences,
        "final_nodes": final_nodes.tolist(),
        "final_residual_norm": final_details["residual_norm"],
        "final_maximum_block_residual": final_details["maximum_block_norm"],
        "final_block_residual_norms": final_details["block_norms"].tolist(),
        "final_endpoint": final_details["endpoint"],
        "final_stable_target": final_details["stable_target"],
        "direct_replay": {
            "endpoint_residual": direct_endpoint_residual.tolist(),
            "endpoint_residual_norm": float(np.linalg.norm(direct_endpoint_residual)),
            "maximum_node_discrepancy": float(np.max(direct_node_discrepancies)),
            "node_discrepancies": direct_node_discrepancies.tolist(),
        },
        "optimizer": {
            "success": bool(result.success),
            "status": int(result.status),
            "message": str(result.message),
            "cost": float(result.cost),
            "optimality": float(result.optimality),
            "nfev": int(result.nfev),
            "njev": None if result.njev is None else int(result.njev),
        },
        "jacobian_policy": "analytic_segment_transitions_with_central_endpoint_a_derivative",
        "independent_integrator": manifest.get("independent_integrator"),
        "jacobian_singular_values": singular_values.tolist(),
        "history": history,
        "root_nominated": root_nominated,
        "classification": (
            "multiple_shooting_root_nominated"
            if root_nominated
            else "multiple_shooting_unresolved"
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
