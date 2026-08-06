import numpy as np

from butterfly.integrate import SolverConfig, integrate_trajectory
from butterfly.models import RosslerParameters, rossler_equilibria


HUB = RosslerParameters(a=0.1798, b=0.2, c=10.3084)


def test_equilibrium_remains_fixed() -> None:
    equilibrium = rossler_equilibria(HUB)[0]
    result = integrate_trajectory(HUB, equilibrium, (0.0, 5.0))
    assert result.success
    np.testing.assert_allclose(result.y[:, -1], equilibrium, atol=1e-12, rtol=0.0)


def test_short_trajectory_converges_under_tighter_tolerances() -> None:
    initial = (0.0, 4.0, 0.0)
    reference = integrate_trajectory(
        HUB,
        initial,
        (0.0, 2.0),
        config=SolverConfig(rtol=1e-12, atol=1e-14, max_step=0.01),
    )
    candidate = integrate_trajectory(
        HUB,
        initial,
        (0.0, 2.0),
        config=SolverConfig(rtol=1e-9, atol=1e-11, max_step=0.05),
    )
    assert reference.success and candidate.success
    np.testing.assert_allclose(
        candidate.y[:, -1], reference.y[:, -1], rtol=2e-9, atol=2e-10
    )


def test_invalid_initial_state_is_rejected() -> None:
    try:
        integrate_trajectory(HUB, (0.0, 1.0), (0.0, 1.0))
    except ValueError as error:
        assert "three finite values" in str(error)
    else:
        raise AssertionError("invalid state was accepted")
