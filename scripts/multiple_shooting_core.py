"""Core analytic multiple-shooting equations for periodic Rössler branches."""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares
from scipy.sparse import csr_matrix, lil_matrix, vstack as sparse_vstack

from butterfly import RosslerParameters, SolverConfig, rossler_jacobian, rossler_rhs


def integrate_segment(
    state, duration, parameters, solver, continuation_parameter="b"
):
    if continuation_parameter not in {"a", "b", "c"}:
        raise ValueError("continuation_parameter must be 'a', 'b', or 'c'")
    initial = np.r_[state, np.eye(3).ravel(), np.zeros(3)]

    def augmented(time, value):
        point = value[:3]
        jacobian = rossler_jacobian(point, parameters)
        transition = value[3:12].reshape(3, 3)
        sensitivity = value[12:15]
        if continuation_parameter == "a":
            parameter_forcing = np.asarray((0.0, point[1], 0.0))
        elif continuation_parameter == "b":
            parameter_forcing = np.asarray((0.0, 0.0, 1.0))
        else:
            parameter_forcing = np.asarray((0.0, 0.0, -point[2]))
        return np.r_[
            rossler_rhs(time, point, parameters),
            (jacobian @ transition).ravel(),
            jacobian @ sensitivity + parameter_forcing,
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
    return final[:3], final[3:12].reshape(3, 3), final[12:15]


def integrate_segment_sensitivities(
    state,
    duration,
    parameters,
    solver,
    continuation_parameters=("a", "c"),
):
    """Integrate one arc with simultaneous parameter sensitivities."""
    names = tuple(continuation_parameters)
    if not names or len(set(names)) != len(names):
        raise ValueError("continuation parameters must be unique and nonempty")
    if any(name not in {"a", "b", "c"} for name in names):
        raise ValueError("continuation parameters must be drawn from 'a', 'b', 'c'")
    initial = np.r_[
        state,
        np.eye(3).ravel(),
        np.zeros(3 * len(names)),
    ]

    def forcing(name, point):
        if name == "a":
            return np.asarray((0.0, point[1], 0.0))
        if name == "b":
            return np.asarray((0.0, 0.0, 1.0))
        return np.asarray((0.0, 0.0, -point[2]))

    def augmented(time, value):
        point = value[:3]
        jacobian = rossler_jacobian(point, parameters)
        transition = value[3:12].reshape(3, 3)
        sensitivities = value[12:].reshape(len(names), 3)
        sensitivity_derivatives = [
            jacobian @ sensitivity + forcing(name, point)
            for name, sensitivity in zip(names, sensitivities, strict=True)
        ]
        return np.r_[
            rossler_rhs(time, point, parameters),
            (jacobian @ transition).ravel(),
            np.asarray(sensitivity_derivatives).ravel(),
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
    sensitivities = final[12:].reshape(len(names), 3)
    return (
        final[:3],
        final[3:12].reshape(3, 3),
        {name: sensitivities[index] for index, name in enumerate(names)},
    )


def seed_variables(state, total_duration, b, *, segment_count, a, c, solver):
    parameters = RosslerParameters(a=a, b=b, c=c)
    duration = total_duration / segment_count
    nodes = [np.asarray(state, dtype=float)]
    for _ in range(1, segment_count):
        endpoint, _, _ = integrate_segment(nodes[-1], duration, parameters, solver)
        nodes.append(endpoint)
    return np.r_[np.concatenate(nodes), total_duration, b]


def base_system(
    variables,
    *,
    segment_count,
    a,
    c,
    phase,
    phase_reference,
    solver,
    continuation_parameter="b",
    fixed_b=None,
    sparse_jacobian=False,
):
    nodes = variables[: 3 * segment_count].reshape(segment_count, 3)
    total_duration = float(variables[3 * segment_count])
    parameter_value = float(variables[3 * segment_count + 1])
    duration = total_duration / segment_count
    if continuation_parameter == "a":
        if fixed_b is None or c is None:
            raise ValueError("fixed b and c are required when continuing a")
        parameters = RosslerParameters(a=parameter_value, b=fixed_b, c=c)
    elif continuation_parameter == "b":
        if a is None or c is None:
            raise ValueError("fixed a and c are required when continuing b")
        parameters = RosslerParameters(a=a, b=parameter_value, c=c)
    elif continuation_parameter == "c":
        if a is None or fixed_b is None:
            raise ValueError("fixed a and b are required when continuing c")
        parameters = RosslerParameters(a=a, b=fixed_b, c=parameter_value)
    else:
        raise ValueError("continuation_parameter must be 'a', 'b', or 'c'")
    rows = 3 * segment_count + 1
    columns = 3 * segment_count + 2
    residual = np.empty(rows)
    jacobian = (
        lil_matrix((rows, columns), dtype=float)
        if sparse_jacobian
        else np.zeros((rows, columns))
    )
    for index, node in enumerate(nodes):
        endpoint, transition, sensitivity = integrate_segment(
            node,
            duration,
            parameters,
            solver,
            continuation_parameter=continuation_parameter,
        )
        next_index = (index + 1) % segment_count
        row = slice(3 * index, 3 * index + 3)
        current = slice(3 * index, 3 * index + 3)
        following = slice(3 * next_index, 3 * next_index + 3)
        residual[row] = endpoint - nodes[next_index]
        jacobian[row, current] += transition
        jacobian[row, following] -= np.eye(3)
        jacobian[row, 3 * segment_count] = rossler_rhs(
            duration, endpoint, parameters
        ) / segment_count
        jacobian[row, 3 * segment_count + 1] = sensitivity
    residual[-1] = float(np.dot(phase, nodes[0] - phase_reference))
    jacobian[-1, :3] = phase
    return residual, jacobian.tocsr() if sparse_jacobian else jacobian


def correct_arclength(
    predictor,
    tangent,
    *,
    segment_count,
    a,
    c,
    phase,
    phase_reference,
    solver,
    tolerance,
    max_evaluations,
    continuation_parameter="b",
    fixed_b=None,
    sparse_jacobian=False,
):
    cached_variables = None
    cached_residual = None
    cached_jacobian = None

    def evaluate(variables):
        nonlocal cached_variables, cached_residual, cached_jacobian
        if cached_variables is not None and np.array_equal(variables, cached_variables):
            return cached_residual, cached_jacobian
        base_residual, base_jacobian = base_system(
            variables,
            segment_count=segment_count,
            a=a,
            c=c,
            phase=phase,
            phase_reference=phase_reference,
            solver=solver,
            continuation_parameter=continuation_parameter,
            fixed_b=fixed_b,
            sparse_jacobian=sparse_jacobian,
        )
        residual = np.r_[base_residual, np.dot(tangent, variables - predictor)]
        jacobian = (
            sparse_vstack(
                (base_jacobian, csr_matrix(tangent.reshape(1, -1))),
                format="csr",
            )
            if sparse_jacobian
            else np.vstack((base_jacobian, tangent))
        )
        cached_variables = variables.copy()
        cached_residual = residual
        cached_jacobian = jacobian
        return residual, jacobian

    lower = np.full(len(predictor), -np.inf)
    upper = np.full(len(predictor), np.inf)
    lower[3 * segment_count] = 1e-12
    solution = least_squares(
        lambda value: evaluate(value)[0],
        predictor,
        jac=lambda value: evaluate(value)[1],
        bounds=(lower, upper),
        xtol=tolerance,
        ftol=tolerance,
        gtol=tolerance,
        max_nfev=max_evaluations,
        x_scale="jac",
    )
    residual, _ = evaluate(solution.x)
    matching = residual[: 3 * segment_count]
    return solution.x, {
        "success": bool(
            solution.success
            and np.linalg.norm(matching) <= 1e-8
            and abs(residual[3 * segment_count]) <= 1e-8
            and abs(residual[-1]) <= 1e-8
        ),
        "message": solution.message,
        "evaluations": int(solution.nfev),
        "matching_residual": float(np.linalg.norm(matching)),
        "phase_residual": float(abs(residual[3 * segment_count])),
        "arclength_residual": float(abs(residual[-1])),
    }


def correct_fixed_b(
    initial_variables,
    fixed_b,
    *,
    segment_count,
    a,
    c,
    phase,
    phase_reference,
    solver,
    tolerance,
    max_evaluations,
):
    """Correct cyclic nodes and total duration while holding ``b`` fixed."""
    cached_variables = None
    cached_residual = None
    cached_jacobian = None

    def evaluate(variables):
        nonlocal cached_variables, cached_residual, cached_jacobian
        if cached_variables is not None and np.array_equal(variables, cached_variables):
            return cached_residual, cached_jacobian
        extended = np.r_[variables, fixed_b]
        residual, jacobian = base_system(
            extended,
            segment_count=segment_count,
            a=a,
            c=c,
            phase=phase,
            phase_reference=phase_reference,
            solver=solver,
        )
        cached_variables = variables.copy()
        cached_residual = residual
        cached_jacobian = jacobian[:, :-1]
        return cached_residual, cached_jacobian

    lower = np.full(len(initial_variables), -np.inf)
    upper = np.full(len(initial_variables), np.inf)
    lower[3 * segment_count] = 1e-12
    solution = least_squares(
        lambda value: evaluate(value)[0],
        initial_variables,
        jac=lambda value: evaluate(value)[1],
        bounds=(lower, upper),
        xtol=tolerance,
        ftol=tolerance,
        gtol=tolerance,
        max_nfev=max_evaluations,
        x_scale="jac",
    )
    residual, _ = evaluate(solution.x)
    matching = residual[: 3 * segment_count]
    return solution.x, {
        "success": bool(
            solution.success
            and np.linalg.norm(matching) <= 1e-8
            and abs(residual[-1]) <= 1e-8
        ),
        "message": solution.message,
        "evaluations": int(solution.nfev),
        "matching_residual": float(np.linalg.norm(matching)),
        "phase_residual": float(abs(residual[-1])),
    }


def correct_fixed_parameter(
    initial_variables,
    fixed_parameter,
    *,
    segment_count,
    a,
    c,
    phase,
    phase_reference,
    solver,
    tolerance,
    max_evaluations,
    continuation_parameter="b",
    fixed_b=None,
    sparse_jacobian=False,
):
    """Correct cyclic nodes and duration while holding the chosen parameter."""

    cached_variables = None
    cached_residual = None
    cached_jacobian = None

    def evaluate(variables):
        nonlocal cached_variables, cached_residual, cached_jacobian
        if cached_variables is not None and np.array_equal(variables, cached_variables):
            return cached_residual, cached_jacobian
        extended = np.r_[variables, fixed_parameter]
        residual, jacobian = base_system(
            extended,
            segment_count=segment_count,
            a=a,
            c=c,
            phase=phase,
            phase_reference=phase_reference,
            solver=solver,
            continuation_parameter=continuation_parameter,
            fixed_b=fixed_b,
            sparse_jacobian=sparse_jacobian,
        )
        cached_variables = variables.copy()
        cached_residual = residual
        cached_jacobian = jacobian[:, :-1]
        return cached_residual, cached_jacobian

    lower = np.full(len(initial_variables), -np.inf)
    upper = np.full(len(initial_variables), np.inf)
    lower[3 * segment_count] = 1e-12
    solution = least_squares(
        lambda value: evaluate(value)[0],
        initial_variables,
        jac=lambda value: evaluate(value)[1],
        bounds=(lower, upper),
        xtol=tolerance,
        ftol=tolerance,
        gtol=tolerance,
        max_nfev=max_evaluations,
        x_scale="jac",
    )
    residual, _ = evaluate(solution.x)
    matching = residual[: 3 * segment_count]
    return solution.x, {
        "success": bool(
            solution.success
            and np.linalg.norm(matching) <= 1e-8
            and abs(residual[-1]) <= 1e-8
        ),
        "message": solution.message,
        "evaluations": int(solution.nfev),
        "matching_residual": float(np.linalg.norm(matching)),
        "phase_residual": float(abs(residual[-1])),
    }
