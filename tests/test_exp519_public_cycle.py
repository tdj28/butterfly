"""Public cycle checker exercised on authentic, previously audited evidence."""
from copy import deepcopy
import json
import pytest
from scripts import verify_exp519_public_response as public


@pytest.fixture(scope='module')
def original():
    root = public.run.ROOT
    result = root/'docs/experiments/receipts/EXP-497-contact-localization-result.json'
    plan = root/'experiments/manifests/EXP-497-contact-localization.json'
    assert public.sha256(result) == 'ed229b4a772ef19d227272006401d19090ee5e28a357791f25400cafa3271cff'
    assert public.sha256(plan) == '2e3cc27a66bc99e4b2f76fa9ad7bb9b61da233bcf1a080463980f30c51678cfe'
    row = next(r for r in json.loads(result.read_bytes())['rows'] if r['status'] == 'proximate')
    return row, json.loads(plan.read_bytes())['periodic']


def test_authentic_prior_cycle_without_new_integrations(original):
    row, p = original
    count = public.check_cycle(row['result']['cycle'], row['spec'], row['seed'], p)
    assert count == sum(len(r['raw_files']) for r in row['result']['cycle']['profiles'])
    assert count > 0


@pytest.mark.parametrize('mutation', [
    'method', 'identity', 'missing-raw', 'missing-observation', 'closure', 'phase', 'gate',
    'window', 'event-count', 'accepted', 'angle', 'plane', 'event-time', 'distinct',
    'shorter-period', 'minimal-period', 'winding', 'geometry-gate', 'integer-error',
    'repeat', 'profile-gate', 'cycle-status', 'rigor', 'uncertain'])
def test_semantic_cycle_tampering(original, mutation):
    row, p = deepcopy(original); cycle = row['result']['cycle']; profile = cycle['profiles'][0]
    window = profile['metric']['windows'][0]
    event = next(e for e in profile['observation']['events']['historical'] if e['accepted'])
    if mutation == 'method': cycle['profiles'].reverse()
    elif mutation == 'identity': cycle['spec'] = dict(cycle['spec'], id='substitute')
    elif mutation == 'missing-raw': profile['raw_files'].pop(0)
    elif mutation == 'missing-observation': profile['raw_files'].pop()
    elif mutation == 'closure': profile['correction']['closure_error'] += .1
    elif mutation == 'phase': profile['correction']['phase_residual'] += .1
    elif mutation == 'gate': profile['correction_gate']['passed'] = False
    elif mutation == 'window': profile['metric']['windows'].reverse()
    elif mutation == 'event-count': window['counts']['historical'] += 1
    elif mutation == 'accepted': event['accepted'] = False
    elif mutation == 'angle': event['angle'] += .1
    elif mutation == 'plane': event['residual'] += .1
    elif mutation == 'event-time': event['time'] = -1.
    elif mutation == 'distinct': window['minimum_distinct_event_separation']['historical'] += .1
    elif mutation == 'shorter-period': window['shorter_periods'][0]['excluded'] = False
    elif mutation == 'minimal-period': window['conditional_minimal_period'] = False
    elif mutation == 'winding': window['geometry']['raw']['cut_index'] += 1
    elif mutation == 'geometry-gate': window['geometry']['raw']['qualified'] = False
    elif mutation == 'integer-error': window['geometry']['raw']['integer_error'] += .1
    elif mutation == 'repeat': profile['metric']['repeat']['passed'] = False
    elif mutation == 'profile-gate': profile['qualified'] = False
    elif mutation == 'cycle-status': cycle['status'] = 'unqualified'
    elif mutation == 'rigor': profile['metric']['rigorous_minimal_period_proof'] = True
    elif mutation == 'uncertain': profile['observation']['uncertain_extrema'] = [{'unfounded': True}]
    with pytest.raises(ValueError): public.check_cycle(cycle, row['spec'], row['seed'], p)
