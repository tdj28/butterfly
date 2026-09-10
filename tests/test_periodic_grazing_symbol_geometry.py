"""Conditional analytic controls, not a target flow/word verification."""
from fractions import Fraction as F
import numpy as np
import pytest
from butterfly.models import RosslerParameters, rossler_equilibria, rossler_rhs, rossler_jacobian
from butterfly.poincare import legacy_rossler_section
from butterfly import polynomial_census as roots


@pytest.mark.parametrize('height,count', [(F(-1, 8), 0), (F(0), 1), (F(1, 8), 2)])
def test_exact_quadratic_crossing_birth_and_orientations(height, count):
    # t=2u-1, kappa=1, g=height-t^2/2 on u in [0,1].
    p = roots.integers([height-F(1, 2), F(2), F(-2)])
    certificate = roots.isolate(p, F(2), time_width=F('1e-15'))
    checked = roots.verify(p, F(2), certificate, time_width=F('1e-15'))
    assert checked['complete'] and len(checked['roots']) == count
    if height > 0:
        times = [2*(F(lo)+F(hi))/2-1 for lo, hi in checked['roots']]
        assert times == [F(-1, 2), F(1, 2)]
        assert sum(t > 0 for t in times) == 1  # g'=-t: exactly one downward crossing.


@pytest.mark.parametrize('a,c', [(.15, 7.), (.215593, 7.147), (.3, 20.)])
@pytest.mark.parametrize('delta', [.01, 1., 15.])
def test_projected_stationary_contact_is_regular_not_an_equilibrium(a, c, delta):
    params = RosslerParameters(a, .2, c); eq = rossler_equilibria(params)[0]
    q = eq+np.array([0., 0., delta]); v = rossler_rhs(0., q, params)
    np.testing.assert_allclose(v, [-delta, 0., (eq[0]-c)*delta], rtol=2e-14, atol=2e-14)
    acceleration = rossler_jacobian(q, params)@v
    assert acceleration[1] == pytest.approx(-delta, rel=2e-14, abs=2e-14)
    assert np.linalg.norm(v) > 0
    assert not legacy_rossler_section(params).accepts(q)  # Strict x<x* gate.


@pytest.mark.parametrize('displacement', [-1., -.01, .01, 1.])
def test_section_gate_is_exactly_downward_orientation(displacement):
    params = RosslerParameters(.215593, .2, 7.147); eq = rossler_equilibria(params)[0]
    q = eq+np.array([displacement, 0., 15.]); v = rossler_rhs(0., q, params)
    assert v[1] == pytest.approx(displacement)
    assert legacy_rossler_section(params).accepts(q) == (v[1] < 0)
