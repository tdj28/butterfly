import numpy as np

from butterfly import (
    RosslerParameters,
    SolverConfig,
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
