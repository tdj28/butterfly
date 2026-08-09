"""Single-shooting continuation of periodic Rössler orbits in ``c``.

The flow is integrated with an adaptive ODE solver.  Newton-style least
squares is used only to correct the finite-dimensional periodic-orbit and
pseudo-arclength equations; it is not a replacement for time integration.
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

from .integrate import SolverConfig
from .models import RosslerParameters, rossler_jacobian, rossler_rhs
from .periodic import flow_monodromy


def _flow_transition_c_sensitivity(
    state: np.ndarray,
    duration: float,
    parameters: RosslerParameters,
    solver: SolverConfig,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    initial = np.r_[state, np.eye(3).ravel(), np.zeros(3)]

    def augmented_rhs(time: float, augmented: np.ndarray) -> np.ndarray:
        current = augmented[:3]
        jacobian = rossler_jacobian(current, parameters)
        transition = augmented[3:12].reshape(3, 3)
        sensitivity = augmented[12:15]
        # f_c = (0, 0, -z) for z' = b + z (x - c).
        forcing = np.asarray((0.0, 0.0, -current[2]))
        return np.r_[
            rossler_rhs(time, current, parameters),
            (jacobian @ transition).ravel(),
            jacobian @ sensitivity + forcing,
        ]

    result = solve_ivp(
        augmented_rhs,
        (0.0, duration),
        initial,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
    )
    if not result.success:
        raise RuntimeError(f"periodic c-sensitivity integration failed: {result.message}")
    final = np.asarray(result.y[:, -1], dtype=float)
    return final[:3], final[3:12].reshape(3, 3), final[12:15]


def extended_shooting_jacobian_c(
    variables: np.ndarray,
    *,
    a: float,
    b: float,
    phase_direction: np.ndarray,
    solver: SolverConfig,
) -> np.ndarray:
    """Jacobian of closure plus phase with variables ``(x0, T, c)``."""

    state = np.asarray(variables[:3], dtype=float)
    duration = float(variables[3])
    c = float(variables[4])
    parameters = RosslerParameters(a=a, b=b, c=c)
    final_state, transition, sensitivity = _flow_transition_c_sensitivity(
        state, duration, parameters, solver
    )
    jacobian = np.zeros((4, 5), dtype=float)
    jacobian[:3, :3] = transition - np.eye(3)
    jacobian[:3, 3] = rossler_rhs(duration, final_state, parameters)
    jacobian[:3, 4] = sensitivity
    jacobian[3, :3] = phase_direction
    return jacobian


def correct_arclength_c(
    predictor: np.ndarray,
    tangent: np.ndarray,
    reference_state: np.ndarray,
    reference_c: float,
    *,
    a: float,
    b: float,
    solver: SolverConfig,
    tolerance: float,
    max_evaluations: int,
) -> tuple[np.ndarray, dict]:
    """Correct a periodic orbit subject to a pseudo-arclength condition."""

    phase_parameters = RosslerParameters(a=a, b=b, c=reference_c)
    phase_direction = rossler_rhs(0.0, reference_state, phase_parameters)
    phase_direction /= np.linalg.norm(phase_direction)
    cached_variables = None
    cached_residual = None
    cached_jacobian = None

    def evaluate(variables: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        nonlocal cached_variables, cached_residual, cached_jacobian
        if cached_variables is not None and np.array_equal(variables, cached_variables):
            return cached_residual, cached_jacobian
        state = np.asarray(variables[:3], dtype=float)
        duration = float(variables[3])
        c = float(variables[4])
        parameters = RosslerParameters(a=a, b=b, c=c)
        final_state, transition, sensitivity = _flow_transition_c_sensitivity(
            state, duration, parameters, solver
        )
        residual = np.r_[
            final_state - state,
            np.dot(phase_direction, state - reference_state),
            np.dot(tangent, variables - predictor),
        ]
        jacobian = np.empty((5, 5), dtype=float)
        jacobian[:3, :3] = transition - np.eye(3)
        jacobian[:3, 3] = rossler_rhs(duration, final_state, parameters)
        jacobian[:3, 4] = sensitivity
        jacobian[3, :3] = phase_direction
        jacobian[3, 3:] = 0.0
        jacobian[4, :] = tangent
        cached_variables = variables.copy()
        cached_residual = residual
        cached_jacobian = jacobian
        return residual, jacobian

    solution = least_squares(
        lambda variables: evaluate(variables)[0],
        predictor,
        jac=lambda variables: evaluate(variables)[1],
        bounds=(
            np.asarray((-np.inf, -np.inf, -np.inf, 1e-12, -np.inf)),
            np.full(5, np.inf),
        ),
        xtol=tolerance,
        ftol=tolerance,
        gtol=tolerance,
        max_nfev=max_evaluations,
        x_scale="jac",
    )
    residual, _ = evaluate(solution.x)
    return np.asarray(solution.x), {
        "success": bool(solution.success and np.linalg.norm(residual[:3]) <= 1e-8),
        "message": str(solution.message),
        "evaluations": int(solution.nfev),
        "closure_error": float(np.linalg.norm(residual[:3])),
        "phase_residual": float(abs(residual[3])),
        "arclength_residual": float(abs(residual[4])),
    }


def diagnose_periodic_c(
    variables: np.ndarray,
    *,
    a: float,
    b: float,
    solver: SolverConfig,
) -> dict:
    state = np.asarray(variables[:3], dtype=float)
    duration = float(variables[3])
    c = float(variables[4])
    parameters = RosslerParameters(a=a, b=b, c=c)
    monodromy = flow_monodromy(parameters, state, duration, config=solver)
    neutral_index = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
    nontrivial = np.delete(monodromy.multipliers, neutral_index)
    dominant = complex(nontrivial[int(np.argmax(np.abs(nontrivial)))])
    return {
        "parameters": {"a": a, "b": b, "c": c},
        "initial_state": state.tolist(),
        "period_time": duration,
        "closure_error": monodromy.closure_error,
        "neutral_multiplier_error": float(
            abs(monodromy.multipliers[neutral_index] - 1.0)
        ),
        "dominant_nontrivial_multiplier": {
            "real": float(dominant.real),
            "imag": float(dominant.imag),
            "modulus": float(abs(dominant)),
        },
        "max_nontrivial_multiplier_modulus": float(np.max(np.abs(nontrivial))),
    }
