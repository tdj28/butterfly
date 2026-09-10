"""Prospective synthetic controller and authentic historical-input controls."""
from copy import deepcopy
import json
import subprocess
import sys
import numpy as np
import pytest
from scripts import run_exp507_fold_restoration as run


def test_authentic_unique_fixed_c_proposal():
    p = run.expected()
    old = run.inputs()
    q = p['proposal']
    assert q['spec']['parameters']['b'] == old['spec']['parameters']['b']
    assert q['spec']['parameters']['c'] == old['spec']['parameters']['c']
    assert abs(q['realized_normalized_step'][0]) < .1
    assert q['realized_normalized_step'][1] == 0
    assert len(q['predicted']) == 256
    assert q['spec']['parameters']['a'] < old['spec']['parameters']['a']
    assert p['points'] == p['attempts'] == 1


def fixture():
    numerical = run.prior.base.load()
    prior = run.prior.inputs()
    before = deepcopy(run.inputs())
    for v in before['vectors']:
        v['value'] = [.002, 1.]
    return numerical,prior,before


def test_exact_linear_correction_and_clipping():
    numerical,prior,before = fixture()
    for row in prior['response']['matrices']:
        row['matrices'][1] = [[2., 0.], [0., 2.]]
    # initialize also checks/secant-updates the synthetic models; determinant remains positive.
    p = run.model.propose(numerical,prior,before)
    assert p['unclipped_normalized_step'] == -.001
    np.testing.assert_allclose(p['realized_normalized_step'],[-.001,0],atol=1e-12)
    for v in before['vectors']:
        v['value'][0] = 2.
    p = run.model.propose(numerical,prior,before)
    assert p['unclipped_normalized_step'] == -1.
    np.testing.assert_allclose(p['realized_normalized_step'],[-.1,0],atol=1e-12)


@pytest.mark.parametrize('kind',['missing','nonfinite','negative-slope','unqualified'])
def test_invalid_proposal_inputs(kind):
    numerical,prior,before = fixture()
    if kind == 'missing':
        before['vectors'].pop()
    elif kind == 'nonfinite':
        before['vectors'][0]['value'][0] = float('nan')
    elif kind == 'negative-slope':
        prior['response']['matrices'][0]['matrices'][1][0][0] = -1
    else:
        before['qualified'] = False
    with pytest.raises(ValueError):
        run.model.propose(numerical,prior,before)


@pytest.mark.parametrize('kind',['pass','distance','adjacent','unqualified','different-spec'])
def test_primary_does_not_follow_scalar_improvement(kind):
    numerical = run.prior.base.load()
    before = run.inputs()
    proposal = run.expected()['proposal']
    point = deepcopy(before)
    point['spec'] = deepcopy(proposal['spec'])
    point['cycle']['spec'] = deepcopy(proposal['spec'])
    point['contact']['envelope']['pair_state_distance'][3] = 1e-4
    for v in point['vectors']:
        v['value'][0] = 0
    if kind == 'distance':
        point['contact']['envelope']['pair_state_distance'][3] = np.nextafter(1e-4,1.)
    elif kind == 'adjacent':
        point['correspondence']['passed'] = False
    elif kind == 'unqualified':
        point['qualified'] = False
    elif kind == 'different-spec':
        point['spec']['parameters']['c'] += .01
        with pytest.raises(ValueError):
            run.model.decide(numerical,before,point,proposal)
        return
    result = run.model.decide(numerical,before,point,proposal)
    assert result['fold_restored'] == (kind == 'pass')
    assert result['symbolic_chains_verified'] is False
    if kind in ('pass','distance'):
        assert result['half_signed_fold_reduction']


def test_frozen_source_consumer_in_isolated_interpreter():
    child = subprocess.run([sys.executable,'-B','-m','scripts.run_exp507_fold_restoration'],
        cwd=run.ROOT,capture_output=True,text=True,check=True)
    assert json.loads(child.stdout) == dict(valid=True,target_integrations=0,points=1,variants=256)


def test_warm_plan_preserves_numerics_and_input():
    numerical = run.prior.base.load()
    old = deepcopy(numerical)
    p = run.prior.model.warm_plan(numerical,run.inputs())
    assert numerical == old
    for key in ('fold','periodic','configurations','primary_radius','ledger'):
        assert p[key] == old[key]
    assert p['reference_cycle'] == run.inputs()['cycle']
