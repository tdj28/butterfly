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
    running_times: NDArray[np.float64]
    mean_divergence: float
    trace_identity_error: float
    final_state: NDArray[np.float64]
    elapsed: float
    qr_steps: int
    success: bool
    message: str


@dataclass(frozen=True, slots=True)
class LargestLyapunovResult:
    exponent: float
    running_exponent: NDArray[np.float64]
    final_state: NDArray[np.float64]
    elapsed: float
    renormalizations: int
    perturbation: float
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
                running_times=np.empty(0, dtype=np.float64),
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
    history_times: list[float] = []
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
                running_times=np.asarray(history_times, dtype=np.float64),
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
                running_times=np.asarray(history_times, dtype=np.float64),
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
        history_times.append(elapsed)

    exponents = log_sums / elapsed
    mean_divergence = divergence_integral / elapsed
    return LyapunovResult(
        exponents=exponents,
        running_exponents=np.asarray(history, dtype=np.float64),
        running_times=np.asarray(history_times, dtype=np.float64),
        mean_divergence=float(mean_divergence),
        trace_identity_error=float(abs(np.sum(exponents) - mean_divergence)),
        final_state=state,
        elapsed=elapsed,
        qr_steps=len(history),
        success=True,
        message="completed requested finite-time spectrum",
    )


def lyapunov_block_estimates(
    result: LyapunovResult, *, blocks: int = 6
) -> NDArray[np.float64]:
    """Recover nonoverlapping block estimates from cumulative QR estimates."""

    if blocks < 2:
        raise ValueError("at least two blocks are required")
    if result.qr_steps < blocks or len(result.running_times) != result.qr_steps:
        raise ValueError("result does not contain enough complete QR history")
    edges = np.linspace(0, result.qr_steps, blocks + 1, dtype=int)
    cumulative = result.running_exponents * result.running_times[:, None]
    cumulative = np.vstack((np.zeros((1, 3), dtype=np.float64), cumulative))
    times = np.concatenate(([0.0], result.running_times))
    estimates = []
    for start, stop in zip(edges[:-1], edges[1:]):
        duration = times[stop] - times[start]
        estimates.append((cumulative[stop] - cumulative[start]) / duration)
    return np.asarray(estimates, dtype=np.float64)


def largest_lyapunov_two_trajectory(
    parameters: RosslerParameters,
    initial_state: ArrayLike,
    *,
    config: LyapunovConfig = LyapunovConfig(),
    perturbation: float = 1e-8,
    initial_direction: ArrayLike = (1.0, np.sqrt(2.0), np.pi),
) -> LargestLyapunovResult:
    """Estimate the largest exponent without Jacobians or tangent equations.

    A reference and nearby nonlinear trajectory are evolved together. After
    each interval their separation growth is accumulated and the perturbed
    trajectory is reset to the declared distance from the reference trajectory.
    This is an independent algorithmic cross-check of the largest variational
    exponent, though it still shares the declared ODE solver.
    """

    state = np.asarray(initial_state, dtype=np.float64)
    direction = np.asarray(initial_direction, dtype=np.float64)
    if state.shape != (3,) or not np.all(np.isfinite(state)):
        raise ValueError("initial_state must be three finite values")
    if direction.shape != (3,) or not np.all(np.isfinite(direction)):
        raise ValueError("initial_direction must be three finite values")
    direction_norm = np.linalg.norm(direction)
    if direction_norm == 0.0 or perturbation <= 0.0:
        raise ValueError("initial_direction and perturbation must be nonzero/positive")

    if config.transient > 0.0:
        transient_result = integrate_trajectory(
            parameters,
            state,
            (0.0, config.transient),
            config=config.solver,
        )
        if not transient_result.success:
            return LargestLyapunovResult(
                exponent=np.nan,
                running_exponent=np.empty(0, dtype=np.float64),
                final_state=state,
                elapsed=0.0,
                renormalizations=0,
                perturbation=perturbation,
                success=False,
                message=f"transient integration failed: {transient_result.message}",
            )
        state = np.asarray(transient_result.y[:, -1], dtype=np.float64)

    perturbed = state + perturbation * direction / direction_norm
    log_sum = 0.0
    elapsed = 0.0
    history: list[float] = []
    intervals = math.ceil(config.duration / config.qr_interval)

    for _index in range(intervals):
        interval = min(config.qr_interval, config.duration - elapsed)
        if interval <= np.finfo(np.float64).eps * config.duration:
            break

        def pair_rhs(time: float, pair: NDArray[np.float64]) -> NDArray[np.float64]:
            return np.concatenate(
                (
                    rossler_rhs(time, pair[:3], parameters),
                    rossler_rhs(time, pair[3:], parameters),
                )
            )

        integration = solve_ivp(
            pair_rhs,
            (0.0, interval),
            np.concatenate((state, perturbed)),
            method=config.solver.method,
            rtol=config.solver.rtol,
            atol=config.solver.atol,
            max_step=config.solver.max_step,
        )
        if not integration.success:
            return LargestLyapunovResult(
                exponent=log_sum / elapsed if elapsed > 0.0 else np.nan,
                running_exponent=np.asarray(history, dtype=np.float64),
                final_state=state,
                elapsed=elapsed,
                renormalizations=len(history),
                perturbation=perturbation,
                success=False,
                message=f"paired integration failed: {integration.message}",
            )
        final = np.asarray(integration.y[:, -1], dtype=np.float64)
        state = final[:3]
        separation = final[3:] - state
        distance = float(np.linalg.norm(separation))
        if not np.isfinite(distance) or distance == 0.0:
            return LargestLyapunovResult(
                exponent=np.nan,
                running_exponent=np.asarray(history, dtype=np.float64),
                final_state=state,
                elapsed=elapsed,
                renormalizations=len(history),
                perturbation=perturbation,
                success=False,
                message="trajectory separation became zero or non-finite",
            )
        log_sum += math.log(distance / perturbation)
        elapsed += interval
        history.append(log_sum / elapsed)
        perturbed = state + perturbation * separation / distance

    return LargestLyapunovResult(
        exponent=log_sum / elapsed,
        running_exponent=np.asarray(history, dtype=np.float64),
        final_state=state,
        elapsed=elapsed,
        renormalizations=len(history),
        perturbation=perturbation,
        success=True,
        message="completed two-trajectory largest-exponent estimate",
    )
