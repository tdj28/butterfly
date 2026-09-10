"""Target-free nomination and actual combined grazing-pipeline controls."""
from copy import deepcopy
import json
from types import SimpleNamespace
import numpy as np
import pytest
from scripts import run_exp514_grazing_candidates as run


def inputs():
    return [json.loads((run.ROOT/name).read_bytes()) for name in (run.previous.RECEIPT, run.RECEIPT)]


def settings():
    return dict(grazing=json.loads(run.old.PLAN.read_bytes()),
                numerical=json.loads(run.previous.PLAN.read_bytes())['numerical'])


def test_complete_event_nomination():
    cs = run.model.selection(*inputs())
    assert len(cs) == 5
    assert [c['extremum_index'] for c in cs] == [3, 11, 19, 11, 19]
    assert [c['accepted_prefix'] for c in cs] == [1, 5, 8, 5, 8]
    assert all(c['time_box'][0] < c['seed_time'] < c['time_box'][1] for c in cs)
    assert all(c['original_u_box'][0] <= c['u_box'][0] < c['u_box'][1] <= c['original_u_box'][1] for c in cs)


@pytest.mark.parametrize('kind', ['missing', 'irregular', 'extrema-count', 'sign', 'prefix', 'slope'])
def test_ambiguous_or_incomplete_nomination_rejected(kind):
    a, b = inputs()
    row = b['rows'][0]
    if kind == 'missing':
        b['rows'].pop()
    elif kind == 'irregular':
        row['midpoint_pair']['regular'] = False
    elif kind == 'extrema-count':
        row['midpoints'][0]['report']['extrema'].pop()
    elif kind == 'sign':
        row['midpoints'][0]['report']['extrema'][3]['plane_value'] *= -1
    elif kind == 'prefix':
        report = row['midpoints'][0]['report']
        next(e for e in report['reconstructed'] if e['accepted'])['accepted'] = False
    else:
        row['midpoints'][0]['measurement']['observation']['x_graph_slope'] *= -1
    with pytest.raises(ValueError):
        run.model.selection(a, b)


def synthetic_roots(c):
    q = dict(u=-1e-5, time=1., state=[0., 0., 1.], residual=[0., 0.], jacobian=[[2., 0.], [0., 2.]])
    return dict(converged=True, trace=[q])


def test_actual_sequence_keeps_all_failed_sides_and_both_solvers():
    c = dict(run.old.control_specs()[0], count=2)
    seen = []
    def observe(c, i, u, method):
        seen.append((i, method))
        return dict(method=method, status='integration-failed')
    row = run.model.run_candidate(c, settings()['grazing'], lambda c,m:synthetic_roots(c), observe)
    assert seen == [(i,m) for i in range(4) for m in ('DOP853','Radau')]
    assert not row['decision']['qualified'] and not row['decision']['symbolic_chains_verified']
    assert row['decision']['reason'] == 'side integration failed'
    row['sides'].pop()
    with pytest.raises(ValueError, match='complete prescribed'):
        run.model.decision(c, row['roots'], row['sides'], settings()['grazing'])


@pytest.mark.parametrize('kind', ['grazing', 'no-root-in-box'])
def test_actual_combined_producer_analytic_controls(tmp_path, kind):
    p = settings()
    c = dict(run.old.control_specs()[0 if kind=='grazing' else 3], count=2)
    rhs, jac = run.old.fields_for_control(c)
    calls = []
    saved = {}
    def budget(integrating=False):
        if integrating:
            calls.append(True)
    result = run.produce(c, p, tmp_path, budget, lambda n,v:saved.update({n:v}),
        (rhs, jac, run.PoincareSection((0.,1.,0.), 0., -1)))
    assert result['decision']['qualified'] == (kind=='grazing')
    assert len(calls) == len(list(tmp_path.glob('*.npz')))
    assert not result['decision']['projected_fold_qualified']
    assert len(result['sides']) == (4 if kind=='grazing' else 0)
    if kind=='grazing':
        assert all(abs(r['shooting']['trace'][-1]['u']+1e-5)<1e-9 for r in result['roots'])


def test_failed_shooting_retains_mesh_and_no_side_targets(tmp_path, monkeypatch):
    c = dict(run.old.control_specs()[0], count=2)
    initial = np.r_[c['initial_state'], c['initial_tangent']]
    monkeypatch.setattr(run.model.boundary, 'solve_ivp', lambda *a,**k:SimpleNamespace(
        success=False, t=np.array([0.,.1]), y=np.column_stack([initial,initial])))
    rhs, jac = run.old.fields_for_control(c)
    result = run.produce(c, settings(), tmp_path, lambda *_:None, lambda *_:None,
        (rhs, jac, run.PoincareSection((0.,1.,0.),0.,-1)))
    assert len(list(tmp_path.glob('*.npz'))) == 2
    assert not result['sides'] and not result['decision']['qualified']
    assert all(r['shooting']['reason']=='integration failed' for r in result['roots'])


def test_frozen_plan_and_budget():
    p = run.load()
    assert str(run.old.PLAN.relative_to(run.ROOT)) in p['source_paths']
    assert p['limits']['target_ivps'] == 5*(2*8+4*2*2)
    assert p['limits']['output_bytes']+p['limits']['minimum_free_bytes'] < p['limits']['initial_free_bytes']
    assert p['paid_review']=='not-requested-human-approval-policy'
    assert p['grazing']['square_root_ratio_relative_error'] == .05
