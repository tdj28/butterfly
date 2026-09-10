from copy import deepcopy
import math
import pytest
from scripts import exp519_fold_response as m

ANCHOR = dict(a=.21559892539912653, b=.2, c=7.152000000000001)


def residuals(values):
    return [dict(key=deepcopy(key), residual=list(values)) for key in m.KEYS]


def linear_measure(spec, intercept=None, slope=None):
    intercept = [9e-5, 0., 1.4e-4, 8e-5, 0., 1e-4] if intercept is None else intercept
    slope = [.0004, 0., .0006, .00035, 0., .0004] if slope is None else slope
    delta = (spec['parameters']['a']-ANCHOR['a'])/m.H
    return dict(spec=deepcopy(spec), qualified=True,
                vectors=residuals([x+delta*y for x, y in zip(intercept, slope, strict=True)]))


def result():
    return m.follow(ANCHOR, linear_measure(dict(parameters=ANCHOR))['vectors'], linear_measure)


def test_linear_fresh_response_one_correction_and_scalar_audit():
    from scripts.audit_exp519_fold_response import scalar_response
    r = result()
    assert r['response']['qualified'] and r['decision']['qualified_contact']
    assert len(r['points']) == 4 and len(r['response']['variants']) == 16
    assert abs(r['proposal']['realized_normalized_step']+.225) < 1e-10
    assert not r['symbolic_chains_verified'] and not r['exact_contact_verified']
    scalar_response(r, ANCHOR, linear_measure(dict(parameters=ANCHOR))['vectors'])


def test_negative_orientation_is_not_excluded():
    slope = [-.0004, 0., -.0006, -.00035, 0., -.0004]
    r = m.follow(ANCHOR, linear_measure(dict(parameters=ANCHOR))['vectors'], lambda s: linear_measure(s, slope=slope))
    assert r['response']['qualified'] and r['proposal']['realized_normalized_step'] > 0


def test_favorable_point_cannot_replace_prescribed_correction():
    def measure(s):
        p = linear_measure(s)
        if s['id'] == 'correction': p['spec']['parameters']['a'] += 1e-6
        return p
    with pytest.raises(ValueError, match='prescribed point'):
        m.follow(ANCHOR, linear_measure(dict(parameters=ANCHOR))['vectors'], measure)


@pytest.mark.parametrize('index', range(4))
def test_stencil_failure_completes_matrix_and_blocks_correction(index):
    seen = []
    def measure(s):
        p = linear_measure(s); p['qualified'] = len(seen) != index; seen.append(s['id'])
        return p
    r = m.follow(ANCHOR, residuals([0.]*6), measure)
    assert seen == [s['id'] for s in m.stencil(ANCHOR)]
    assert r['correction'] is None and not r['response']['qualified']


@pytest.mark.parametrize('kind', ['missing', 'reordered', 'wrong-b', 'wrong-c', 'wrong-a'])
def test_fixed_stencil_rejects_substitution(kind):
    points = [linear_measure(s) for s in m.stencil(ANCHOR)]
    if kind == 'missing': points.pop()
    elif kind == 'reordered': points.reverse()
    else: points[0]['spec']['parameters'][kind[-1]] += .001
    with pytest.raises(ValueError): m.response(points, ANCHOR)


@pytest.mark.parametrize('kind', ['missing', 'duplicate', 'wrong-history', 'wrong-method', 'wrong-phase', 'nan', 'infinity', 'dimension'])
def test_complete_finite_keyed_matrix(kind):
    v = residuals([0.]*6)
    if kind == 'missing': v.pop()
    elif kind == 'duplicate': v[-1] = deepcopy(v[0])
    elif kind == 'wrong-history': v[0]['key'][0] = 8
    elif kind == 'wrong-method': v[0]['key'][2] = 'RK4'
    elif kind == 'wrong-phase': v[0]['key'][3] = .5
    elif kind == 'dimension': v[0]['residual'].pop()
    else: v[0]['residual'][2] = math.nan if kind == 'nan' else math.inf
    with pytest.raises(ValueError): m.values(v)


@pytest.mark.parametrize('kind', ['unresolved', 'opposite-sign', 'nonlinear-x', 'nonlinear-z'])
def test_bad_fresh_response_blocks_correction(kind):
    def measure(s):
        p = linear_measure(s); delta = (s['parameters']['a']-ANCHOR['a'])/m.H
        if kind == 'unresolved':
            for v in p['vectors']: v['residual'][0] = 9e-5
        elif kind == 'opposite-sign': p['vectors'][0]['residual'][0] = 9e-5-delta*.0004
        else:
            axis = 0 if kind == 'nonlinear-x' else 2
            for v in p['vectors']: v['residual'][axis] += .002*delta**3
        return p
    r = m.follow(ANCHOR, linear_measure(dict(parameters=ANCHOR))['vectors'], measure)
    assert not r['response']['qualified'] and r['correction'] is None


def test_x_contact_does_not_override_full_state_failure():
    anchor = residuals([9e-5, 0., .001, 0., 0., 0.])
    measure = lambda s: linear_measure(s, [9e-5, 0., .001, 0., 0., 0.], [.0004, 0., 0., 0., 0., 0.])
    r = m.follow(ANCHOR, anchor, measure)
    assert r['response']['qualified'] and r['decision']['prediction_qualified']
    assert not r['decision']['full_state_contact'] and not r['decision']['qualified_contact']
    assert max(abs(v['signed_x']) for v in r['decision']['variants']) < 1e-12


def test_step_clipped_not_retried_and_failure_retained():
    seen = []
    def measure(s):
        p = linear_measure(s, [1., 0., 0., 0., 0., 0.]); seen.append(s['id'])
        if s['id'] == 'correction': p['qualified'] = False
        return p
    r = m.follow(ANCHOR, residuals([1., 0., 0., 0., 0., 0.]), measure)
    assert len(seen) == 5 and seen[-1] == 'correction'
    assert abs(r['proposal']['realized_normalized_step']+1.) < 1e-10
    assert not r['decision']['qualified_contact']


def test_zero_scalar_step_does_not_mask_full_state_mismatch():
    r = m.follow(ANCHOR, residuals([0., 0., .1, 0., 0., 0.]), linear_measure)
    assert r['response']['qualified'] and r['correction'] is None
    assert r['correction_not_run_reason'] == 'scalar-floor-full-state-mismatch'


def test_full_state_prediction_failure_reported_separately():
    def measure(s):
        p = linear_measure(s)
        if s['id'] == 'correction':
            for v in p['vectors']: v['residual'][2] = 9e-5
        return p
    r = m.follow(ANCHOR, linear_measure(dict(parameters=ANCHOR))['vectors'], measure)
    assert r['decision']['full_state_contact'] and not r['decision']['prediction_qualified']
    assert not r['decision']['qualified_contact']


@pytest.mark.parametrize('kind', ['slope', 'step', 'contact', 'error'])
def test_separate_scalar_audit_rejects_mutated_arithmetic(kind):
    from scripts.audit_exp519_fold_response import scalar_response
    r = result()
    if kind == 'slope': r['response']['variants'][0]['fine'][2] += .01
    elif kind == 'step': r['proposal']['spec']['parameters']['a'] += .01
    elif kind == 'contact': r['decision']['variants'][0]['full_state_distance'] += .01
    else: r['decision']['variants'][0]['prediction_error'] += .01
    with pytest.raises(ValueError): scalar_response(r, ANCHOR, linear_measure(dict(parameters=ANCHOR))['vectors'])


def test_new_candidates_preserve_curve_not_old_family_names():
    from tests.test_exp518_fold_transport import rows
    before = rows(); saved = deepcopy(before); spec = m.stencil(ANCHOR)[0]
    candidates = m.candidates(before, spec, -.03)
    assert before == saved
    for c, old in zip(candidates, before, strict=True):
        assert c['initial_state'] == [-6., -.03, .01]
        assert c['initial_tangent'] == old['candidate']['initial_tangent']
        assert c['count'] == c['history']+1
        assert c['id'].startswith('exp519-') and c['family_id'].startswith('exp519-')
        assert c['parent_id'] == old['candidate']['id']


def test_authentic_prepare_validate_and_isolated_startup():
    from scripts import run_exp519_fold_response as run
    p = run.load()
    assert p == run.expected()
    original = run.inputs(); mutated = run.inputs(); mutated['anchor']['a'] = 0
    assert run.inputs()['anchor'] == original['anchor']
    receipt = run.startup(p)
    assert receipt['passed'] and receipt['isolated'] and receipt['new_integrations'] == 0


def test_input_cache_rejects_changed_pinned_bytes(monkeypatch):
    from scripts import run_exp519_fold_response as run
    monkeypatch.setattr(run, 'sha256', lambda p: '0'*64)
    with pytest.raises(ValueError, match='fixed EXP-519 input'): run.inputs()


@pytest.mark.parametrize('kind', ['ivps', 'clock', 'disk'])
def test_resource_failure_stays_fatal_after_producer_catches_it(kind):
    from scripts import run_exp519_fold_response as run
    now, free = [0.], [100]
    budget = run.Budget(dict(wall_seconds=10, minimum_free_bytes=10, target_ivps=1), None, 0.,
                        clock=lambda: now[0], free=lambda: free[0])
    budget(True)
    assert budget.calls == 1
    budget()  # Exactly the allowed number is not itself an interruption.
    if kind == 'clock': now[0] = 11.
    if kind == 'disk': free[0] = 9
    with pytest.raises(run.base.previous.cycles_run.BudgetStop): budget(kind == 'ivps')
    now[0], free[0] = 0., 100
    with pytest.raises(run.base.previous.cycles_run.BudgetStop): budget()
    assert budget.calls == 1


def test_real_dispatcher_runs_all_folds_even_when_cycle_unqualified(tmp_path, monkeypatch):
    from contextlib import nullcontext
    from scripts import run_exp519_fold_response as run
    from tests.test_exp518_fold_transport import rows
    original = rows(); source = dict(rows=original, cycle=dict(profiles=[dict(correction={'seed': 'fixed-anchor'})]))
    p = dict(solvers=m.folds.METHODS, numerical={}, periodic={}); spec = m.stencil(ANCHOR)[0]
    calls = []; saved = {}
    def save(name, value): saved[name] = deepcopy(value)
    def cycle(s, method, seed, settings, output, budget):
        assert seed == {'seed': 'fixed-anchor'}
        calls.append(('cycle', method)); return dict(method=method, qualified=False)
    monkeypatch.setattr(run.base.previous.cycles_run, 'run_profile', cycle)
    monkeypatch.setattr(run.base.previous.cycles_run, 'compare_profiles', lambda *args: dict(passed=False))
    monkeypatch.setattr(run.coverage, 'fields', lambda c: (None, None, None))
    monkeypatch.setattr(run.coverage.dense, 'capture', lambda c, u, method, *a: dict(method=method))
    monkeypatch.setattr(run.prior, 'midpoint_seed', lambda c, profiles, p: (c, dict(regular=True)))
    monkeypatch.setattr(run.prior.prior, 'retain_failed_censuses', lambda *a: nullcontext())
    def fold(folder, c, method, settings, budget):
        calls.append(('fold', c['history'], c['direction'], method))
        return dict(method=method)
    monkeypatch.setattr(run.base, 'fold_profile', fold)
    monkeypatch.setattr(run.prior, 'assess', lambda *a: dict(qualified=False))
    monkeypatch.setattr(run, 'summarize', lambda spec, rows, cycle, *a: dict(rows=rows, cycle=cycle))
    got = run.measure(spec, tmp_path, p, source, lambda *a: None, save)
    assert calls == [('cycle', method) for method in m.folds.METHODS]+[
        ('fold', h, d, method) for h, d in m.folds.CASES for method in m.folds.METHODS]
    assert len(got['rows']) == 4 and got['cycle']['status'] == 'unqualified'
    assert spec['id']+'/point.json' in saved


def test_x_and_full_state_residuals_derive_from_fixed_events():
    contact = dict(rows=[])
    for h, d in m.folds.CASES:
        variants = []
        for method in m.folds.METHODS:
            for phase in m.PHASES:
                variants.append(dict(method=method, phase=phase, cycle_events=[[i, i, i] for i in range(6)],
                    fold_input=[2., 2., 2.], fold_output=[3., 3., 3.], signed_residual=1/15))
        contact['rows'].append(dict(family_id=f'exp519-history-{h}-direction-{d}', variants=variants))
    assert m.values(m.vectors(contact))[0].tolist() == [1/15, 1/15, 100., 1/15, 1/15, 100.]
    contact['rows'][0]['variants'][0]['signed_residual'] = 0
    with pytest.raises(ValueError, match='signed x'): m.vectors(contact)


@pytest.mark.parametrize('radius,passed', [(1e-4, True), (1e-4+1e-12, False)])
def test_exact_full_state_gate_boundary(radius, passed):
    point = dict(qualified=True, vectors=residuals([0., 0., radius, 0., 0., 0.]))
    decision = m.verdict(point, residuals([0.]*6), dict(predicted_vectors=point['vectors']))
    assert decision['full_state_contact'] == passed
    assert decision['prediction_qualified']
