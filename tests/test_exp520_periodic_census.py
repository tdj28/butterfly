"""Synthetic dense-output census controls; no EXP-519 target extrema read."""
from copy import deepcopy
from fractions import Fraction as F

import numpy as np
import pytest
from scipy.integrate._ivp.rk import Dop853DenseOutput
from scipy.integrate._ivp.radau import RadauDenseOutput
from butterfly import polynomial_census as roots
from scripts import exp520_periodic_census as census


@pytest.mark.parametrize('method', ['DOP853', 'Radau'])
def test_exact_basis_matches_independent_expansion_and_scipy(method):
    rng = np.random.default_rng(520)
    old = rng.normal(size=3)
    coefficients = rng.normal(size=(7, 3) if method == 'DOP853' else (3, 3))
    p = census.powers(old, coefficients, method)
    assert p == census.powers(old, coefficients, method, auditor=True)
    if method == 'DOP853': dense = Dop853DenseOutput(3., 5., old, coefficients)
    else: dense = RadauDenseOutput(3., 5., old, coefficients)
    for x in (F(0), F(1, 7), F(1, 2), F(1)):
        expected = [float(roots.evaluate(q, x)) for q in p]
        np.testing.assert_allclose(dense(3+2*float(x)), expected, rtol=2e-14, atol=2e-14)


@pytest.mark.parametrize('polynomial,count,complete', [
    ([1, 0, 1], 0, True), ([-1, 2], 1, True),
    ([3, -16, 16], 2, True), ([0, -1, 1], 2, True),
    ([1, -4, 4], 1, True), ([-1, 6, -12, 8], 1, True),
    ([0, 0, 0], 0, False), ([1, -6, 9], 0, False),
])
def test_missing_root_tangent_multiple_and_unresolved_controls(polynomial, count, complete):
    certificate = roots.isolate(polynomial, 1, time_width=census.TIME_WIDTH)
    result = roots.verify(polynomial, 1, certificate, time_width=census.TIME_WIDTH)
    assert result['complete'] == complete
    assert len(result['roots']) == count
    if not complete: assert result['unresolved']


def trajectory(polynomials, width=2.5):
    old = np.array([[p[0], 0., 0.] for p in polynomials])
    coefficients = np.zeros((len(old), 3, 3))
    for i, p in enumerate(polynomials): coefficients[i, 0, :len(p)-1] = p[1:]
    states = np.vstack((old, [sum(polynomials[-1]), 0., 0.]))
    return dict(times=np.linspace(0, width, len(old)+1), states=states, dense_old=old,
                dense_coefficients=coefficients, historical_extrema_times=np.array([]),
                historical_extrema_states=np.empty((0, 3)))


def analyze(raw, **kwargs):
    return census.profile(raw, 'Radau', dict(a=.2, b=.2, c=7.), [0., 0., 0.], 1., **kwargs)


def test_same_sign_endpoint_roots_are_retained_despite_missing_callbacks():
    raw = trajectory([[3., -16., 16.]])
    result, certificates = analyze(raw)
    assert result['polynomial_census_complete'] and len(result['events']) == 2
    assert not result['callback_comparison']['passed'] and not result['qualified']
    assert [e['time'] for e in result['events']] == [.625, 1.875]
    replay, _ = analyze(raw, certificate=certificates)
    assert replay == result


def test_shared_endpoint_has_single_ownership_with_both_witnesses():
    result, certificates = analyze(trajectory([[-1., 1.], [0., 1.]]))
    assert result['polynomial_census_complete']
    assert len(result['events']) == 1
    assert result['events'][0]['segments'] == [0, 1]
    assert len(result['events'][0]['join_witnesses']) == 1
    assert analyze(trajectory([[-1., 1.], [0., 1.]]), certificate=certificates)[0] == result


def test_jump_over_zero_blocks_completeness_even_if_no_segment_has_a_root():
    result, _ = analyze(trajectory([[-1.], [1.]]))
    assert not result['polynomial_census_complete'] and result['join_failures']
    assert not result['events']


@pytest.mark.parametrize('mutation', ['missing', 'empty', 'false-root', 'points'])
def test_certificate_tampering_rejected(mutation):
    raw = trajectory([[3., -16., 16.]])
    _, certificates = analyze(raw)
    bad = deepcopy(certificates)
    if mutation == 'missing': bad.clear()
    elif mutation == 'empty': bad[0]['leaves'] = [dict(path='', kind='empty', variations=0)]
    elif mutation == 'false-root': bad[0]['leaves'][0]['root'] = ['1/8', '1/8']
    else: bad[0]['points'].append('1/8')
    with pytest.raises(ValueError): analyze(raw, certificate=bad)


@pytest.mark.parametrize('mutation', ['nan', 'shape', 'order', 'horizon', 'mesh'])
def test_invalid_raw_inventory_fails_or_is_retained_as_unqualified(mutation):
    raw = trajectory([[3., -16., 16.]])
    if mutation == 'nan': raw['dense_old'][0, 0] = np.nan
    elif mutation == 'shape': raw['dense_coefficients'] = np.zeros((1, 2, 3))
    elif mutation == 'order': raw['times'] = np.array([0., 0.])
    elif mutation == 'horizon': raw['times'][-1] = 2.6
    else: raw['states'][-1, 0] += 1
    if mutation == 'mesh':
        result, _ = analyze(raw)
        assert not result['polynomial_census_complete']
    else:
        with pytest.raises(ValueError): analyze(raw)


def test_grazing_geometry_is_not_an_equilibrium_or_homoclinic_proof():
    # Exact regular projected-center passage, with nonzero z displacement.
    poly = [[F(0)], [F(0)], [F(2)]]
    e = census.classify(poly, F(0), F(1), ['1/2', '1/2'], dict(a=.2, b=.2, c=7.), [0, 0, 0])
    assert e['signed_gap'] == 0 and e['z_separation'] == 2
    assert e['speed'] > 0 and e['acceleration'] == -2 and e['curvature_sign'] == -1


def test_cross_context_nearest_selection_requires_identity_and_separation():
    def event(t, g):
        return dict(time=t, cycle_phase=t, state=[t, g, 0], normalized_gap=g)
    profiles = [dict(method=m, qualified=True, windows=[dict(events=[event(.2, .01), event(.7, .2)]) for _ in range(2)]) for m in ('DOP853', 'Radau')]
    result = census.point_comparison(profiles, [1., 1.])
    assert result['consistent_nearest'] and result['nearest_index'] == 0
    for p in profiles:
        for w in p['windows']: w['events'][1]['normalized_gap'] = .01000001
    result = census.point_comparison(profiles, [1., 1.])
    assert not result['consistent_nearest'] and not result['nearest']
