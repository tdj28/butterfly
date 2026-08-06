"""Reference Lyapunov spectrum using variational equations and periodic QR."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.integrate import solve_ivp

from .integrate import SolverConfig, integrate_trajectory
from .models import RosslerParameters, rossler_jacobian, rossler_rhs


@dataclass(frozen=True, slots=True)
class LyapunovConfig:
    transient: float = 100.0
    duration: float = 1000.0
    qr_interval: float = 0.5
    solver: SolverConfig = SolverConfig()

    def __post_init__(self) -> None:
        if self.transient < 0.0 or self.duration <= 0.0 or self.qr_interval <= 0.0:
            raise ValueError("transient must be nonnegative; duration/QR interval positive")


@dataclass(frozen=True, slots=True)
class LyapunovResult:
    exponents: NDArray[np.float64]
    running_exponents: NDArray[np.float64]
    mean_divergence: float
    trace_identity_error: float
    final_state: NDArray[np.float64]
    elapsed: float
    qr_steps: int
    success: bool
    message: str


def lyapunov_spectrum(
    parameters: RosslerParameters,
    initial_state: ArrayLike,
    *,
    config: LyapunovConfig = LyapunovConfig(),
) -> LyapunovResult:
    """Compute the full finite-time Lyapunov spectrum in Float64.

    The state and a 3x3 tangent basis are integrated together. The tangent basis
    is orthonormalized every ``qr_interval`` and logarithms of the absolute QR
    diagonal are accumulated. The divergence integral provides an independent
    trace-identity diagnostic: the sum of exponents should equal mean divergence.
    """

    state = np.asarray(initial_state, dtype=np.float64)
    if state.shape != (3,) or not np.all(np.isfinite(state)):
        raise ValueError("initial_state must be three finite values")

    if config.transient > 0.0:
        transient_result = integrate_trajectory(
            parameters,
            state,
            (0.0, config.transient),
            config=config.solver,
        )
        if not transient_result.success:
            return LyapunovResult(
                exponents=np.full(3, np.nan),
                running_exponents=np.empty((0, 3), dtype=np.float64),
                mean_divergence=np.nan,
                trace_identity_error=np.nan,
                final_state=np.asarray(transient_result.y[:, -1], dtype=np.float64),
                elapsed=0.0,
                qr_steps=0,
                success=False,
                message=f"transient integration failed: {transient_result.message}",
            )
        state = np.asarray(transient_result.y[:, -1], dtype=np.float64)

    basis = np.eye(3, dtype=np.float64)
    log_sums = np.zeros(3, dtype=np.float64)
    divergence_integral = 0.0
    history: list[NDArray[np.float64]] = []
    elapsed = 0.0
    intervals = math.ceil(config.duration / config.qr_interval)

    for _index in range(intervals):
        interval = min(config.qr_interval, config.duration - elapsed)
        if interval <= np.finfo(np.float64).eps * config.duration:
            break
        initial = np.concatenate((state, basis.ravel(), np.asarray((0.0,))))

        def augmented_rhs(
            time: float, augmented: NDArray[np.float64]
        ) -> NDArray[np.float64]:
            current_state = augmented[:3]
            tangent = augmented[3:12].reshape(3, 3)
            state_derivative = rossler_rhs(time, current_state, parameters)
            tangent_derivative = rossler_jacobian(
                current_state, parameters
            ) @ tangent
            divergence = parameters.a + current_state[0] - parameters.c
            return np.concatenate(
                (state_derivative, tangent_derivative.ravel(), (divergence,))
            )

        integration = solve_ivp(
            augmented_rhs,
            (0.0, interval),
            initial,
            method=config.solver.method,
            rtol=config.solver.rtol,
            atol=config.solver.atol,
            max_step=config.solver.max_step,
        )
        if not integration.success:
            exponents = log_sums / elapsed if elapsed > 0.0 else np.full(3, np.nan)
            mean_divergence = (
                divergence_integral / elapsed if elapsed > 0.0 else np.nan
            )
            return LyapunovResult(
                exponents=exponents,
                running_exponents=np.asarray(history, dtype=np.float64),
                mean_divergence=float(mean_divergence),
                trace_identity_error=float(abs(np.sum(exponents) - mean_divergence)),
                final_state=state,
                elapsed=elapsed,
                qr_steps=len(history),
                success=False,
                message=f"variational integration failed: {integration.message}",
            )

        final = np.asarray(integration.y[:, -1], dtype=np.float64)
        state = final[:3]
        propagated = final[3:12].reshape(3, 3)
        divergence_integral += float(final[12])
        basis, triangular = np.linalg.qr(propagated)
        diagonal = np.diag(triangular)
        if np.any(np.abs(diagonal) <= np.finfo(np.float64).tiny):
            return LyapunovResult(
                exponents=np.full(3, np.nan),
                running_exponents=np.asarray(history, dtype=np.float64),
                mean_divergence=np.nan,
                trace_identity_error=np.nan,
                final_state=state,
                elapsed=elapsed,
                qr_steps=len(history),
                success=False,
                message="tangent basis became numerically singular",
            )
        signs = np.sign(diagonal)
        signs[signs == 0.0] = 1.0
        basis = basis * signs
        log_sums += np.log(np.abs(diagonal))
        elapsed += interval
        history.append((log_sums / elapsed).copy())

    exponents = log_sums / elapsed
    mean_divergence = divergence_integral / elapsed
    return LyapunovResult(
        exponents=exponents,
        running_exponents=np.asarray(history, dtype=np.float64),
        mean_divergence=float(mean_divergence),
        trace_identity_error=float(abs(np.sum(exponents) - mean_divergence)),
        final_state=state,
        elapsed=elapsed,
        qr_steps=len(history),
        success=True,
        message="completed requested finite-time spectrum",
    )
