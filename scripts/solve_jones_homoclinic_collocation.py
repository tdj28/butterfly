#!/usr/bin/env python3
"""Solve the Jones homoclinic continuation plane by adaptive collocation."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_bvp, solve_ivp

from butterfly import RosslerParameters, SolverConfig
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes

try:
    from scripts.continue_jones_homoclinic_pseudoarclength import (
        load_bound_receipt,
    )
    from scripts.scan_jones_homoclinic_manifold_match import (
        align_local_geometry,
        stable_manifold_targets,
    )
    from scripts.scan_jones_homoclinic_unstable_angles import eigenspaces
except ModuleNotFoundError:  # Direct ``python scripts/...`` execution.
    from continue_jones_homoclinic_pseudoarclength import load_bound_receipt
    from scan_jones_homoclinic_manifold_match import (
        align_local_geometry,
        stable_manifold_targets,
    )
    from scan_jones_homoclinic_unstable_angles import eigenspaces


SCHEMA = "butterfly.jones-homoclinic-collocation-manifest.v1"


def physical_secant_plane(
    previous: np.ndarray,
    current: np.ndarray,
    scales: np.ndarray,
    desired_c_increment: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return the normalized physical secant and its crossing predictor."""
    tangent = (np.asarray(current) - np.asarray(previous)) / np.asarray(scales)
    tangent /= np.linalg.norm(tangent)
    if tangent[1] * desired_c_increment <= 0.0:
        tangent *= -1.0
    step = desired_c_increment / (tangent[1] * scales[1])
    predictor = np.asarray(current) + step * tangent * scales
    return tangent, predictor


def scaled_rossler_flow(
    states: np.ndarray, total_time: float, a_value: float, b_value: float, c_value: float
) -> np.ndarray:
    """Vectorized Rössler flow on normalized collocation time."""
    x, y, z = states
    return total_time * np.vstack((-y - z, x + a_value * y, b_value + z * (x - c_value)))


def scaled_rossler_jacobian(
    states: np.ndarray, total_time: float, a_value: float, c_value: float
) -> np.ndarray:
    """State Jacobian of the normalized-time vector field."""
    x, _y, z = states
    count = states.shape[1]
    jacobian = np.zeros((3, 3, count), dtype=np.float64)
    jacobian[0, 1] = -total_time
    jacobian[0, 2] = -total_time
    jacobian[1, 0] = total_time
    jacobian[1, 1] = total_time * a_value
    jacobian[2, 0] = total_time * z
    jacobian[2, 2] = total_time * (x - c_value)
    return jacobian


def replay_defects(
    states: np.ndarray,
    total_time: float,
    parameters: RosslerParameters,
    solver: SolverConfig,
) -> np.ndarray:
    """Independently replay every uniform collocation arc with Radau."""
    segment_count = states.shape[0] - 1
    duration = total_time / segment_count

    def right_hand_side(_time, state):
        x, y, z = state
        return np.asarray(
            (-y - z, x + parameters.a * y, parameters.b + z * (x - parameters.c))
        )

    defects = []
    for index in range(segment_count):
        result = solve_ivp(
            right_hand_side,
            (0.0, duration),
            states[index],
            method=solver.method,
            rtol=solver.rtol,
            atol=solver.atol,
            max_step=solver.max_step,
        )
        if not result.success:
            raise RuntimeError(result.message)
        defects.append(float(np.linalg.norm(result.y[:, -1] - states[index + 1])))
    return np.asarray(defects)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported homoclinic collocation manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    try:
        receipts = [
            load_bound_receipt(binding) for binding in manifest["source_receipts"]
        ]
        warm_binding = manifest["warm_start_receipt"]
        warm = load_bound_receipt(warm_binding)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    if len(receipts) != 2 or not all(row["passed"] for row in receipts):
        raise SystemExit("two qualified ordered source roots are required")

    b_value = float(manifest["fixed_b"])
    reference = RosslerParameters(**manifest["reference_parameters"])
    _eq, _values, reference_stable, reference_plane = eigenspaces(reference)
    stable_branch_sign = int(manifest["stable_branch_sign"])

    def geometry(a_value: float, c_value: float, angle: float):
        parameters = RosslerParameters(a=a_value, b=b_value, c=c_value)
        equilibrium, _eigenvalues, stable, plane = align_local_geometry(
            parameters, reference_stable, reference_plane
        )
        targets = [
            row
            for row in stable_manifold_targets(
                parameters, equilibrium, stable, manifest
            )
            if row["status"] == "completed"
            and row["branch_sign"] == stable_branch_sign
        ]
        if len(targets) != 1:
            raise RuntimeError("unique completed stable target required")
        radius = float(manifest["unstable_seed_radius"])
        direction = np.cos(angle) * plane[:, 0] + np.sin(angle) * plane[:, 1]
        angle_derivative = radius * (
            -np.sin(angle) * plane[:, 0] + np.cos(angle) * plane[:, 1]
        )
        return (
            equilibrium + radius * direction,
            np.asarray(targets[0]["state"], dtype=np.float64),
            angle_derivative,
        )

    previous = np.asarray(
        [
            receipts[0]["final_variables"]["a"],
            receipts[0]["final_variables"]["c"],
        ],
        dtype=np.float64,
    )
    current = np.asarray(
        [
            receipts[1]["final_variables"]["a"],
            receipts[1]["final_variables"]["c"],
        ],
        dtype=np.float64,
    )
    physical_scales = np.asarray(
        [manifest["pseudoarclength"]["scales"]["a"], manifest["pseudoarclength"]["scales"]["c"]],
        dtype=np.float64,
    )
    tangent, predictor = physical_secant_plane(
        previous,
        current,
        physical_scales,
        float(manifest["pseudoarclength"]["desired_c_increment"]),
    )

    warm_variables = warm["final_variables"]
    parameters_guess = np.asarray(
        [
            warm_variables["total_flight_time"],
            warm_variables["a"],
            warm_variables["c"],
            warm_variables["angle"],
        ],
        dtype=np.float64,
    )
    initial_guess, target_guess, _angle_derivative = geometry(
        parameters_guess[1], parameters_guess[2], parameters_guess[3]
    )
    warm_nodes = np.asarray(warm["final_nodes"], dtype=np.float64)
    segment_count = int(warm["segment_count"])
    if warm_nodes.shape != (segment_count - 1, 3):
        raise SystemExit("warm-start node shape mismatch")
    mesh = np.linspace(0.0, 1.0, segment_count + 1)
    state_guess = np.vstack((initial_guess, warm_nodes, target_guess)).T

    derivative_steps = manifest["derivatives"]["absolute_steps"]
    a_step = float(derivative_steps["a"])
    c_step = float(derivative_steps["c"])

    def ode(_mesh, states, parameters):
        total_time, a_value, c_value, _angle = parameters
        return scaled_rossler_flow(states, total_time, a_value, b_value, c_value)

    def ode_jacobian(_mesh, states, parameters):
        total_time, a_value, c_value, _angle = parameters
        field = scaled_rossler_flow(states, 1.0, a_value, b_value, c_value)
        parameter_jacobian = np.zeros((3, 4, states.shape[1]), dtype=np.float64)
        parameter_jacobian[:, 0] = field
        parameter_jacobian[1, 1] = total_time * states[1]
        parameter_jacobian[2, 2] = -total_time * states[2]
        return (
            scaled_rossler_jacobian(states, total_time, a_value, c_value),
            parameter_jacobian,
        )

    def boundary_residual(left, right, parameters):
        _total_time, a_value, c_value, angle = parameters
        initial, target, _angle_derivative = geometry(a_value, c_value, angle)
        arc = float(
            np.dot(
                tangent,
                (np.asarray((a_value, c_value)) - predictor) / physical_scales,
            )
        )
        return np.r_[left - initial, right - target, arc]

    def boundary_jacobian(_left, _right, parameters):
        _total_time, a_value, c_value, angle = parameters
        initial, target, angle_derivative = geometry(a_value, c_value, angle)
        initial_ap, target_ap, _ = geometry(a_value + a_step, c_value, angle)
        initial_am, target_am, _ = geometry(a_value - a_step, c_value, angle)
        initial_cp, target_cp, _ = geometry(a_value, c_value + c_step, angle)
        initial_cm, target_cm, _ = geometry(a_value, c_value - c_step, angle)
        initial_a = (initial_ap - initial_am) / (2.0 * a_step)
        target_a = (target_ap - target_am) / (2.0 * a_step)
        initial_c = (initial_cp - initial_cm) / (2.0 * c_step)
        target_c = (target_cp - target_cm) / (2.0 * c_step)
        left_jacobian = np.zeros((7, 3), dtype=np.float64)
        right_jacobian = np.zeros((7, 3), dtype=np.float64)
        parameter_jacobian = np.zeros((7, 4), dtype=np.float64)
        left_jacobian[:3] = np.eye(3)
        right_jacobian[3:6] = np.eye(3)
        parameter_jacobian[:3, 1] = -initial_a
        parameter_jacobian[:3, 2] = -initial_c
        parameter_jacobian[:3, 3] = -angle_derivative
        parameter_jacobian[3:6, 1] = -target_a
        parameter_jacobian[3:6, 2] = -target_c
        parameter_jacobian[6, 1] = tangent[0] / physical_scales[0]
        parameter_jacobian[6, 2] = tangent[1] / physical_scales[1]
        return left_jacobian, right_jacobian, parameter_jacobian

    collocation = manifest["collocation"]
    started = time.perf_counter()
    result = solve_bvp(
        ode,
        boundary_residual,
        mesh,
        state_guess,
        p=parameters_guess,
        fun_jac=ode_jacobian,
        bc_jac=boundary_jacobian,
        tol=float(collocation["tolerance"]),
        bc_tol=float(collocation["boundary_tolerance"]),
        max_nodes=int(collocation["maximum_nodes"]),
        verbose=0,
    )
    elapsed = time.perf_counter() - started
    total_time, a_value, c_value, angle = map(float, result.p)
    final_parameters = RosslerParameters(a=a_value, b=b_value, c=c_value)
    final_boundary_residual = boundary_residual(result.y[:, 0], result.y[:, -1], result.p)
    replay_mesh = np.linspace(0.0, 1.0, int(manifest["replay"]["segment_count"]) + 1)
    replay_states = result.sol(replay_mesh).T
    replay_solver = SolverConfig(**manifest["replay"]["solver"])
    defects = replay_defects(replay_states, total_time, final_parameters, replay_solver)
    warm_final = result.sol(mesh).T
    node_displacement = float(
        np.max(np.abs((warm_final - state_guess.T) / float(manifest["node_bound_radius"])))
    )
    global_values = np.asarray((total_time, a_value, c_value, angle))
    global_centers = np.asarray(
        (
            parameters_guess[0],
            predictor[0],
            predictor[1],
            parameters_guess[3],
        )
    )
    global_half_widths = np.asarray(
        [
            manifest["global_half_widths"][name]
            for name in ("total_flight_time", "a", "c", "angle")
        ],
        dtype=np.float64,
    )
    global_margins = global_half_widths - np.abs(global_values - global_centers)
    acceptance = manifest["acceptance"]
    maximum_collocation_residual = float(np.max(result.rms_residuals))
    maximum_boundary_residual = float(np.max(np.abs(final_boundary_residual)))
    maximum_replay_defect = float(np.max(defects))
    checks = {
        "source_roots_bound": all(row["passed"] for row in receipts),
        "warm_start_bound": warm["experiment_id"] == warm_binding["experiment_id"],
        "collocation_converged": result.status == 0,
        "finite_result": bool(
            np.all(np.isfinite(result.y))
            and np.all(np.isfinite(result.p))
            and np.all(np.isfinite(defects))
        ),
        "positive_flight_time": total_time > 0.0,
        "forward_c_direction": c_value > current[1],
        "historical_section_crossed": a_value < float(acceptance["historical_section_a"]),
        "boundary_residual": maximum_boundary_residual
        <= float(acceptance["maximum_boundary_residual"]),
        "collocation_residual": maximum_collocation_residual
        <= float(acceptance["maximum_collocation_rms_residual"]),
        "independent_replay": maximum_replay_defect
        <= float(acceptance["maximum_replay_block_defect"]),
        "node_status_bound": 1.0 - node_displacement
        >= float(acceptance["minimum_node_boundary_margin"]),
        "global_status_bound": float(np.min(global_margins))
        >= float(acceptance["minimum_global_boundary_margin"]),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    output = {
        "schema": manifest["output_schema"],
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "source_receipts": [
            {"experiment_id": row["experiment_id"], "sha256": binding["sha256"], "passed": row["passed"]}
            for row, binding in zip(receipts, manifest["source_receipts"], strict=True)
        ],
        "warm_start_receipt": {
            "experiment_id": warm["experiment_id"],
            "sha256": warm_binding["sha256"],
            "passed": warm["passed"],
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "fixed_b": b_value,
        "reference_parameters": manifest["reference_parameters"],
        "physical_tangent": tangent.tolist(),
        "predictor_parameters": {"a": float(predictor[0]), "c": float(predictor[1])},
        "initial_variables": {
            "total_flight_time": float(parameters_guess[0]),
            "a": float(parameters_guess[1]),
            "c": float(parameters_guess[2]),
            "angle": float(parameters_guess[3]),
        },
        "final_variables": {
            "total_flight_time": total_time,
            "a": a_value,
            "c": c_value,
            "angle": angle,
        },
        "collocation": {
            "success": bool(result.success),
            "status": int(result.status),
            "message": str(result.message),
            "iterations": int(result.niter),
            "initial_nodes": int(mesh.size),
            "final_nodes": int(result.x.size),
            "maximum_rms_residual": maximum_collocation_residual,
            "maximum_boundary_residual": maximum_boundary_residual,
        },
        "replay": {
            "segment_count": int(manifest["replay"]["segment_count"]),
            "maximum_block_defect": maximum_replay_defect,
            "block_defects": defects.tolist(),
            "states": replay_states.tolist(),
        },
        "node_boundary_margin": 1.0 - node_displacement,
        "global_boundary_margins": global_margins.tolist(),
        "solution_mesh": result.x.tolist(),
        "solution_states": result.y.T.tolist(),
        "checks": checks,
        "classification": (
            "collocation_bracket_root_nominated"
            if all(checks.values())
            else "collocation_unresolved"
        ),
        "elapsed_seconds": elapsed,
        "passed": all(checks.values()),
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    print(json.dumps(output, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
