import numpy as np
from types import SimpleNamespace

import pytest

from butterfly import (
    RosslerParameters,
    SolverConfig,
    correct_periodic_orbit,
    correct_unit_multiplier_orbit,
    flow_monodromy,
    rossler_equilibria,
    rossler_jacobian,
)


def test_equilibrium_monodromy_matches_matrix_exponential_eigenvalues() -> None:
    parameters = RosslerParameters(a=0.1798, b=0.2, c=10.3084)
    equilibrium = rossler_equilibria(parameters)[0]
    period_time = 0.1
    result = flow_monodromy(
        parameters,
        equilibrium,
        period_time,
        config=SolverConfig(rtol=1e-12, atol=1e-14, max_step=0.005),
    )
    expected = np.exp(np.linalg.eigvals(rossler_jacobian(equilibrium, parameters)) * period_time)
    assert result.success
    assert result.closure_error < 1e-13
    assert np.allclose(
        np.sort_complex(result.multipliers), np.sort_complex(expected), rtol=1e-10, atol=1e-12
    )
    assert np.isclose(
        result.computed_determinant, result.predicted_determinant, rtol=1e-10
    )


def test_periodic_shooting_corrects_perturbed_period3_cycle() -> None:
    parameters = RosslerParameters(a=0.245, b=0.2, c=5.75)
    reference = np.asarray([-4.443749791275888, -0.034834311337015006, 0.01970013003267939])
    perturbed = reference + np.asarray([2e-5, -1e-5, 1e-6])
    correction = correct_periodic_orbit(
        parameters,
        perturbed,
        16.788110651043098 * (1.0 + 2e-6),
        config=SolverConfig(rtol=1e-11, atol=1e-13, max_step=0.05),
        tolerance=1e-11,
    )

    assert correction.optimizer_success
    assert correction.success
    assert correction.closure_error < 1e-9
    assert correction.phase_residual < 1e-10
    assert abs(correction.period_time - 16.788110651043098) < 1e-5


def test_coupled_unit_multiplier_correction_excludes_flow_mode() -> None:
    correction = correct_unit_multiplier_orbit(
        a=0.245,
        c=5.1,
        initial_b=0.27204621592418715,
        initial_state=np.asarray(
            [-4.176536702108349, -0.03577455846005116, 0.029480289783174195]
        ),
        period_time=33.78616265748715,
        config=SolverConfig(rtol=1e-10, atol=1e-12, max_step=0.05),
        tolerance=1e-9,
    )

    assert correction.success
    assert abs(correction.b - 0.27228) < 5e-4
    assert correction.closure_error < 1e-7
    assert correction.eigen_residual < 1e-7
    assert correction.flow_orthogonality_residual < 1e-7
    assert correction.normalization_residual < 1e-7


def test_periodic_corrector_rejects_closure_with_failed_phase_condition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # a=b=0 and z=0 give the exact circle x=cos(t), y=sin(t).
    # Optimizer termination can occur through stagnation; it is not proof that
    # all equations passed. Simulate such a termination on the correct orbit
    # but outside the phase plane through the requested seed.
    variables = np.asarray((1.0, 0.0, 0.0, 2.0 * np.pi))
    monkeypatch.setattr(
        "butterfly.periodic.least_squares",
        lambda *args, **kwargs: SimpleNamespace(
            x=variables, success=True, nfev=1, message="xtol termination"
        ),
    )
    correction = correct_periodic_orbit(
        RosslerParameters(a=0.0, b=0.0, c=1.0),
        (1.0, 0.01, 0.0),
        2.0 * np.pi,
    )
    assert correction.optimizer_success
    assert correction.closure_error < 1e-10
    assert correction.phase_residual > 1e-3
    assert not correction.success
