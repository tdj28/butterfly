import copy
from decimal import Decimal as D
import json

import pytest

from butterfly import decimal_grazing as numeric
from butterfly.bounded_json import ArtifactQuotaExceeded, directory_bytes
from scripts import run_exp515_third_return_precision as run
from scripts import audit_exp515_third_return_precision as audit


@pytest.mark.parametrize('kind', run.KINDS)
def test_analytic_projection_and_initial_exclusion(kind):
    c = run.control_case(kind)
    raw = numeric.integrate(c['initial'], c['field'], c['horizon'], numeric.CONFIGS[0])
    result, certificates = run.model.analyze(raw, c['section'])
    replay, _ = run.model.analyze(raw, c['section'], certificate=certificates)
    assert result == replay
    assert run.control_identity(c, result)['passed']
    audit.check_raw(raw, c, numeric.CONFIGS[0])
    if kind == 'phase-small':
        assert D(result['measures'][0]['scaled_norm']) == D('1e-12')
    if kind == 'phase-zero':
        assert result['measures'][0]['box_relative_radius'] is None


def test_complete_plan_and_exact_initials():
    p = run.load()
    assert p['limits']['target_ivps'] == 12
    assert [(c['direction'], c['node']) for c in p['cases']] == [(d, n) for d in (0, 1) for n in (8, 9, 10)]
    old = json.loads((run.ROOT/run.RECEIPT).read_bytes())
    for case in p['cases']:
        profile = old['result']['rows'][case['direction']]['samples'][case['node']]['profiles'][0]
        assert case['initial'] == [str(D.from_float(x)) for x in profile['report']['initial_state']+profile['report']['initial_tangent']]
        assert case['horizon'] == '18'


def test_input_tamper_fails_before_selection(monkeypatch):
    monkeypatch.setattr(run, 'INPUTS', {run.RECEIPT: '0'*64})
    with pytest.raises(ValueError, match='input'):
        run.expected()


def test_missing_historical_comparator_rejected():
    old = json.loads((run.ROOT/run.RECEIPT).read_bytes())
    old['result']['rows'][0]['samples'][8]['profiles'].pop()
    with pytest.raises(ValueError, match='identity'):
        run.model.selection(old)


def test_vector_comparison_does_not_use_absolute_zero_floor():
    assert not run.model.vector_compare(['1e-20', '0', '0'], ['2e-20', '0', '0'])['within_one_percent']
    assert not run.model.vector_compare(['0', '0', '0'], ['0', '0', '0'])['within_one_percent']
    assert run.model.vector_compare(['1e-20', '0', '0'], ['1.001e-20', '0', '0'])['within_one_percent']


def test_scalar_raw_recurrence_rejects_tamper():
    c = run.control_case('ordinary')
    raw = numeric.integrate(c['initial'], c['field'], c['horizon'], numeric.CONFIGS[0])
    raw['steps'][0]['coefficients'][0][1] = '1.01'
    with pytest.raises(ValueError, match='recurrence'):
        audit.check_raw(raw, c, numeric.CONFIGS[0])


def test_production_archive_and_replay(tmp_path):
    c = run.control_case('phase-small')
    limits = dict(output_bytes=8*1024**2, minimum_free_bytes=0, failure_reserve_bytes=1024)
    calls = []
    result = run.produce(c, numeric.CONFIGS[0], tmp_path, limits, lambda integrating=False: calls.append(integrating))
    assert sum(calls) == 1
    assert audit.profile(tmp_path, c, numeric.CONFIGS[0], result)
    changed = copy.deepcopy(result)
    changed['measures'][0]['corrected'][2] = '2e-14'
    with pytest.raises(ValueError, match='replay'):
        audit.profile(tmp_path, c, numeric.CONFIGS[0], changed)


def test_producer_quota_preserves_partial_product(tmp_path):
    c = run.control_case('ordinary')
    limits = dict(output_bytes=1400, minimum_free_bytes=0, failure_reserve_bytes=256)
    with pytest.raises(ArtifactQuotaExceeded):
        run.produce(c, numeric.CONFIGS[0], tmp_path, limits, lambda integrating=False: None)
    assert directory_bytes(tmp_path) <= limits['output_bytes']-limits['failure_reserve_bytes']
    assert list(tmp_path.iterdir())


def synthetic_pair():
    c = run.control_case('phase-small')
    raw = numeric.integrate(c['initial'], c['field'], c['horizon'], numeric.CONFIGS[0])
    profile, _ = run.model.analyze(raw, c['section'])
    # Three copies test matrix/decision logic, not a three-return analytic flow.
    profile['measures'] = [copy.deepcopy(profile['measures'][0]) for _ in range(3)]
    profile['census']['events'] = [copy.deepcopy(profile['census']['events'][0]) for _ in range(3)]
    pair = [dict(copy.deepcopy(profile), configuration=config['name']) for config in numeric.CONFIGS]
    old = [dict(method=m, events=[dict(time=e['time'], state=e['state'], tangent=e['corrected'])
        for e in profile['measures']]) for m in ('DOP853', 'Radau')]
    return pair, old


def test_decision_retains_failed_ordinal_and_comparators():
    pair, old = synthetic_pair()
    assert run.model.compare(pair, old)['all_three_resolved']
    pair[1]['measures'][1]['corrected'][2] = '2e-14'
    result = run.model.compare(pair, old)
    assert not result['all_three_resolved']
    assert len(result['ordinals']) == 3 and len(result['historical']) == 4
    assert not result['ordinals'][1]['resolved']
    assert result['ordinals'][0]['resolved'] and result['ordinals'][2]['resolved']


def test_missing_return_and_box_uncertainty_block_resolution():
    pair, old = synthetic_pair()
    pair[1]['measures'].pop()
    assert not run.model.compare(pair, old)['all_three_resolved']
    pair, old = synthetic_pair()
    pair[0]['measures'][2]['box_relative_radius'] = '.002'
    assert not run.model.compare(pair, old)['all_three_resolved']


def test_wrong_precision_order_rejected():
    pair, old = synthetic_pair()
    with pytest.raises(ValueError, match='ordered'):
        run.model.compare(pair[::-1], old)


def test_quadratic_variation_uses_rossler_jacobian():
    # Instantaneous algebra at an inert state; no target trajectory generated.
    field = run.load()['cases'][0]['field']
    q = list(map(D, ['1', '2', '3', '4', '5', '6']))
    coef = numeric.coefficients(q, field, 1)
    a, b, c = [D.from_float(v) for v in (.21559488260076548, .2, 7.162000000000001)]
    expected = [-q[1]-q[2], q[0]+a*q[1], b+q[2]*(q[0]-c),
                -q[4]-q[5], q[3]+a*q[4], q[2]*q[3]+(q[0]-c)*q[5]]
    assert all(abs(row[1]-v) < D('1e-25') for row, v in zip(coef, expected, strict=True))
