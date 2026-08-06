import numpy as np

from butterfly.models import (
    RosslerParameters,
    equilibrium_eigenvalues,
    rossler_equilibria,
    rossler_jacobian,
    rossler_rhs,
)


HUB = RosslerParameters(a=0.1798, b=0.2, c=10.3084)


def test_rhs_matches_declared_equations() -> None:
    actual = rossler_rhs(123.0, (1.0, 2.0, 3.0), HUB)
    expected = (-5.0, 1.0 + 2.0 * HUB.a, HUB.b + 3.0 * (1.0 - HUB.c))
    np.testing.assert_allclose(actual, expected, rtol=0.0, atol=0.0)


def test_analytic_jacobian_matches_central_difference() -> None:
    state = np.asarray((1.2, -0.7, 0.4))
    epsilon = 1e-6
    numerical = np.column_stack(
        [
            (
                rossler_rhs(0.0, state + epsilon * np.eye(3)[index], HUB)
                - rossler_rhs(0.0, state - epsilon * np.eye(3)[index], HUB)
            )
            / (2.0 * epsilon)
            for index in range(3)
        ]
    )
    np.testing.assert_allclose(
        rossler_jacobian(state, HUB), numerical, rtol=1e-9, atol=1e-9
    )


def test_equilibria_are_zeros_of_vector_field() -> None:
    equilibria = rossler_equilibria(HUB)
    assert equilibria.shape == (2, 3)
    assert equilibria[0, 2] < equilibria[1, 2]
    for point in equilibria:
        np.testing.assert_allclose(rossler_rhs(0.0, point, HUB), 0.0, atol=1e-13)


def test_hub_small_equilibrium_is_saddle_focus() -> None:
    values = equilibrium_eigenvalues(HUB)[0]
    real_value = values[np.argmin(np.abs(values.imag))]
    pair = values[np.argsort(np.abs(values.imag))[-2:]]
    assert real_value.real < 0.0
    assert np.all(pair.real > 0.0)
    assert np.sign(pair[0].imag) != np.sign(pair[1].imag)
    np.testing.assert_allclose(pair.real, 0.08897, atol=5e-4)
    np.testing.assert_allclose(np.abs(pair.imag), 0.99596, atol=5e-4)
    np.testing.assert_allclose(real_value.real, -10.3030, atol=5e-4)


def test_degenerate_a_zero_equilibrium() -> None:
    parameters = RosslerParameters(a=0.0, b=0.2, c=5.0)
    equilibria = rossler_equilibria(parameters)
    np.testing.assert_allclose(equilibria, ((0.0, -0.04, 0.04),))
