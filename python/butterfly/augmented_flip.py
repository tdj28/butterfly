"""Exact second-variational equations for segmented Rössler flip events."""

from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

from .integrate import SolverConfig
from .models import RosslerParameters, rossler_jacobian, rossler_rhs


def rossler_hessian_action(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Return ``D²f[left, right]`` for the Rössler vector field.

    Only ``f_z = b + z(x-c)`` is nonlinear, so the Hessian action is sparse
    and independent of the current state and parameters.
    """

    left = np.asarray(left, dtype=float)
    right = np.asarray(right, dtype=float)
    return np.asarray(
        (0.0, 0.0, left[2] * right[0] + left[0] * right[2]),
        dtype=float,
    )


def integrate_flip_segment(
    state: np.ndarray,
    tangent: np.ndarray,
    duration: float,
    parameters: RosslerParameters,
    solver: SolverConfig,
    continuation_parameter: str = "b",
):
    """Integrate a segment and all derivatives needed by the flip system.

    Returns the endpoint, state transition, endpoint parameter sensitivity,
    transported tangent, its initial-state Jacobian, and its parameter
    sensitivity. ``continuation_parameter`` may be ``"b"`` or ``"c"``.
    The latter two quantities are exact second-variational actions for the
    Rössler equations.
    """

    if continuation_parameter not in {"b", "c"}:
        raise ValueError("continuation_parameter must be 'b' or 'c'")

    initial = np.r_[
        state,
        np.eye(3).ravel(),
        np.zeros(3),
        tangent,
        np.zeros(9),
        np.zeros(3),
    ]

    def augmented(time, value):
        point = value[:3]
        transition = value[3:12].reshape(3, 3)
        parameter_sensitivity = value[12:15]
        transported = value[15:18]
        state_tangent_sensitivity = value[18:27].reshape(3, 3)
        parameter_tangent_sensitivity = value[27:30]
        jacobian = rossler_jacobian(point, parameters)
        state_tangent_forcing = np.column_stack(
            [
                rossler_hessian_action(transition[:, index], transported)
                for index in range(3)
            ]
        )
        parameter_tangent_forcing = rossler_hessian_action(
            parameter_sensitivity, transported
        )
        if continuation_parameter == "b":
            vector_field_parameter = np.asarray((0.0, 0.0, 1.0))
            jacobian_parameter_action = np.zeros(3)
        else:
            vector_field_parameter = np.asarray((0.0, 0.0, -point[2]))
            jacobian_parameter_action = np.asarray((0.0, 0.0, -transported[2]))
        return np.r_[
            rossler_rhs(time, point, parameters),
            (jacobian @ transition).ravel(),
            jacobian @ parameter_sensitivity + vector_field_parameter,
            jacobian @ transported,
            (
                jacobian @ state_tangent_sensitivity + state_tangent_forcing
            ).ravel(),
            jacobian @ parameter_tangent_sensitivity
            + parameter_tangent_forcing
            + jacobian_parameter_action,
        ]

    result = solve_ivp(
        augmented,
        (0.0, duration),
        initial,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
    )
    if not result.success:
        raise RuntimeError(result.message)
    final = result.y[:, -1]
    return (
        final[:3],
        final[3:12].reshape(3, 3),
        final[12:15],
        final[15:18],
        final[18:27].reshape(3, 3),
        final[27:30],
    )


def augmented_flip_system(
    variables: np.ndarray,
    *,
    segment_count: int,
    a: float,
    c: float | None,
    phase: np.ndarray,
    phase_reference: np.ndarray,
    solver: SolverConfig,
    continuation_parameter: str = "b",
    fixed_b: float | None = None,
):
    """Return the square anti-periodic multiple-shooting residual and Jacobian.

    The historical/default form continues ``b`` at fixed ``(a,c)``.  Setting
    ``continuation_parameter="c"`` instead interprets the parameter unknown as
    ``c`` and requires ``fixed_b``.
    """

    state_count = 3 * segment_count
    variable_count = 6 * segment_count + 2
    if np.shape(variables) != (variable_count,):
        raise ValueError(f"expected {variable_count} variables")
    nodes = variables[:state_count].reshape(segment_count, 3)
    total_duration = float(variables[state_count])
    parameter_value = float(variables[state_count + 1])
    tangent_offset = state_count + 2
    tangents = variables[tangent_offset:].reshape(segment_count, 3)
    segment_duration = total_duration / segment_count
    if continuation_parameter == "b":
        if c is None:
            raise ValueError("fixed c is required when continuing b")
        parameters = RosslerParameters(a=a, b=parameter_value, c=c)
    elif continuation_parameter == "c":
        if fixed_b is None:
            raise ValueError("fixed_b is required when continuing c")
        parameters = RosslerParameters(a=a, b=fixed_b, c=parameter_value)
    else:
        raise ValueError("continuation_parameter must be 'b' or 'c'")
    residual = np.zeros(variable_count)
    jacobian = np.zeros((variable_count, variable_count))

    for index, (node, tangent) in enumerate(zip(nodes, tangents, strict=True)):
        (
            endpoint,
            transition,
            parameter_sensitivity,
            transported,
            state_tangent_sensitivity,
            parameter_tangent_sensitivity,
        ) = integrate_flip_segment(
            node,
            tangent,
            segment_duration,
            parameters,
            solver,
            continuation_parameter=continuation_parameter,
        )
        next_index = (index + 1) % segment_count
        current_state = slice(3 * index, 3 * index + 3)
        next_state = slice(3 * next_index, 3 * next_index + 3)
        orbit_rows = slice(3 * index, 3 * index + 3)
        residual[orbit_rows] = endpoint - nodes[next_index]
        jacobian[orbit_rows, current_state] += transition
        jacobian[orbit_rows, next_state] -= np.eye(3)
        jacobian[orbit_rows, state_count] = (
            rossler_rhs(segment_duration, endpoint, parameters) / segment_count
        )
        jacobian[orbit_rows, state_count + 1] = parameter_sensitivity

        tangent_rows = slice(state_count + 1 + 3 * index, state_count + 4 + 3 * index)
        current_tangent = slice(
            tangent_offset + 3 * index, tangent_offset + 3 * index + 3
        )
        next_tangent = slice(
            tangent_offset + 3 * next_index, tangent_offset + 3 * next_index + 3
        )
        residual[tangent_rows] = transported
        jacobian[tangent_rows, current_state] += state_tangent_sensitivity
        jacobian[tangent_rows, current_tangent] += transition
        jacobian[tangent_rows, state_count] = (
            rossler_jacobian(endpoint, parameters) @ transported / segment_count
        )
        jacobian[tangent_rows, state_count + 1] = parameter_tangent_sensitivity
        if index + 1 < segment_count:
            residual[tangent_rows] -= tangents[next_index]
            jacobian[tangent_rows, next_tangent] -= np.eye(3)
        else:
            residual[tangent_rows] += tangents[0]
            jacobian[tangent_rows, tangent_offset : tangent_offset + 3] += np.eye(3)

    residual[state_count] = float(np.dot(phase, nodes[0] - phase_reference))
    jacobian[state_count, :3] = phase
    residual[-1] = float(np.dot(tangents[0], tangents[0]) - 1.0)
    jacobian[-1, tangent_offset : tangent_offset + 3] = 2.0 * tangents[0]
    return residual, jacobian
