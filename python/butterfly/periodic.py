"""Periodic-orbit diagnostics from flow returns and variational monodromy."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.integrate import solve_ivp

from .integrate import SolverConfig
from .models import RosslerParameters, rossler_jacobian, rossler_rhs


@dataclass(frozen=True, slots=True)
class MonodromyResult:
    period_time: float
    final_state: NDArray[np.float64]
    closure_error: float
    monodromy: NDArray[np.float64]
    multipliers: NDArray[np.complex128]
    divergence_integral: float
    predicted_determinant: float
    computed_determinant: float
    success: bool
    message: str


def flow_monodromy(
    parameters: RosslerParameters,
    initial_state: ArrayLike,
    period_time: float,
    *,
    config: SolverConfig = SolverConfig(),
) -> MonodromyResult:
    """Integrate one proposed period with the full flow variational matrix.

    The routine diagnoses an already localized orbit; it does not solve the
    periodic shooting equations. One multiplier of a true autonomous-flow
    periodic orbit should approach one. Strong contraction can make the
    smallest multiplier unrecoverable in Float64, so both the computed and
    divergence-predicted determinants are retained.
    """

    state = np.asarray(initial_state, dtype=np.float64)
    if state.shape != (3,) or not np.all(np.isfinite(state)):
        raise ValueError("initial_state must contain three finite values")
    if not np.isfinite(period_time) or period_time <= 0.0:
        raise ValueError("period_time must be positive and finite")
    initial = np.concatenate((state, np.eye(3, dtype=np.float64).ravel(), (0.0,)))

    def augmented_rhs(
        time: float, augmented: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        current_state = augmented[:3]
        tangent = augmented[3:12].reshape(3, 3)
        return np.concatenate(
            (
                rossler_rhs(time, current_state, parameters),
                (rossler_jacobian(current_state, parameters) @ tangent).ravel(),
                (parameters.a + current_state[0] - parameters.c,),
            )
        )

    integration = solve_ivp(
        augmented_rhs,
        (0.0, period_time),
        initial,
        method=config.method,
        rtol=config.rtol,
        atol=config.atol,
        max_step=config.max_step,
    )
    final = np.asarray(integration.y[:, -1], dtype=np.float64)
    final_state = final[:3]
    monodromy = final[3:12].reshape(3, 3)
    divergence_integral = float(final[12])
    multipliers = np.linalg.eigvals(monodromy).astype(np.complex128)
    return MonodromyResult(
        period_time=float(period_time),
        final_state=final_state,
        closure_error=float(np.linalg.norm(final_state - state)),
        monodromy=monodromy,
        multipliers=multipliers,
        divergence_integral=divergence_integral,
        predicted_determinant=float(np.exp(divergence_integral)),
        computed_determinant=float(np.linalg.det(monodromy)),
        success=bool(integration.success),
        message=str(integration.message),
    )
