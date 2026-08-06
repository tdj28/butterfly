import numpy as np

from butterfly.integrate import SolverConfig
from butterfly.lyapunov import LyapunovConfig, lyapunov_spectrum
from butterfly.models import (
    RosslerParameters,
    equilibrium_eigenvalues,
    rossler_equilibria,
)


HUB = RosslerParameters(a=0.1798, b=0.2, c=10.3084)


def equilibrium_config(duration: float = 60.0) -> LyapunovConfig:
    return LyapunovConfig(
        transient=0.0,
        duration=duration,
        qr_interval=0.5,
        solver=SolverConfig(rtol=1e-11, atol=1e-13, max_step=0.02),
    )


def test_equilibrium_spectrum_matches_linearization() -> None:
    equilibrium = rossler_equilibria(HUB)[0]
    result = lyapunov_spectrum(HUB, equilibrium, config=equilibrium_config())
    expected = np.sort(equilibrium_eigenvalues(HUB)[0].real)[::-1]
    assert result.success
    np.testing.assert_allclose(
        np.sort(result.exponents)[::-1], expected, rtol=0.0, atol=2e-2
    )


def test_trace_identity_matches_mean_divergence() -> None:
    equilibrium = rossler_equilibria(HUB)[0]
    result = lyapunov_spectrum(HUB, equilibrium, config=equilibrium_config(20.0))
    expected_divergence = HUB.a + equilibrium[0] - HUB.c
    assert result.success
    np.testing.assert_allclose(result.mean_divergence, expected_divergence, atol=1e-11)
    assert result.trace_identity_error < 1e-9
    assert result.running_exponents.shape == (40, 3)


def test_invalid_initial_state_is_rejected() -> None:
    try:
        lyapunov_spectrum(HUB, (1.0, 2.0))
    except ValueError as error:
        assert "three finite values" in str(error)
    else:
        raise AssertionError("invalid state was accepted")
