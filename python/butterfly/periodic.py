"""Periodic-orbit diagnostics from flow returns and variational monodromy."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

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


@dataclass(frozen=True, slots=True)
class PeriodicOrbitCorrection:
    initial_state: NDArray[np.float64]
    period_time: float
    final_state: NDArray[np.float64]
    closure_error: float
    phase_residual: float
    correction_norm: float
    evaluations: int
    optimizer_success: bool
    success: bool
    message: str


@dataclass(frozen=True, slots=True)
class UnitMultiplierCorrection:
    """Coupled periodic-orbit and nontrivial +1 Floquet correction."""

    initial_state: NDArray[np.float64]
    period_time: float
    b: float
    eigenvector: NDArray[np.float64]
    closure_error: float
    phase_residual: float
    eigen_residual: float
    normalization_residual: float
    flow_orthogonality_residual: float
    multipliers: NDArray[np.complex128]
    evaluations: int
    success: bool
    message: str


def correct_periodic_orbit(
    parameters: RosslerParameters,
    initial_state: ArrayLike,
    period_time: float,
    *,
    config: SolverConfig = SolverConfig(),
    max_evaluations: int = 40,
    tolerance: float = 1e-11,
) -> PeriodicOrbitCorrection:
    """Correct a near-periodic flow orbit with phase-conditioned shooting.

    The four unknowns are the three initial-state coordinates and period. The
    three flow-closure equations are augmented by a hyperplane phase condition
    through the supplied reference state. The exact variational matrix and the
    vector field at the return supply the shooting Jacobian.
    """

    reference = np.asarray(initial_state, dtype=np.float64)
    if reference.shape != (3,) or not np.all(np.isfinite(reference)):
        raise ValueError("initial_state must contain three finite values")
    if not np.isfinite(period_time) or period_time <= 0.0:
        raise ValueError("period_time must be positive and finite")
    if max_evaluations < 1 or tolerance <= 0.0:
        raise ValueError("invalid corrector configuration")
    phase_direction = rossler_rhs(0.0, reference, parameters)
    phase_norm = float(np.linalg.norm(phase_direction))
    if phase_norm == 0.0:
        raise ValueError("phase condition is undefined at an equilibrium")
    phase_direction = phase_direction / phase_norm
    seed = np.concatenate((reference, (float(period_time),)))
    cache_variables: NDArray[np.float64] | None = None
    cache_residual: NDArray[np.float64] | None = None
    cache_jacobian: NDArray[np.float64] | None = None
    cache_final_state: NDArray[np.float64] | None = None

    def evaluate(
        variables: NDArray[np.float64],
    ) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
        nonlocal cache_variables, cache_residual, cache_jacobian, cache_final_state
        if cache_variables is not None and np.array_equal(variables, cache_variables):
            assert cache_residual is not None
            assert cache_jacobian is not None
            assert cache_final_state is not None
            return cache_residual, cache_jacobian, cache_final_state
        state = variables[:3]
        duration = float(variables[3])
        augmented_initial = np.concatenate((state, np.eye(3, dtype=np.float64).ravel()))

        def augmented_rhs(
            time: float, augmented: NDArray[np.float64]
        ) -> NDArray[np.float64]:
            current_state = augmented[:3]
            tangent = augmented[3:].reshape(3, 3)
            return np.concatenate(
                (
                    rossler_rhs(time, current_state, parameters),
                    (rossler_jacobian(current_state, parameters) @ tangent).ravel(),
                )
            )

        integration = solve_ivp(
            augmented_rhs,
            (0.0, duration),
            augmented_initial,
            method=config.method,
            rtol=config.rtol,
            atol=config.atol,
            max_step=config.max_step,
        )
        if not integration.success:
            raise RuntimeError(f"periodic shooting integration failed: {integration.message}")
        final = np.asarray(integration.y[:, -1], dtype=np.float64)
        final_state = final[:3]
        monodromy = final[3:].reshape(3, 3)
        residual = np.concatenate(
            (final_state - state, (float(np.dot(phase_direction, state - reference)),))
        )
        jacobian = np.empty((4, 4), dtype=np.float64)
        jacobian[:3, :3] = monodromy - np.eye(3)
        jacobian[:3, 3] = rossler_rhs(duration, final_state, parameters)
        jacobian[3, :3] = phase_direction
        jacobian[3, 3] = 0.0
        cache_variables = variables.copy()
        cache_residual = residual
        cache_jacobian = jacobian
        cache_final_state = final_state
        return residual, jacobian, final_state

    solution = least_squares(
        lambda variables: evaluate(variables)[0],
        seed,
        jac=lambda variables: evaluate(variables)[1],
        bounds=(np.asarray([-np.inf, -np.inf, -np.inf, 1e-12]), np.full(4, np.inf)),
        xtol=tolerance,
        ftol=tolerance,
        gtol=tolerance,
        max_nfev=max_evaluations,
        x_scale="jac",
    )
    residual, _, final_state = evaluate(solution.x)
    closure_error = float(np.linalg.norm(residual[:3]))
    return PeriodicOrbitCorrection(
        initial_state=np.asarray(solution.x[:3], dtype=np.float64),
        period_time=float(solution.x[3]),
        final_state=final_state,
        closure_error=closure_error,
        phase_residual=float(abs(residual[3])),
        correction_norm=float(np.linalg.norm(solution.x - seed)),
        evaluations=int(solution.nfev),
        optimizer_success=bool(solution.success),
        success=bool(
            solution.success
            and np.linalg.norm(residual) <= max(10.0 * tolerance, 1e-10)
        ),
        message=str(solution.message),
    )


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
    divergence-predicted determinants are retained. For a finite smooth flow
    segment the exact determinant is strictly positive: a numerically zero
    multiplier is not evidence of a superstable flow orbit. Critical points
    of a scalar projection of a return map require a separate diagnostic.
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


def correct_unit_multiplier_orbit(
    *,
    a: float,
    c: float,
    initial_b: float,
    initial_state: ArrayLike,
    period_time: float,
    config: SolverConfig = SolverConfig(),
    max_evaluations: int = 120,
    tolerance: float = 1e-10,
) -> UnitMultiplierCorrection:
    """Solve a periodic orbit together with a nontrivial +1 multiplier.

    The unknowns are initial state, flow period, ``b``, and a real Floquet
    eigenvector. Flow closure and a fixed phase condition are coupled to
    ``(M-I)q=0``. Unit normalization fixes the scale of ``q`` and Euclidean
    orthogonality to the flow direction excludes the autonomous neutral mode.
    The resulting nine-residual/eight-unknown system is intentionally
    overdetermined: away from a second unit multiplier the eigenvector and
    orthogonality conditions cannot both vanish.

    This formulation requires a second independent unit eigenvector. A generic
    saddle-node of cycles can instead have a defective double unit multiplier
    of the full monodromy, with only the flow direction as an eigenvector. Such
    folds require a projected Poincare or bordered formulation; failure of this
    corrector cannot exclude them.
    """

    reference = np.asarray(initial_state, dtype=np.float64)
    if reference.shape != (3,) or not np.all(np.isfinite(reference)):
        raise ValueError("initial_state must contain three finite values")
    if not np.isfinite(initial_b) or not np.isfinite(a) or not np.isfinite(c):
        raise ValueError("parameters must be finite")
    if not np.isfinite(period_time) or period_time <= 0.0:
        raise ValueError("period_time must be positive and finite")
    if max_evaluations < 1 or tolerance <= 0.0:
        raise ValueError("invalid corrector configuration")

    seed_parameters = RosslerParameters(a=a, b=initial_b, c=c)
    periodic_seed = correct_periodic_orbit(
        seed_parameters,
        reference,
        period_time,
        config=config,
        max_evaluations=max(20, max_evaluations // 3),
        tolerance=min(tolerance, 1e-11),
    )
    if not periodic_seed.success:
        raise RuntimeError(f"initial periodic correction failed: {periodic_seed.message}")
    reference = periodic_seed.initial_state
    phase_direction = rossler_rhs(0.0, reference, seed_parameters)
    phase_direction = phase_direction / np.linalg.norm(phase_direction)
    seed_monodromy = flow_monodromy(
        seed_parameters, reference, periodic_seed.period_time, config=config
    )
    eigenvalues, eigenvectors = np.linalg.eig(seed_monodromy.monodromy)
    neutral_index = int(np.argmin(np.abs(eigenvalues - 1.0)))
    candidate_indices = [index for index in range(3) if index != neutral_index]
    event_index = min(candidate_indices, key=lambda index: abs(eigenvalues[index] - 1.0))
    event_vector = eigenvectors[:, event_index]
    if np.max(np.abs(event_vector.imag)) > 1e-7:
        raise ValueError("nearest nontrivial unit-multiplier seed is not real")
    eigenvector = np.asarray(event_vector.real, dtype=np.float64)
    eigenvector -= float(np.dot(eigenvector, phase_direction)) * phase_direction
    eigenvector_norm = float(np.linalg.norm(eigenvector))
    if eigenvector_norm <= 1e-10:
        raise ValueError("unit-multiplier eigenvector seed is degenerate")
    eigenvector /= eigenvector_norm

    seed = np.concatenate(
        (
            reference,
            (float(periodic_seed.period_time), float(initial_b)),
            eigenvector,
        )
    )
    cache_variables: NDArray[np.float64] | None = None
    cache_residual: NDArray[np.float64] | None = None
    cache_monodromy: MonodromyResult | None = None

    def evaluate(
        variables: NDArray[np.float64],
    ) -> tuple[NDArray[np.float64], MonodromyResult]:
        nonlocal cache_variables, cache_residual, cache_monodromy
        if cache_variables is not None and np.array_equal(variables, cache_variables):
            assert cache_residual is not None
            assert cache_monodromy is not None
            return cache_residual, cache_monodromy
        state = variables[:3]
        duration = float(variables[3])
        b = float(variables[4])
        vector = variables[5:8]
        parameters = RosslerParameters(a=a, b=b, c=c)
        monodromy = flow_monodromy(parameters, state, duration, config=config)
        local_flow = rossler_rhs(0.0, state, parameters)
        local_flow = local_flow / np.linalg.norm(local_flow)
        residual = np.concatenate(
            (
                monodromy.final_state - state,
                (float(np.dot(phase_direction, state - reference)),),
                (monodromy.monodromy - np.eye(3)) @ vector,
                (float(np.dot(vector, vector) - 1.0),),
                (float(np.dot(vector, local_flow)),),
            )
        )
        cache_variables = variables.copy()
        cache_residual = residual
        cache_monodromy = monodromy
        return residual, monodromy

    lower = np.full(8, -np.inf)
    lower[3] = 1e-12
    solution = least_squares(
        lambda variables: evaluate(variables)[0],
        seed,
        bounds=(lower, np.full(8, np.inf)),
        xtol=tolerance,
        ftol=tolerance,
        gtol=tolerance,
        max_nfev=max_evaluations,
        x_scale="jac",
    )
    residual, monodromy = evaluate(solution.x)
    closure_error = float(np.linalg.norm(residual[:3]))
    eigen_residual = float(np.linalg.norm(residual[4:7]))
    success_threshold = max(100.0 * tolerance, 1e-8)
    return UnitMultiplierCorrection(
        initial_state=np.asarray(solution.x[:3], dtype=np.float64),
        period_time=float(solution.x[3]),
        b=float(solution.x[4]),
        eigenvector=np.asarray(solution.x[5:8], dtype=np.float64),
        closure_error=closure_error,
        phase_residual=float(abs(residual[3])),
        eigen_residual=eigen_residual,
        normalization_residual=float(abs(residual[7])),
        flow_orthogonality_residual=float(abs(residual[8])),
        multipliers=monodromy.multipliers,
        evaluations=int(solution.nfev),
        success=bool(solution.success and np.linalg.norm(residual) <= success_threshold),
        message=str(solution.message),
    )
