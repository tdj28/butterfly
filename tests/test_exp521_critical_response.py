"""Synthetic linear truth, nonlinearity, branch-identity and fail-closed tests."""
from copy import deepcopy
import math
import json
import numpy as np
import pytest
from scripts import exp521_critical_response as m
from scripts.audit_exp521_critical_response import scalar_check

ANCHOR = dict(a=.21559309191221962, b=.2, c=7.152000000000001)


def vector(values): return [dict(key=deepcopy(k), residual=list(values)) for k in m.fold.KEYS]
def gaps(values): return [dict(key=deepcopy(k), residual=float(values[i % 2])) for i, k in enumerate(m.GKEYS)]


def fixture():
    ja = [1e-4, 0, 2e-5, 1e-4, 0, 2e-5]; ga = [.001, .002]
    source = dict(anchor=ANCHOR, vectors=vector([0.]*6), gaps=gaps([-.02, -.03]),
        a_center=ANCHOR['a']+5e-6,
        a_response=dict(qualified=True, variants=[dict(key=deepcopy(k), fine=ja) for k in m.fold.KEYS]),
        a_gaps=dict(qualified=True, variants=[dict(key=deepcopy(k), fine=ga[i % 2]) for i, k in enumerate(m.GKEYS)]))
    def measure(spec):
        da = (spec['parameters']['a']-ANCHOR['a'])/m.HA
        dc = (spec['parameters']['c']-ANCHOR['c'])/m.HC
        return dict(spec=deepcopy(spec), qualified=True,
            vectors=vector([j*(da+.1*dc) for j in ja]),
            gaps=gaps([g+u*da+v*dc for g, u, v in zip([-.02, -.03], ga, [.005, -.001], strict=True)]))
    return source, measure


def test_linear_step_full_prediction_and_independent_scalar_audit():
    source, measure = fixture(); r = m.follow(source, measure)
    assert r['response']['qualified'] and r['decision']['qualified']
    assert len(r['points']) == 4 and len(r['decision']['folds']) == 16 and len(r['decision']['gaps']) == 8
    assert r['proposal']['normalized_c_step'] == pytest.approx(1.)
    assert not r['proposal']['derivative_centers_identical']
    assert all(x['improved'] for x in r['decision']['gaps'][::2])
    assert not any(x['improved'] for x in r['decision']['gaps'][1::2])
    assert not r['symbolic_chains_verified'] and not r['D_identified']
    scalar_check(r, source)
    assert json.loads(json.dumps(r)) == r


@pytest.mark.parametrize('index', range(4))
def test_every_stencil_failure_retained_and_blocks_correction(index):
    source, measure = fixture(); seen = []
    def failed(spec):
        p = measure(spec); p['qualified'] = len(seen) != index; seen.append(spec['id']); return p
    result = m.follow(source, failed)
    assert len(seen) == 4 and result['correction'] is None
    assert result['correction_not_run_reason'] == 'unqualified-response'
    scalar_check(result, source)


@pytest.mark.parametrize('kind', ['missing', 'order', 'wrong-a', 'wrong-b', 'wrong-c'])
def test_complete_stencil_identity(kind):
    source, measure = fixture(); points = [measure(s) for s in m.stencil(ANCHOR)]
    if kind == 'missing': points.pop()
    elif kind == 'order': points.reverse()
    else: points[0]['spec']['parameters'][kind[-1]] += .01
    with pytest.raises(ValueError): m.response(points, ANCHOR)


@pytest.mark.parametrize('kind', ['missing', 'wrong-key', 'nan', 'inf'])
def test_gap_inventory_and_finiteness(kind):
    values = gaps([-.02, -.03])
    if kind == 'missing': values.pop()
    elif kind == 'wrong-key': values[0]['key'][-1] = 6
    else: values[0]['residual'] = math.nan if kind == 'nan' else math.inf
    with pytest.raises(ValueError): m.gvalues(values)


@pytest.mark.parametrize('kind', ['gap-nonlinearity', 'fold-nonlinearity', 'failed-a', 'no-progress'])
def test_bad_response_or_no_progress_never_authorizes_step(kind):
    source, measure = fixture()
    if kind == 'failed-a': source['a_gaps']['qualified'] = False
    def changed(spec):
        p = measure(spec); dc = (spec['parameters']['c']-ANCHOR['c'])/m.HC
        if kind == 'gap-nonlinearity': p['gaps'][0]['residual'] += .02*dc**3
        elif kind == 'fold-nonlinearity': p['vectors'][0]['residual'][2] += .01*dc**3
        elif kind == 'no-progress':
            p['gaps'] = gaps([-.02+.0001*dc, -.03+.0002*dc])
        return p
    result = m.follow(source, changed)
    assert result['correction'] is None


@pytest.mark.parametrize('kind', ['full-state', 'first-gap', 'second-gap', 'wrong-spec', 'unqualified'])
def test_false_success_cannot_hide_failed_correction(kind):
    source, measure = fixture()
    def changed(spec):
        p = measure(spec)
        if spec['id'] == 'critical-step':
            if kind == 'full-state': p['vectors'][0]['residual'][2] = .001
            elif kind == 'first-gap': p['gaps'][0]['residual'] = -.1
            elif kind == 'second-gap': p['gaps'][1]['residual'] = -.1
            elif kind == 'wrong-spec': p['spec']['parameters']['b'] += .01
            else: p['qualified'] = False
        return p
    if kind == 'wrong-spec':
        with pytest.raises(ValueError): m.follow(source, changed)
    else:
        result = m.follow(source, changed)
        assert not result['decision']['qualified']
        scalar_check(result, source)


def census_fixture():
    events = [dict(cycle_phase=(i+.1)/16, state=[float(i), -float(i), float(i)],
                   signed_gap=-float(i)-.1, curvature_sign=1 if i % 2 == 0 else -1) for i in range(16)]
    return dict(profiles=[dict(method=method, qualified=True, windows=[dict(phase=w, events=deepcopy(events))
        for w in (.25, 1.25)]) for method in ('DOP853', 'Radau')])


def test_unique_cyclic_rotation_tracks_physical_objects_not_current_ordinals():
    anchor = census_fixture(); current = deepcopy(anchor)
    for p in current['profiles']:
        for w in p['windows']: w['events'] = w['events'][3:]+w['events'][:3]
    r = m.match(anchor, current)
    assert r['qualified'] and all(c['matches'][0]['shift'] == 13 for c in r['contexts'])
    assert [v['event']['state'][0] for v in r['gaps']] == [5., 13.]*4


@pytest.mark.parametrize('kind', ['missing', 'curvature', 'phase', 'state', 'unqualified', 'ambiguous', 'nan', 'shape'])
def test_false_root_identity_rejected(kind):
    anchor = census_fixture(); current = deepcopy(anchor); window = current['profiles'][0]['windows'][0]
    if kind == 'missing': window['events'].pop()
    elif kind == 'curvature': window['events'][5]['curvature_sign'] = 1
    elif kind == 'phase': window['events'][5]['cycle_phase'] += .02
    elif kind == 'state': window['events'][5]['state'][2] += 2
    elif kind == 'unqualified': current['profiles'][0]['qualified'] = False
    elif kind == 'ambiguous':
        for point in (anchor, current):
            for p in point['profiles']:
                for w in p['windows']: w['events'] = [deepcopy(w['events'][0]) for _ in range(16)]
    elif kind == 'nan': window['events'][5]['state'][2] = math.nan
    else: window['events'][5]['state'].pop()
    if kind in ('nan', 'shape'):
        with pytest.raises(ValueError): m.match(anchor, current)
    else:
        result = m.match(anchor, current)
        assert not result['qualified'] and result['gaps'] is None


@pytest.mark.parametrize('kind', ['slope', 'optimum', 'prediction', 'decision'])
def test_separate_scalar_auditor_rejects_semantic_tampering(kind):
    source, measure = fixture(); result = m.follow(source, measure)
    if kind == 'slope': result['response']['folds'][0]['fine'][0] *= 2
    elif kind == 'optimum': result['proposal']['spec']['parameters']['a'] += 1e-6
    elif kind == 'prediction': result['proposal']['predicted_gaps'][1]['residual'] += .01
    else: result['decision']['qualified'] = False
    with pytest.raises(ValueError): scalar_check(result, source)


def test_clipped_step_remains_in_old_a_domain():
    source, measure = fixture(); source['a_center'] = ANCHOR['a']+9.9e-6
    result = m.follow(source, measure)
    assert result['proposal'] is not None
    a = result['proposal']['spec']['parameters']['a']
    assert source['a_center']-m.HA <= a <= source['a_center']+m.HA
    assert abs(result['proposal']['normalized_c_step']) < 1


def test_cross_solver_root_matching_is_not_inferred_from_same_index():
    anchor = census_fixture(); current = deepcopy(anchor)
    current['profiles'][1]['windows'][1]['events'][13]['state'][0] += 2
    assert not m.match(anchor, current)['qualified']
