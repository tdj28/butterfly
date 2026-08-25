#!/usr/bin/env python3
"""Continue Jones's homoclinic boundary-value root in both a and c."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import least_squares

from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes

try:
    from scripts.multiple_shooting_core import (
        integrate_segment,
        integrate_segment_sensitivities,
    )
    from scripts.scan_jones_homoclinic_manifold_match import (
        align_local_geometry,
        stable_manifold_targets,
    )
    from scripts.scan_jones_homoclinic_unstable_angles import eigenspaces
    from scripts.solve_jones_homoclinic_multiple_shooting import block_norms, node_bounds
except ModuleNotFoundError:  # Direct ``python scripts/...`` execution.
    from multiple_shooting_core import (
        integrate_segment,
        integrate_segment_sensitivities,
    )
    from scan_jones_homoclinic_manifold_match import (
        align_local_geometry,
        stable_manifold_targets,
    )
    from scan_jones_homoclinic_unstable_angles import eigenspaces
    from solve_jones_homoclinic_multiple_shooting import block_norms, node_bounds


SCHEMA = "butterfly.jones-homoclinic-pseudoarclength-manifest.v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def variable_layout(segment_count: int) -> dict[str, int]:
    if segment_count < 2:
        raise ValueError("pseudo-arclength shooting requires at least two arcs")
    node_count = segment_count - 1
    node_size = 3 * node_count
    return {
        "node_count": node_count,
        "node_size": node_size,
        "time_index": node_size,
        "a_index": node_size + 1,
        "c_index": node_size + 2,
        "angle_index": node_size + 3,
        "variable_count": node_size + 4,
    }


def subdivide_bound_nodes(
    source_nodes: np.ndarray,
    initial: np.ndarray,
    total_time: float,
    parameters: RosslerParameters,
    solver: SolverConfig,
    target_segment_count: int,
) -> np.ndarray:
    """Subdivide every exact source arc to a common finer representation."""
    source_nodes = np.asarray(source_nodes, dtype=np.float64)
    source_segment_count = len(source_nodes) + 1
    if target_segment_count % source_segment_count:
        raise ValueError("target segmentation must be a multiple of source segmentation")
    factor = target_segment_count // source_segment_count
    if factor < 1:
        raise ValueError("target segmentation cannot be coarser than the source")
    if factor == 1:
        return source_nodes.copy()
    target_dt = total_time / target_segment_count
    source_starts = np.vstack((np.asarray(initial, dtype=np.float64), source_nodes))
    rows = []
    for source_index, source_start in enumerate(source_starts):
        current = source_start
        for _subindex in range(1, factor):
            current, _transition, _sensitivity = integrate_segment(
                current,
                target_dt,
                parameters,
                solver,
                continuation_parameter="a",
            )
            rows.append(current)
        if source_index < source_segment_count - 1:
            rows.append(source_nodes[source_index])
    result = np.asarray(rows, dtype=np.float64)
    expected_shape = (target_segment_count - 1, 3)
    if result.shape != expected_shape:
        raise RuntimeError("subdivided node shape mismatch")
    return result


def unwrap_angle(previous: float, current: float) -> float:
    """Choose the previous angular representative nearest the current one."""
    return current + ((previous - current + np.pi) % (2.0 * np.pi) - np.pi)


def native_boolean_checks(checks: dict) -> dict:
    """Convert NumPy comparison results at the JSON receipt boundary."""
    return {name: bool(value) for name, value in checks.items()}


def source_curve_values(receipt: dict) -> tuple[float, float, float, float]:
    """Read ``(a, c, angle, T)`` from fixed-c or pseudo-arclength receipts."""
    variables = receipt["final_variables"]
    if "c" in variables:
        c_value = variables["c"]
    elif "fixed_parameters" in receipt and "c" in receipt["fixed_parameters"]:
        c_value = receipt["fixed_parameters"]["c"]
    else:
        raise ValueError("source receipt does not bind a curve c coordinate")
    return (
        float(variables["a"]),
        float(c_value),
        float(variables["angle"]),
        float(variables["total_flight_time"]),
    )


def source_angle_gauge(
    receipt: dict, binding: dict, *, fixed_b: float
) -> RosslerParameters:
    """Recover the eigenspace reference used to encode a source angle."""
    if "reference_parameters" in receipt:
        values = receipt["reference_parameters"]
    elif "angle_gauge_reference_parameters" in binding:
        values = binding["angle_gauge_reference_parameters"]
    elif "fixed_parameters" in receipt and "c" in receipt["fixed_parameters"]:
        # Legacy fixed-c multiple-shooting receipts used this reference by
        # construction but did not serialize it explicitly.
        values = {"a": 0.1798, "b": fixed_b, "c": receipt["fixed_parameters"]["c"]}
    else:
        raise ValueError("pseudo-arclength source angle gauge is not bound")
    gauge = RosslerParameters(**values)
    if gauge.b != fixed_b:
        raise ValueError("source angle gauge has inconsistent fixed b")
    return gauge


def directional_c_bounds(
    current_c: float,
    predictor_c: float,
    half_width: float,
    minimum_increment: float | None,
) -> tuple[float, float]:
    """Return predictor-centered c bounds with an optional forward floor."""
    lower = predictor_c - half_width
    upper = predictor_c + half_width
    if minimum_increment is not None:
        if minimum_increment <= 0.0:
            raise ValueError("minimum c increment must be positive")
        lower = max(lower, current_c + minimum_increment)
    if lower >= predictor_c or predictor_c >= upper:
        raise ValueError("directional c bounds exclude the predictor")
    return lower, upper


def projected_arclength_tangent(
    delta: np.ndarray,
    scales: np.ndarray,
    layout: dict[str, int],
    components: tuple[str, ...],
) -> np.ndarray:
    """Normalize a secant after projecting onto declared variable groups."""
    supported = {"nodes", "total_flight_time", "a", "c", "angle"}
    unknown = set(components) - supported
    if unknown:
        raise ValueError(f"unsupported arclength components: {sorted(unknown)}")
    tangent = np.asarray(delta, dtype=np.float64) / np.asarray(scales, dtype=np.float64)
    mask = np.zeros_like(tangent, dtype=bool)
    if "nodes" in components:
        mask[: layout["node_size"]] = True
    for name, index_name in (
        ("total_flight_time", "time_index"),
        ("a", "a_index"),
        ("c", "c_index"),
        ("angle", "angle_index"),
    ):
        if name in components:
            mask[layout[index_name]] = True
    tangent[~mask] = 0.0
    norm = np.linalg.norm(tangent)
    if not np.isfinite(norm) or norm == 0.0:
        raise ValueError("projected arclength tangent is degenerate")
    return tangent / norm


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported homoclinic pseudo-arclength manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    receipts = []
    for binding in manifest["source_receipts"]:
        path = Path(binding["path"])
        if sha256_file(path) != binding["sha256"]:
            raise SystemExit(f"source receipt hash mismatch: {path}")
        receipt = json.loads(path.read_bytes())
        for field in ("schema", "experiment_id", "passed", "classification"):
            if receipt.get(field) != binding[field]:
                raise SystemExit(f"source receipt binding mismatch: {field}")
        failed_checks = sorted(
            key for key, value in receipt.get("checks", {}).items() if value is False
        )
        if failed_checks != binding["failed_checks"]:
            raise SystemExit("source failed-check binding mismatch")
        for field, expected in binding["expected"].items():
            if receipt.get(field) != expected:
                raise SystemExit(f"source value binding mismatch: {field}")
        receipts.append(receipt)
    if len(receipts) != 2:
        raise SystemExit("exactly two ordered source receipts are required")
    previous_receipt, current_receipt = receipts

    b_value = float(manifest["fixed_b"])
    solver = SolverConfig(**manifest["solver"])
    segment_count = int(manifest["segment_count"])
    layout = variable_layout(segment_count)
    stable_branch_sign = int(manifest["stable_branch_sign"])
    reference = RosslerParameters(**manifest["reference_parameters"])
    _equilibrium, _values, reference_stable, reference_plane = eigenspaces(reference)

    def geometry(a_value: float, c_value: float, angle: float):
        parameters = RosslerParameters(a=a_value, b=b_value, c=c_value)
        equilibrium, _values, stable, plane = align_local_geometry(
            parameters, reference_stable, reference_plane
        )
        targets = [
            row
            for row in stable_manifold_targets(parameters, equilibrium, stable, manifest)
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
        initial = equilibrium + radius * direction
        return initial, np.asarray(targets[0]["state"], dtype=np.float64), angle_derivative

    def source_vector(receipt: dict, binding: dict) -> np.ndarray:
        a_value, c_value, source_angle, total_flight_time = source_curve_values(
            receipt
        )
        source_reference = source_angle_gauge(receipt, binding, fixed_b=b_value)
        _eq, _ev, old_stable, old_plane = eigenspaces(source_reference)
        parameters = RosslerParameters(a=a_value, b=b_value, c=c_value)
        old_equilibrium, _ev2, _stable2, aligned_old_plane = align_local_geometry(
            parameters, old_stable, old_plane
        )
        old_direction = (
            np.cos(source_angle) * aligned_old_plane[:, 0]
            + np.sin(source_angle) * aligned_old_plane[:, 1]
        )
        common_equilibrium, _ev3, _stable3, common_plane = align_local_geometry(
            parameters, reference_stable, reference_plane
        )
        if not np.allclose(old_equilibrium, common_equilibrium, rtol=0.0, atol=1e-12):
            raise RuntimeError("source equilibrium alignment mismatch")
        common_angle = float(
            np.arctan2(
                np.dot(old_direction, common_plane[:, 1]),
                np.dot(old_direction, common_plane[:, 0]),
            )
        )
        initial, _target, _angle_derivative = geometry(a_value, c_value, common_angle)
        nodes = subdivide_bound_nodes(
            np.asarray(receipt["final_nodes"], dtype=np.float64),
            initial,
            total_flight_time,
            parameters,
            solver,
            segment_count,
        )
        return np.r_[
            nodes.ravel(),
            total_flight_time,
            a_value,
            c_value,
            common_angle,
        ]

    previous = source_vector(previous_receipt, manifest["source_receipts"][0])
    current = source_vector(current_receipt, manifest["source_receipts"][1])
    previous[layout["angle_index"]] = unwrap_angle(
        previous[layout["angle_index"]], current[layout["angle_index"]]
    )

    scaling = manifest["pseudoarclength"]["scales"]
    scales = np.full(layout["variable_count"], float(scaling["node_component"]))
    scales[layout["time_index"]] = float(scaling["total_flight_time"])
    scales[layout["a_index"]] = float(scaling["a"])
    scales[layout["c_index"]] = float(scaling["c"])
    scales[layout["angle_index"]] = float(scaling["angle"])
    all_components = ("nodes", "total_flight_time", "a", "c", "angle")
    predictor_tangent = projected_arclength_tangent(
        current - previous, scales, layout, all_components
    )
    arclength_components = tuple(
        manifest["pseudoarclength"].get("arclength_components", all_components)
    )
    arclength_tangent = projected_arclength_tangent(
        current - previous, scales, layout, arclength_components
    )
    desired_c_increment = float(manifest["pseudoarclength"]["desired_c_increment"])
    c_direction = (
        predictor_tangent[layout["c_index"]] * scales[layout["c_index"]]
    )
    if c_direction * desired_c_increment <= 0.0:
        predictor_tangent *= -1.0
        arclength_tangent *= -1.0
        c_direction *= -1.0
    arclength_step = desired_c_increment / c_direction
    predictor = current + arclength_step * predictor_tangent * scales

    node_radius = float(manifest["node_bound_radius"])
    lower = np.full(layout["variable_count"], -np.inf)
    upper = np.full(layout["variable_count"], np.inf)
    current_nodes = current[: layout["node_size"]].reshape(layout["node_count"], 3)
    lower[: layout["node_size"]], upper[: layout["node_size"]] = node_bounds(
        current_nodes, node_radius
    )
    global_half_widths = manifest["global_half_widths"]
    for name, index in (
        ("total_flight_time", layout["time_index"]),
        ("a", layout["a_index"]),
        ("c", layout["c_index"]),
        ("angle", layout["angle_index"]),
    ):
        half_width = float(global_half_widths[name])
        lower[index] = predictor[index] - half_width
        upper[index] = predictor[index] + half_width
    directional = manifest.get("directional_bounds", {})
    minimum_c_increment = directional.get("minimum_c_increment")
    lower[layout["c_index"]], upper[layout["c_index"]] = directional_c_bounds(
        float(current[layout["c_index"]]),
        float(predictor[layout["c_index"]]),
        float(global_half_widths["c"]),
        None if minimum_c_increment is None else float(minimum_c_increment),
    )
    if not np.all((predictor > lower) & (predictor < upper)):
        raise SystemExit("pseudo-arclength predictor lies outside frozen bounds")

    parameter_steps = manifest["derivatives"]["absolute_steps"]
    a_step = float(parameter_steps["a"])
    c_step = float(parameter_steps["c"])
    arc_weight = float(manifest["pseudoarclength"]["residual_weight"])
    history = []
    cached_point = cached_residual = cached_jacobian = cached_details = None

    def compute(variables: np.ndarray):
        nonlocal cached_point, cached_residual, cached_jacobian, cached_details
        variables = np.asarray(variables, dtype=np.float64)
        if cached_point is not None and np.array_equal(variables, cached_point):
            return cached_residual, cached_jacobian, cached_details
        nodes = variables[: layout["node_size"]].reshape(layout["node_count"], 3)
        total_time = float(variables[layout["time_index"]])
        a_value = float(variables[layout["a_index"]])
        c_value = float(variables[layout["c_index"]])
        angle = float(variables[layout["angle_index"]])
        parameters = RosslerParameters(a=a_value, b=b_value, c=c_value)
        initial, target, initial_angle_derivative = geometry(a_value, c_value, angle)
        initial_ap, target_ap, _ = geometry(a_value + a_step, c_value, angle)
        initial_am, target_am, _ = geometry(a_value - a_step, c_value, angle)
        initial_cp, target_cp, _ = geometry(a_value, c_value + c_step, angle)
        initial_cm, target_cm, _ = geometry(a_value, c_value - c_step, angle)
        initial_derivatives = {
            "a": (initial_ap - initial_am) / (2.0 * a_step),
            "c": (initial_cp - initial_cm) / (2.0 * c_step),
        }
        target_derivatives = {
            "a": (target_ap - target_am) / (2.0 * a_step),
            "c": (target_cp - target_cm) / (2.0 * c_step),
        }
        segment_time = total_time / segment_count
        matching = np.empty(3 * segment_count)
        jacobian = np.zeros((3 * segment_count + 1, layout["variable_count"]))
        endpoints = []
        for index in range(segment_count):
            start = initial if index == 0 else nodes[index - 1]
            endpoint, transition, sensitivities = integrate_segment_sensitivities(
                start,
                segment_time,
                parameters,
                solver,
                continuation_parameters=("a", "c"),
            )
            destination = target if index + 1 == segment_count else nodes[index]
            row = slice(3 * index, 3 * index + 3)
            matching[row] = endpoint - destination
            if index > 0:
                jacobian[row, slice(3 * (index - 1), 3 * index)] = transition
            if index + 1 < segment_count:
                jacobian[row, slice(3 * index, 3 * index + 3)] -= np.eye(3)
            jacobian[row, layout["time_index"]] = (
                rossler_rhs(segment_time, endpoint, parameters) / segment_count
            )
            for name, parameter_index in (
                ("a", layout["a_index"]),
                ("c", layout["c_index"]),
            ):
                jacobian[row, parameter_index] = sensitivities[name]
                if index == 0:
                    jacobian[row, parameter_index] += (
                        transition @ initial_derivatives[name]
                    )
                if index + 1 == segment_count:
                    jacobian[row, parameter_index] -= target_derivatives[name]
            if index == 0:
                jacobian[row, layout["angle_index"]] = (
                    transition @ initial_angle_derivative
                )
            endpoints.append(endpoint)
        arc_residual = float(
            np.dot(arclength_tangent, (variables - predictor) / scales)
        )
        residual = np.r_[matching, arc_weight * arc_residual]
        jacobian[-1] = arc_weight * arclength_tangent / scales
        norms = block_norms(matching)
        details = {
            "matching_residual_norm": float(np.linalg.norm(matching)),
            "maximum_block_norm": float(np.max(norms)),
            "block_norms": norms,
            "arclength_residual": arc_residual,
            "endpoint": np.asarray(endpoints[-1]).tolist(),
            "stable_target": target.tolist(),
        }
        history.append(
            {
                "evaluation": len(history),
                "a": a_value,
                "c": c_value,
                "angle": angle,
                "total_flight_time": total_time,
                "maximum_block_norm": details["maximum_block_norm"],
                "arclength_residual": arc_residual,
            }
        )
        cached_point = variables.copy()
        cached_residual = residual
        cached_jacobian = jacobian
        cached_details = details
        return residual, jacobian, details

    initial_residual, _initial_jacobian, initial_details = compute(predictor)
    optimization = manifest["optimization"]
    started = time.perf_counter()
    result = least_squares(
        lambda value: compute(value)[0],
        predictor,
        jac=lambda value: compute(value)[1],
        bounds=(lower, upper),
        method="trf",
        x_scale="jac",
        ftol=float(optimization["ftol"]),
        xtol=float(optimization["xtol"]),
        gtol=float(optimization["gtol"]),
        max_nfev=int(optimization["maximum_function_evaluations"]),
    )
    elapsed = time.perf_counter() - started
    final_residual, final_jacobian, final_details = compute(result.x)
    final_nodes = result.x[: layout["node_size"]].reshape(layout["node_count"], 3)
    node_displacement = float(np.max(np.abs((final_nodes - current_nodes) / node_radius)))
    node_margin = 1.0 - node_displacement
    global_margins = []
    for index in (
        layout["time_index"],
        layout["a_index"],
        layout["c_index"],
        layout["angle_index"],
    ):
        global_margins.append(float(min(result.x[index] - lower[index], upper[index] - result.x[index])))
    acceptance = manifest["acceptance"]
    root_nominated = bool(
        final_details["maximum_block_norm"]
        <= float(acceptance["maximum_root_block_residual"])
        and abs(final_details["arclength_residual"])
        <= float(acceptance["maximum_arclength_residual"])
        and min(global_margins) >= float(acceptance["minimum_global_boundary_margin"])
        and node_margin >= float(acceptance["minimum_node_boundary_margin"])
    )
    checks = {
        "source_roots_bound": all(receipt["passed"] for receipt in receipts),
        "initial_residual": initial_details["maximum_block_norm"]
        <= float(acceptance["maximum_initial_block_residual"]),
        "optimizer_terminated_or_root_gate": bool(
            result.status != 0
            or (acceptance.get("allow_root_gate_as_termination", False) and root_nominated)
        ),
        "evaluation_budget": result.nfev
        <= int(optimization["maximum_function_evaluations"]),
        "finite_result": bool(
            np.all(np.isfinite(result.x))
            and np.all(np.isfinite(final_residual))
            and np.all(np.isfinite(final_jacobian))
        ),
        "positive_flight_time": result.x[layout["time_index"]] > 0.0,
        "node_status_bound": node_margin
        >= float(acceptance["minimum_node_boundary_margin"]),
        "global_status_bound": min(global_margins)
        >= float(acceptance["minimum_global_boundary_margin"]),
        "forward_c_direction": result.x[layout["c_index"]]
        > current[layout["c_index"]],
        "root_nominated": root_nominated,
    }
    checks = native_boolean_checks(checks)
    singular_values = np.linalg.svd(final_jacobian, compute_uv=False)
    output = {
        "schema": manifest["output_schema"],
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "source_receipts": [
            {
                "experiment_id": receipt["experiment_id"],
                "sha256": binding["sha256"],
                "passed": receipt["passed"],
            }
            for receipt, binding in zip(receipts, manifest["source_receipts"], strict=True)
        ],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "fixed_b": b_value,
        "reference_parameters": manifest["reference_parameters"],
        "matching_radius": manifest["matching_radius"],
        "segment_count": segment_count,
        "previous_variables": {
            "a": float(previous[layout["a_index"]]),
            "c": float(previous[layout["c_index"]]),
            "angle": float(previous[layout["angle_index"]]),
            "total_flight_time": float(previous[layout["time_index"]]),
        },
        "current_variables": {
            "a": float(current[layout["a_index"]]),
            "c": float(current[layout["c_index"]]),
            "angle": float(current[layout["angle_index"]]),
            "total_flight_time": float(current[layout["time_index"]]),
        },
        "predictor_variables": {
            "a": float(predictor[layout["a_index"]]),
            "c": float(predictor[layout["c_index"]]),
            "angle": float(predictor[layout["angle_index"]]),
            "total_flight_time": float(predictor[layout["time_index"]]),
        },
        "final_variables": {
            "a": float(result.x[layout["a_index"]]),
            "c": float(result.x[layout["c_index"]]),
            "angle": float(result.x[layout["angle_index"]]),
            "total_flight_time": float(result.x[layout["time_index"]]),
        },
        "desired_c_increment": desired_c_increment,
        "arclength_components": list(arclength_components),
        "directional_bounds": directional,
        "normalized_arclength_step": float(arclength_step),
        "initial_maximum_block_residual": initial_details["maximum_block_norm"],
        "initial_arclength_residual": initial_details["arclength_residual"],
        "final_residual_norm": float(np.linalg.norm(final_residual)),
        "final_matching_residual_norm": final_details["matching_residual_norm"],
        "final_maximum_block_residual": final_details["maximum_block_norm"],
        "final_arclength_residual": final_details["arclength_residual"],
        "final_block_residual_norms": final_details["block_norms"].tolist(),
        "final_nodes": final_nodes.tolist(),
        "final_endpoint": final_details["endpoint"],
        "final_stable_target": final_details["stable_target"],
        "node_bound_radius": node_radius,
        "maximum_normalized_node_displacement": node_displacement,
        "node_boundary_margin": node_margin,
        "global_boundary_margins": global_margins,
        "jacobian_singular_values": singular_values.tolist(),
        "optimizer": {
            "success": bool(result.success),
            "status": int(result.status),
            "message": str(result.message),
            "cost": float(result.cost),
            "optimality": float(result.optimality),
            "nfev": int(result.nfev),
            "njev": None if result.njev is None else int(result.njev),
        },
        "history": history,
        "root_nominated": root_nominated,
        "classification": (
            "pseudoarclength_root_nominated"
            if root_nominated
            else "pseudoarclength_unresolved"
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
