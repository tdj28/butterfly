"""Analytic continuation, physical identity transport and adversarial controls."""
from copy import deepcopy
import numpy as np
import pytest
from scripts import exp523_refreshed_path as m
from scripts.audit_exp523_refreshed_path import scalar_check


def census(g):
    profiles = []
    for mi, method in enumerate(('DOP853', 'Radau')):
        windows = []
        for wi, phase in enumerate((.25, 1.25)):
            events = [dict(state=[float(k), 0., 0.], cycle_phase=k/16,
                curvature_sign=(-1 if k % 2 else 1), signed_gap=float(k)) for k in range(16)]
            for j, k in enumerate((5, 13)):
                events[k]['signed_gap'] = float(g[(mi*2+wi)*2+j]*15)
            windows.append(dict(phase=phase, events=events))
        profiles.append(dict(method=method, windows=windows, qualified=True))
    return dict(profiles=profiles, comparison=dict(qualified=True))


def fixture():
    anchor = dict(a=.21559, b=.2, c=7.147)
    def point(spec, source=None):
        da = (spec['parameters']['a']-anchor['a'])/m.local.HA
        dc = (spec['parameters']['c']-anchor['c'])/m.local.HC
        f = (1e-9+.001*da+.0001*dc+2e-6*dc*dc)*np.array([1., 0., .2, 1., 0., .2])
        g = np.array([-.02, -.03]*4)+.0001*da-.001*dc+2e-6*dc*dc
        roots = census(g); reference = roots if source is None else source['census']
        matched = m.local.match(reference, roots)
        return dict(spec=deepcopy(spec), qualified=True,
            vectors=[dict(key=k, residual=f.tolist()) for k in m.local.fold.KEYS],
            gaps=matched['gaps'], census=roots, identity=matched, fold_point=dict(rows=[], cycle={}))
    initial = point(dict(id='initial', parameters=anchor))
    source = dict(anchor=anchor, vectors=initial['vectors'], gaps=initial['gaps'],
        census=initial['census'], rows=[], cycle={})
    return source, point


def test_two_steps_quadratic_truth_fresh_centers_and_separate_scalar_replay():
    source, measure = fixture(); seen = []
    def record(spec, current):
        seen.append((spec['id'], deepcopy(current['anchor'])))
        return measure(spec, current)
    result = m.follow(source, record)
    assert result['qualified'] and result['completed_steps'] == 2 and len(seen) == 18
    assert len({name for name, _ in seen}) == 18
    assert result['steps'][1]['anchor'] == result['accepted'][0]['parameters']
    assert all(r['refinement'] is None and r['predictor_decision']['qualified'] for r in result['steps'])
    assert result['accepted'][-1]['parameters']['c'] == pytest.approx(source['anchor']['c']-.01)
    assert all(not result[k] for k in ('symbolic_chains_verified', 'D_identified', 'exact_critical_locus_proved'))
    scalar_check(result, source)


def test_physical_roots_survive_rotated_native_census_without_mutating_measurement():
    source, measure = fixture(); spec = dict(id='rotated', parameters=source['anchor'])
    point = measure(spec, source)
    for profile in point['census']['profiles']:
        for window in profile['windows']:
            window['events'] = window['events'][3:]+window['events'][:3]
    point['identity'] = m.local.match(source['census'], point['census'])
    point['gaps'] = point['identity']['gaps']; original = deepcopy(point)
    assert all(c['matches'][0]['shift'] == 13 for c in point['identity']['contexts'])
    current = m.recenter(source, point)
    assert point == original
    matched = m.local.match(current['census'], original['census'])
    assert matched['gaps'] == source['gaps']
    assert current['census']['profiles'][0]['windows'][0]['events'][5]['state'][0] == 5.
    assert m.recenter(current, measure(spec, current))['gaps'] == source['gaps']


@pytest.mark.parametrize('bad', ['stencil', 'gap', 'geometry', 'wrong-point', 'quartic-curvature'])
def test_failed_tests_stop_without_resetting_or_second_step(bad):
    source, measure = fixture(); calls = []
    def broken(spec, current):
        calls.append(spec['id']); point = measure(spec, current)
        if bad == 'stencil' and spec['id'] == 'step-0-a-0': point['qualified'] = False
        if bad == 'gap' and spec['id'].endswith('predictor'): point['gaps'][1]['residual'] += .01
        if bad == 'geometry' and spec['id'].endswith('predictor'): point['qualified'] = False
        if bad == 'wrong-point': point['spec']['parameters']['c'] += .01
        if bad == 'quartic-curvature' and '-c-' in spec['id']:
            dc = (spec['parameters']['c']-current['anchor']['c'])/.005
            for row in point['vectors']: row['residual'][2] += .001*dc**4
        return point
    if bad == 'wrong-point':
        with pytest.raises(ValueError, match='prescribed'): m.follow(source, broken)
    else:
        result = m.follow(source, broken)
        assert not result['qualified'] and not result['accepted'] and len(result['steps']) == 1
        assert len(calls) <= 9 and result['steps'][0]['stop_reason']
        scalar_check(result, source)


def test_failed_predictor_preserved_and_one_normal_correction_permitted():
    source, measure = fixture()
    # A small unmodeled center-to-center error persists across a normal step;
    # the new correction must remove it with a separately tested prediction.
    def shifted(spec, current):
        point = measure(spec, current)
        if '-predictor' in spec['id'] or '-refinement' in spec['id']:
            for row in point['vectors']:
                row['residual'] = (np.asarray(row['residual'])+2e-7*np.array([1., 0., .2, 1., 0., .2])).tolist()
        return point
    result = m.follow(source, shifted)
    first = result['steps'][0]
    assert first['predictor_decision']['qualified'] is False
    assert first['refinement_decision']['qualified'] is True and first['accepted']
    assert first['refinement_source']['derivative_center'] == source['anchor']
    scalar_check(result, source)


@pytest.mark.parametrize('change', ['prediction', 'curvature-qualification', 'a-qualification', 'accepted-count', 'decision'])
def test_scalar_replay_rejects_semantic_mutations(change):
    source, measure = fixture(); result = m.follow(source, measure); row = result['steps'][0]
    if change == 'prediction': row['proposal']['predicted_gaps'][1]['residual'] += .01
    elif change == 'curvature-qualification': row['response']['curvature']['qualified'] = False
    elif change == 'a-qualification': row['response']['a']['qualified'] = False
    elif change == 'accepted-count': result['completed_steps'] = 1
    else: row['predictor_decision']['qualified'] = False
    with pytest.raises(ValueError): scalar_check(result, source)


def test_scalar_rejects_tight_accepted_point_with_correctly_recorded_failed_prediction():
    source, measure = fixture(); result = m.follow(source, measure); row = result['steps'][0]
    row['predictor']['vectors'][0]['residual'][2] = 1e-8
    row['predictor_decision'] = m.local.verdict(row['predictor'], source['vectors'], source['gaps'], row['proposal'])
    assert not row['predictor_decision']['qualified'] and m.tight(row['predictor'])
    with pytest.raises(ValueError, match='accepted contact'): scalar_check(result, source)
