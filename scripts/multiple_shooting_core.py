"""Core analytic multiple-shooting equations for periodic Rössler branches."""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

from butterfly import RosslerParameters, SolverConfig, rossler_jacobian, rossler_rhs


def integrate_segment(state, duration, parameters, solver):
    initial = np.r_[state, np.eye(3).ravel(), np.zeros(3)]

    def augmented(time, value):
        point = value[:3]
        jacobian = rossler_jacobian(point, parameters)
        transition = value[3:12].reshape(3, 3)
        sensitivity = value[12:15]
        return np.r_[
            rossler_rhs(time, point, parameters),
            (jacobian @ transition).ravel(),
            jacobian @ sensitivity + np.asarray((0.0, 0.0, 1.0)),
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


def seed_variables(state, total_duration, b, *, segment_count, a, c, solver):
    parameters = RosslerParameters(a=a, b=b, c=c)
    duration = total_duration / segment_count
    nodes = [np.asarray(state, dtype=float)]
    for _ in range(1, segment_count):
        endpoint, _, _ = integrate_segment(nodes[-1], duration, parameters, solver)
        nodes.append(endpoint)
    return np.r_[np.concatenate(nodes), total_duration, b]


def base_system(variables, *, segment_count, a, c, phase, phase_reference, solver):
    nodes = variables[: 3 * segment_count].reshape(segment_count, 3)
    total_duration = float(variables[3 * segment_count])
    b = float(variables[3 * segment_count + 1])
    duration = total_duration / segment_count
    parameters = RosslerParameters(a=a, b=b, c=c)
    rows = 3 * segment_count + 1
    columns = 3 * segment_count + 2
    residual = np.empty(rows)
    jacobian = np.zeros((rows, columns))
    for index, node in enumerate(nodes):
        endpoint, transition, sensitivity = integrate_segment(
            node, duration, parameters, solver
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
    return residual, jacobian


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
        )
        residual = np.r_[base_residual, np.dot(tangent, variables - predictor)]
        jacobian = np.vstack((base_jacobian, tangent))
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
        ),
        "message": solution.message,
        "evaluations": int(solution.nfev),
        "matching_residual": float(np.linalg.norm(matching)),
        "phase_residual": float(abs(residual[3 * segment_count])),
        "arclength_residual": float(abs(residual[-1])),
    }
