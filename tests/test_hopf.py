import numpy as np
import pytest

from butterfly import (
    RosslerParameters,
    equilibrium_eigenvalues,
    rossler_equilibrium_characteristic_coefficients,
    rossler_hopf_points,
)


def _complex_pair_real(parameters: RosslerParameters, equilibrium_index: int) -> float:
    values = equilibrium_eigenvalues(parameters)[equilibrium_index]
    pair = values[np.argsort(np.abs(values.imag))[-2:]]
    return float(np.mean(pair.real))


def test_hub_a_hopf_point_satisfies_independent_eigen_and_routh_checks() -> None:
    point, = rossler_hopf_points(a=0.1798, b=0.2)
    np.testing.assert_allclose(point.parameters.c, 0.5192306256940273, atol=1e-14)
    coefficients = rossler_equilibrium_characteristic_coefficients(
        point.parameters, point.equilibrium
    )
    A, B, C = coefficients
    np.testing.assert_allclose(A * B, C, atol=2e-15)
    np.testing.assert_allclose(point.angular_frequency**2, B, atol=2e-15)
    assert point.real_eigenvalue < 0.0
    assert abs(_complex_pair_real(point.parameters, point.equilibrium_index)) < 2e-15


def test_hopf_pair_crosses_transversely_when_c_increases() -> None:
    point, = rossler_hopf_points(a=0.1798, b=0.2)
    c = point.parameters.c
    left = RosslerParameters(a=0.1798, b=0.2, c=c - 1e-6)
    right = RosslerParameters(a=0.1798, b=0.2, c=c + 1e-6)
    assert _complex_pair_real(left, point.equilibrium_index) < -1e-8
    assert _complex_pair_real(right, point.equilibrium_index) > 1e-8


def test_two_regular_hopf_points_can_exist_above_a_equals_b() -> None:
    points = rossler_hopf_points(a=0.201, b=0.2)
    assert len(points) == 2
    assert points[0].parameters.c < points[1].parameters.c
    assert {point.equilibrium_index for point in points} == {1}
    assert all(point.real_eigenvalue > 0.0 for point in points)


@pytest.mark.parametrize("a,b", [(0.0, 0.2), (0.1, 0.0), (-0.1, 0.2)])
def test_hopf_rejects_nonregular_parameters(a: float, b: float) -> None:
    with pytest.raises(ValueError):
        rossler_hopf_points(a=a, b=b)
