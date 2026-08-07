import numpy as np

from butterfly import (
    RosslerParameters,
    SolverConfig,
    correct_periodic_orbit,
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

    assert correction.success
    assert correction.closure_error < 1e-9
    assert correction.phase_residual < 1e-10
    assert abs(correction.period_time - 16.788110651043098) < 1e-5
