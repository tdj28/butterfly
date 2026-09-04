"""Finite-interval homoclinic collocation with asymptotic projection boundaries.

This is a new endpoint formulation, not the archived matching-sphere residual.
The left endpoint lies in the unstable linear eigenspace and the right in the
stable linear eigenspace. Two endpoint radii fix departure/arrival phases;
one system parameter and the flight time are unknown. The linear endpoint
approximation must be tested by shrinking both radii: small collocation
residuals alone do not establish a homoclinic limit or parameter accuracy.

SciPy supplies fourth-order adaptive collocation; this is not AUTO/HomCont.
"""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Callable, Any

import numpy as np
from scipy.integrate import solve_bvp, solve_ivp
from scipy.linalg import schur
from scipy.optimize import brentq


@dataclass(frozen=True)
class HomoclinicModel:
    name: str
    dimension: int
    field: Callable[[np.ndarray, float], np.ndarray]
    state_jacobian: Callable[[np.ndarray, float], np.ndarray]
    parameter_derivative: Callable[[np.ndarray, float], np.ndarray]
    equilibrium: Callable[[float], np.ndarray]


@dataclass(frozen=True)
class ParameterBox:
    lower: tuple[float, float]
    upper: tuple[float, float]

    def __post_init__(self):
        lower, upper = np.asarray(self.lower), np.asarray(self.upper)
        if lower.shape != (2,) or upper.shape != (2,):
            raise ValueError("parameter/time bounds must each contain two entries")
        if not np.all(np.isfinite([lower, upper])) or np.any(upper <= lower):
            raise ValueError("parameter/time bounds must be finite and increasing")
        if lower[1] <= 0.0:
            raise ValueError("flight-time bounds must be positive")

    def decode(self, transformed):
        transformed = np.asarray(transformed, dtype=float)
        if transformed.shape != (2,) or not np.all(np.isfinite(transformed)):
            raise ValueError("transformed parameters must be finite")
        lower, upper = np.asarray(self.lower), np.asarray(self.upper)
        half = (upper - lower) / 2.0
        unit = np.tanh(transformed)
        physical = np.clip((lower + upper) / 2.0 + half * unit, lower, upper)
        return physical, half * (1.0 - unit**2)

    def encode(self, physical):
        lower, upper = np.asarray(self.lower), np.asarray(self.upper)
        unit = (2.0 * np.asarray(physical) - lower - upper) / (upper - lower)
        if not np.all(np.isfinite(unit)) or np.any(np.abs(unit) >= 1.0):
            raise ValueError("initial parameter/time must be strictly inside bounds")
        return np.arctanh(unit)


def projection_complements(jacobian: np.ndarray):
    """Orthogonal complements of unstable/stable invariant subspaces.

    Separate ordered real Schur decompositions are essential for nonnormal
    Jacobians: right stable eigenvectors need not be orthogonal to right
    unstable eigenvectors.
    """
    values = np.linalg.eigvals(jacobian)
    if np.any(np.abs(values.real) < 1e-8):
        raise ValueError("projection boundaries require a hyperbolic equilibrium")
    _tu, qu, unstable_count = schur(jacobian, output="real", sort=lambda re, im: re > 0.0)
    _ts, qs, stable_count = schur(jacobian, output="real", sort=lambda re, im: re < 0.0)
    if min(stable_count, unstable_count) == 0 or stable_count + unstable_count != len(jacobian):
        raise ValueError("a hyperbolic saddle with stable and unstable directions is required")
    return qu[:, unstable_count:], qs[:, stable_count:]


def _align_columns(current, reference):
    left, _singular, right = np.linalg.svd(current.T @ reference)
    return current @ (left @ right)


class ProjectionBoundary:
    def __init__(self, model: HomoclinicModel, reference_parameter: float, radii):
        self.model = model
        self.radii = np.asarray(radii, dtype=float)
        if self.radii.shape != (2,) or not np.all(np.isfinite(self.radii)) or np.any(self.radii <= 0.0):
            raise ValueError("two finite positive endpoint radii are required")
        self.reference = self._geometry(reference_parameter)[1:]

    def _geometry(self, parameter):
        equilibrium = self.model.equilibrium(parameter)
        jacobian = self.model.state_jacobian(equilibrium[:, None], parameter)[:, :, 0]
        left, right = projection_complements(jacobian)
        return equilibrium, left, right

    def geometry(self, parameter):
        equilibrium, left, right = self._geometry(parameter)
        return equilibrium, _align_columns(left, self.reference[0]), _align_columns(right, self.reference[1])

    def residual(self, left_state, right_state, parameter):
        equilibrium, left, right = self.geometry(parameter)
        departure = (left_state - equilibrium) / self.radii[0]
        arrival = (right_state - equilibrium) / self.radii[1]
        return np.r_[
            left.T @ departure,
            right.T @ arrival,
            (np.dot(departure, departure) - 1.0) / 2.0,
            (np.dot(arrival, arrival) - 1.0) / 2.0,
        ]


def solve_projected_homoclinic(
    model: HomoclinicModel,
    mesh: np.ndarray,
    states: np.ndarray,
    *,
    parameter: float,
    flight_time: float,
    radii: tuple[float, float],
    box: ParameterBox,
    tolerance: float = 1e-5,
    boundary_tolerance: float = 1e-8,
    maximum_nodes: int = 16000,
    maximum_seconds: float = 45.0,
    maximum_state_norm: float = 1000.0,
) -> tuple[Any | None, dict]:
    """Solve a finite BVP; fail with diagnostics on runaway or exhausted budget."""
    if not all(np.isfinite(v) and v > 0.0 for v in (tolerance, boundary_tolerance, maximum_seconds, maximum_state_norm)):
        raise ValueError("solver tolerances and budgets must be finite and positive")
    mesh, states = np.asarray(mesh), np.asarray(states)
    if mesh.ndim != 1 or len(mesh) < 3 or mesh[0] != 0.0 or mesh[-1] != 1.0 or np.any(np.diff(mesh) <= 0.0):
        raise ValueError("mesh must increase from zero to one")
    if states.shape != (model.dimension, len(mesh)) or not np.all(np.isfinite(states)):
        raise ValueError("initial states must have finite shape (dimension, mesh size)")
    if maximum_nodes < len(mesh):
        raise ValueError("initial mesh exceeds node budget")
    boundary = ProjectionBoundary(model, parameter, radii)
    guess = box.encode((parameter, flight_time))
    started = time.monotonic()
    last_parameters = [float(parameter), float(flight_time)]

    def guard(values, transformed):
        if time.monotonic() - started > maximum_seconds:
            raise TimeoutError("collocation wall-clock budget exhausted")
        if not np.all(np.isfinite(values)) or np.max(np.linalg.norm(values, axis=0)) > maximum_state_norm:
            raise ValueError("collocation state left its declared finite domain")
        physical, derivative = box.decode(transformed)
        last_parameters[:] = physical.tolist()
        return physical, derivative

    def ode(_mesh, values, transformed):
        (current_parameter, duration), _derivative = guard(values, transformed)
        return duration * model.field(values, current_parameter)

    def ode_jacobian(_mesh, values, transformed):
        (current_parameter, duration), derivative = guard(values, transformed)
        parameter_jacobian = np.empty((model.dimension, 2, values.shape[1]))
        parameter_jacobian[:, 0] = duration * model.parameter_derivative(values, current_parameter) * derivative[0]
        parameter_jacobian[:, 1] = model.field(values, current_parameter) * derivative[1]
        return duration * model.state_jacobian(values, current_parameter), parameter_jacobian

    def bc(left, right, transformed):
        (current_parameter, _duration), _derivative = guard(np.column_stack((left, right)), transformed)
        return boundary.residual(left, right, current_parameter)

    def bc_jacobian(left_state, right_state, transformed):
        (current_parameter, _duration), _derivative = guard(np.column_stack((left_state, right_state)), transformed)
        equilibrium, left, right = boundary.geometry(current_parameter)
        count = model.dimension + 2
        left_jacobian, right_jacobian = np.zeros((count, model.dimension)), np.zeros((count, model.dimension))
        left_jacobian[:left.shape[1]] = left.T / radii[0]
        right_jacobian[left.shape[1]:model.dimension] = right.T / radii[1]
        left_jacobian[-2] = (left_state - equilibrium) / radii[0]**2
        right_jacobian[-1] = (right_state - equilibrium) / radii[1]**2
        parameter_jacobian = np.zeros((count, 2))
        offset = np.asarray((1e-4, 0.0))
        parameter_jacobian[:, 0] = (bc(left_state, right_state, transformed + offset) - bc(left_state, right_state, transformed - offset)) / (2e-4)
        return left_jacobian, right_jacobian, parameter_jacobian

    try:
        result = solve_bvp(
            ode, bc, mesh, states, p=guess, fun_jac=ode_jacobian,
            bc_jac=bc_jacobian, tol=tolerance, bc_tol=boundary_tolerance,
            max_nodes=maximum_nodes,
        )
        physical, _derivative = box.decode(result.p)
        values = result.y
        guard(values, result.p)
        residual = bc(values[:, 0], values[:, -1], result.p)
        margins = np.minimum(physical - np.asarray(box.lower), np.asarray(box.upper) - physical) / (np.asarray(box.upper) - np.asarray(box.lower))
        summary = {
            "solver_success": bool(result.success), "solver_status": int(result.status),
            "message": str(result.message), "parameter": float(physical[0]),
            "flight_time": float(physical[1]), "nodes": len(result.x),
            "iterations": int(result.niter),
            "maximum_scaled_boundary_residual": float(np.max(np.abs(residual))),
            "maximum_collocation_relative_rms": float(np.max(result.rms_residuals)),
            "minimum_parameter_box_margin": float(np.min(margins)),
            "maximum_excursion": float(np.max(np.linalg.norm(values - model.equilibrium(physical[0])[:, None], axis=0))),
            "endpoint_radii": np.linalg.norm(values[:, [0, -1]] - model.equilibrium(physical[0])[:, None], axis=0).tolist(),
        }
        summary["passed_numerical_gates"] = bool(
            result.success and summary["maximum_scaled_boundary_residual"] <= boundary_tolerance
            and summary["maximum_collocation_relative_rms"] <= tolerance
            and summary["minimum_parameter_box_margin"] > 1e-4
        )
        summary["elapsed_seconds"] = time.monotonic() - started
        return result, summary
    except (ValueError, TimeoutError, RuntimeError, FloatingPointError) as error:
        return None, {
            "solver_success": False, "passed_numerical_gates": False,
            "message": f"{type(error).__name__}: {error}",
            "last_parameter": last_parameters[0], "last_flight_time": last_parameters[1],
            "elapsed_seconds": time.monotonic() - started,
        }


def duffing_model() -> HomoclinicModel:
    def field(values, damping):
        x, y = values
        return np.vstack((y, x - x**3 + damping * y))

    def jacobian(values, damping):
        result = np.zeros((2, 2, values.shape[1]))
        result[0, 1] = 1.0
        result[1, 0] = 1.0 - 3.0 * values[0]**2
        result[1, 1] = damping
        return result

    return HomoclinicModel(
        "damped-duffing", 2, field, jacobian,
        lambda values, _damping: np.vstack((np.zeros(values.shape[1]), values[1])),
        lambda _damping: np.zeros(2),
    )


def duffing_homoclinic(times):
    times = np.asarray(times)
    x = np.sqrt(2.0) / np.cosh(times)
    return np.asarray((x, -x * np.tanh(times)))


def duffing_seed(radius: float, count: int = 201):
    if not np.isfinite(radius) or not 0.0 < radius < 1.0:
        raise ValueError("Duffing control radius must lie in (0,1)")
    half_time = brentq(lambda value: np.linalg.norm(duffing_homoclinic(value)) - radius, 0.0, 50.0)
    mesh = np.linspace(0.0, 1.0, count)
    return mesh, duffing_homoclinic((2.0 * mesh - 1.0) * half_time), 2.0 * half_time


def rossler_bvp_model(b: float, c: float) -> HomoclinicModel:
    # Independently written vectorized equations; no manifold-matching imports.
    def equilibrium(a):
        discriminant = c * c - 4.0 * a * b
        if discriminant <= 0.0 or c <= 0.0:
            raise ValueError("this pilot requires the positive-c hyperbolic small equilibrium")
        z = 2.0 * b / (c + np.sqrt(discriminant))
        return np.asarray((a * z, -z, z))

    def field(values, a):
        x, y, z = values
        return np.vstack((-y - z, x + a * y, b + z * (x - c)))

    def jacobian(values, a):
        result = np.zeros((3, 3, values.shape[1]))
        result[0, 1:3] = -1.0
        result[1, 0] = 1.0
        result[1, 1] = a
        result[2, 0] = values[2]
        result[2, 2] = values[0] - c
        return result

    return HomoclinicModel(
        "rossler-fixed-b-c", 3, field, jacobian,
        lambda values, _a: np.vstack((np.zeros(values.shape[1]), values[1], np.zeros(values.shape[1]))),
        equilibrium,
    )


def local_replay_defects(model, solution, parameter, flight_time, *, segments=128, method="DOP853", rtol=1e-10, atol=1e-12, maximum_step=0.05, deadline=None):
    """Diagnostic IVP replay of short pieces; never a long unstable replay."""
    mesh = np.linspace(0.0, 1.0, segments + 1)
    states = solution.sol(mesh)
    duration = flight_time / segments
    errors = []
    for index in range(segments):
        def field(_time, value):
            if deadline is not None and time.monotonic() > deadline:
                raise TimeoutError("total pilot budget exhausted during local replay")
            return model.field(value[:, None], parameter)[:, 0]

        try:
            trial = solve_ivp(
                field, (0.0, duration), states[:, index], method=method, rtol=rtol, atol=atol,
                max_step=min(maximum_step, duration),
            )
        except TimeoutError as error:
            return {"success": False, "failed_segment": index, "message": str(error)}
        if not trial.success:
            return {"success": False, "failed_segment": index, "message": str(trial.message)}
        errors.append(float(np.linalg.norm(trial.y[:, -1] - states[:, index + 1])))
    return {"success": True, "segments": segments, "maximum_state_defect": max(errors), "rms_state_defect": float(np.sqrt(np.mean(np.square(errors))))}
