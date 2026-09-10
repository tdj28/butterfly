"""Prospective model controls; synthetic stage data are not new flow evidence."""
from copy import deepcopy
import json
import subprocess
import sys
import numpy as np
import pytest
from scripts import run_exp508_constrained_step as run

m = run.model


def context():
    return run.base.load(),run.prior.prior.inputs(),run.prior.inputs(),run.inputs()


def test_authentic_secant_and_predictor():
    numerical,first,rejected,start = context()
    state = m.initialize(numerical,first,rejected,start)
    assert state['maximum_a_column_relative_error'] < .1
    assert len(state['models']) == 256
    for a,b in zip(state['models'],first['response']['matrices'],strict=True):
        assert [r[1] for r in a] == [r[1] for r in b['matrices'][1]]
    p = m.proposal(state,start,numerical['anchor'],'predictor')
    assert p['qualified']
    assert p['spec']['parameters']['c'] == start['spec']['parameters']['c']-.02
    assert p['spec']['parameters']['b'] == .2
    assert abs(p['realized_step'][0]) < .1


@pytest.mark.parametrize('kind',['missing','nonfinite','non-a-step','zero-step','negative-slope','slope-drift','unqualified'])
def test_bad_historical_secant_rejected(kind):
    numerical,first,rejected,start = context()
    if kind == 'missing':
        start['vectors'].pop()
    elif kind == 'nonfinite':
        start['vectors'][0]['value'][0] = float('nan')
    elif kind == 'non-a-step':
        start['spec']['parameters']['c'] += .001
    elif kind == 'zero-step':
        start['spec']['parameters']['a'] = rejected['spec']['parameters']['a']
    elif kind == 'negative-slope':
        start['vectors'][0]['value'][0] = .1
    elif kind == 'slope-drift':
        start['vectors'][0]['value'][0] = -.1
    else:
        start['qualified'] = False
    with pytest.raises(ValueError):
        m.initialize(numerical,first,rejected,start)


def simulated(kind='normal'):
    numerical,first,rejected,start = context()
    seen = []
    def measure(p,spec):
        seen.append(spec['id'])
        point = deepcopy(start)
        point['spec'] = deepcopy(spec)
        point['cycle']['spec'] = deepcopy(spec)
        correction = spec['id'] == 'corrector'
        fold = 1e-7 if correction else 3e-5
        distance = 1e-6 if correction else 1.1e-4
        factor = .88 if correction else .9
        if kind in ('predictor-already-proximate','corrector-fails'):
            distance = 1e-6
        if kind in ('zero-good','zero-bad'):
            fold = 0.
            distance = 1e-6 if kind == 'zero-good' else 1.1e-4
        if kind == 'predictor-unqualified' and not correction or kind == 'corrector-unqualified' and correction:
            point['qualified'] = False
        if kind == 'corrector-fails' and correction:
            distance = 1.1e-4
        if kind == 'boundary-worse' and correction:
            factor = 1.01
        point['contact']['envelope']['pair_state_distance'][3] = distance
        old_boundary = float(start['boundary_analysis']['cycle_indices'][1]['maximum_distance'])
        point['boundary_analysis']['cycle_indices'][1]['maximum_distance'] = str(old_boundary*factor)
        for v in point['vectors']:
            v['value'][0] = fold
            v['value'][1] *= factor
        if kind == 'one-variant-worse' and correction:
            point['vectors'][-1]['value'][1] = start['vectors'][-1]['value'][1]*1.01
        if kind == 'adjacent-fails' and correction:
            point['correspondence']['passed'] = False
        if kind == 'original-fails' and correction:
            for profile in point['cycle']['profiles']:
                for window in profile['metric']['windows']:
                    window['event_states']['historical'] = np.roll(window['event_states']['historical'],1,axis=0).tolist()
        return point
    progress = m.ledger()
    result = m.follow(numerical,first,rejected,start,measure,progress)
    return result,progress,seen


@pytest.mark.parametrize('kind',['normal','predictor-already-proximate'])
def test_corrector_runs_and_full_pair_can_pass(kind):
    result,progress,seen = simulated(kind)
    assert seen == ['predictor','corrector']
    assert all(p['status'] == 'completed' for p in progress)
    assert result['analysis']['accepted']
    assert result['analysis']['predictor_only_baseline']['accepted'] == (kind == 'predictor-already-proximate')
    assert len(result['entries'][0]['changes']) == len(result['entries'][1]['changes']) == 256
    assert not result['analysis']['symbolic_chains_verified']


@pytest.mark.parametrize('kind',['corrector-fails','corrector-unqualified','boundary-worse','one-variant-worse','adjacent-fails','original-fails'])
def test_no_favorable_component_or_predictor_fallback(kind):
    result,progress,seen = simulated(kind)
    assert seen == ['predictor','corrector']
    assert not result['analysis']['accepted']
    if kind == 'corrector-fails':
        assert result['analysis']['predictor_only_baseline']['accepted']
    assert not result['analysis']['joint_proximity']


@pytest.mark.parametrize('kind',['zero-good','zero-bad','predictor-unqualified'])
def test_exact_conditional_skip_rules(kind):
    result,progress,seen = simulated(kind)
    assert seen == ['predictor']
    assert progress[1]['status'] == 'not-run' and progress[1]['reason']
    assert result['analysis']['accepted'] == (kind == 'zero-good')
    assert result['analysis']['correction_waived'] == (kind == 'zero-good')


def test_corrector_clips_without_changing_c():
    numerical,first,rejected,start = context()
    state = m.initialize(numerical,first,rejected,start)
    for v in start['vectors']:
        v['value'][0] = 1.
    p = m.proposal(state,start,numerical['anchor'],'corrector')
    assert p['qualified'] and p['unclipped_a_step'] < -.1
    np.testing.assert_allclose(p['realized_step'],[-.1,0],atol=1e-12)
    assert p['spec']['parameters']['c'] == start['spec']['parameters']['c']
    assert not m.proposal(state,start,numerical['anchor'],'predictor')['qualified']


def test_known_linear_predictor_and_corrector():
    keys = [[str(i)] for i in range(256)]
    state = dict(keys=keys,models=np.tile([[2.,.003],[.4,1.5]],(256,1,1)).tolist())
    origin = dict(a=.2,b=.2,c=7.)
    current = dict(spec=dict(parameters=origin),vectors=[dict(key=k,value=[.02,1.]) for k in keys])
    predictor = m.proposal(state,current,origin,'predictor')
    assert predictor['qualified']
    np.testing.assert_allclose(predictor['realized_step'],[.005,-10],atol=1e-12)
    np.testing.assert_allclose(predictor['predictions'][0]['change'],[-.02,-14.998],atol=1e-12)
    corrector = m.proposal(state,current,origin,'corrector')
    np.testing.assert_allclose(corrector['realized_step'],[-.01,0],atol=1e-12)


def test_plan_does_not_bind_platform_diagnostic_bits():
    p = run.expected()
    assert 'initial_model' not in p
    assert p['maximum_a_column_relative_change'] == .1


def test_original_start_identity_is_separate(monkeypatch):
    numerical,_,_,start = context()
    point = deepcopy(start)
    original = m.old.response.correspondence
    def fail_start(cycle,reference):
        if reference is start['cycle']:
            return dict(passed=False,rows=[])
        return original(cycle,reference)
    monkeypatch.setattr(m.old.response,'correspondence',fail_start)
    assert not m.qualification(numerical,start,point)['qualified']


def test_frozen_consumer_in_separate_interpreter():
    child = subprocess.run([sys.executable,'-B','-m','scripts.run_exp508_constrained_step'],
        cwd=run.ROOT,capture_output=True,text=True,check=True)
    assert json.loads(child.stdout) == dict(valid=True,target_integrations=0,maximum_points=2,variants=256)
