"""Analytic truth and controls for the prospective fixed-c correction."""
from copy import deepcopy
import json
import numpy as np
import pytest
from scripts import exp522_nonlinear_refinement as m
from scripts.audit_exp522_nonlinear_refinement import scalar_check


def fixture():
    anchor = dict(a=.21559, b=.2, c=7.147)
    f = [1e-6, 0., 2e-7, 1e-6, 0., 2e-7]; j = [v*100 for v in f]
    source = dict(anchor=anchor, a_center=anchor['a']+5e-6,
        a_derivative_center=dict(anchor, a=anchor['a']+5e-6, c=7.152),
        progress_anchor=dict(anchor, c=7.152),
        vectors=[dict(key=k, residual=f) for k in m.prior.fold.KEYS],
        gaps=[dict(key=k, residual=[-.02, -.03][i % 2]) for i, k in enumerate(m.prior.GKEYS)],
        progress_gaps=[dict(key=k, residual=[-.021, -.031][i % 2]) for i, k in enumerate(m.prior.GKEYS)],
        a_response=dict(qualified=True, variants=[dict(key=k, fine=j) for k in m.prior.fold.KEYS]),
        a_gaps=dict(qualified=True, variants=[dict(key=k, fine=[.001, -.002][i % 2]) for i, k in enumerate(m.prior.GKEYS)]))
    def measure(spec):
        da = (spec['parameters']['a']-anchor['a'])/1e-5
        return dict(spec=deepcopy(spec), qualified=True,
            vectors=[dict(key=k, residual=(np.asarray(f)+np.asarray(j)*da).tolist()) for k in m.prior.fold.KEYS],
            gaps=[dict(key=k, residual=[-.02, -.03][i % 2]+[.001, -.002][i % 2]*da)
                for i, k in enumerate(m.prior.GKEYS)])
    return source, measure


def test_linear_truth_net_progress_not_monotonic_from_imperfect_trial():
    source, measure = fixture(); result = m.follow(source, measure)
    assert result['decision']['qualified']
    assert not result['decision']['local']['qualified']
    assert all(not r['improved'] for r in result['decision']['local']['gaps'][::2])
    assert all(r['improved'] for r in result['decision']['net_progress'][::2])
    assert all(r['qualified'] for r in result['decision']['reduction'])
    assert result['proposal']['response_center'] != result['proposal']['prediction_center']
    assert result['parent_predictor_qualified'] is False and result['symbolic_chains_verified'] is False
    scalar_check(result, source)
    assert json.loads(json.dumps(result)) == result


@pytest.mark.parametrize('kind', ['full-state', 'nonlinear', 'second-gap', 'net-progress', 'unqualified', 'wrong-spec'])
def test_every_failed_gate_or_wrong_target_is_preserved(kind):
    source, measure = fixture()
    if kind == 'net-progress': source['progress_gaps'] = deepcopy(source['gaps'])
    def bad(spec):
        point = measure(spec)
        if kind == 'full-state': point['vectors'][0]['residual'][2] = .001
        elif kind == 'nonlinear': point['vectors'][0]['residual'][0] += 2e-7
        elif kind == 'second-gap': point['gaps'][1]['residual'] += .01
        elif kind == 'unqualified': point['qualified'] = False
        elif kind == 'wrong-spec': point['spec']['parameters']['c'] += .001
        return point
    if kind == 'wrong-spec':
        with pytest.raises(ValueError, match='prescribed'): m.follow(source, bad)
    else:
        result = m.follow(source, bad); assert not result['decision']['qualified']; scalar_check(result, source)


def test_tenfold_gate_is_additional_to_prediction_and_radius():
    source, measure = fixture()
    # A persistent transverse residual can be accurately predicted and remain
    # within 1e-4, yet still fail the stronger tenfold reduction requirement.
    for row in source['vectors']: row['residual'] = list(row['residual']); row['residual'][2] = 5e-7
    for row in source['a_response']['variants']: row['fine'] = list(row['fine']); row['fine'][2] = 0.
    proposed = m.proposal(source)
    point = dict(spec=proposed['spec'], qualified=True,
        vectors=deepcopy(proposed['predicted_vectors']), gaps=deepcopy(proposed['predicted_gaps']))
    result = m.follow(source, lambda spec: point)
    assert all(r['qualified'] for r in result['decision']['local']['folds'])
    assert not any(r['qualified'] for r in result['decision']['reduction'])
    assert not result['decision']['qualified']; scalar_check(result, source)


@pytest.mark.parametrize('kind', ['failed-a', 'failed-gap', 'zero-slope', 'disjoint-domain', 'no-movement'])
def test_no_authorized_step_never_calls_measure(kind):
    source, _ = fixture()
    if kind == 'failed-a': source['a_response']['qualified'] = False
    elif kind == 'failed-gap': source['a_gaps']['qualified'] = False
    elif kind == 'zero-slope':
        for row in source['a_response']['variants']: row['fine'] = [0.]*6
    elif kind == 'disjoint-domain': source['a_center'] += .1
    else:
        for row in source['vectors']: row['residual'] = [0.]*6
    def forbidden(spec): raise AssertionError('unauthorized measurement')
    assert m.follow(source, forbidden)['correction'] is None


@pytest.mark.parametrize('field', ['proposal', 'prediction', 'decision', 'reduction', 'reference'])
def test_separate_scalar_audit_rejects_tampering(field):
    source, measure = fixture(); result = m.follow(source, measure)
    if field == 'proposal': result['proposal']['normalized_a_step'] += .01
    elif field == 'prediction': result['proposal']['predicted_gaps'][1]['residual'] += .01
    elif field == 'decision': result['decision']['qualified'] = False
    elif field == 'reduction': result['decision']['reduction'][0]['qualified'] = False
    else: result['proposal']['progress_reference'] = dict(source['anchor'])
    with pytest.raises(ValueError): scalar_check(result, source)


def test_realized_clipping_and_complete_derivative_keys():
    source, _ = fixture(); source['a_center'] = source['anchor']['a']+9.99e-6
    proposed = m.proposal(source); a = proposed['spec']['parameters']['a']
    assert source['a_center']-1e-5 <= a <= source['a_center']+1e-5
    assert abs(proposed['normalized_a_step']) < .01
    source['a_response']['variants'] = source['a_response']['variants'][:-1]
    with pytest.raises(ValueError, match='identities'): m.proposal(source)
