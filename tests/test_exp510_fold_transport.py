"""Synthetic branch-transport controls; no EXP-510 target access."""
from copy import deepcopy
import json
import subprocess
import sys
import numpy as np
import pytest
from scripts import run_exp510_fold_transport as run
from scripts import audit_exp510_fold_transport as audit


def test_fixed_endpoint_and_substeps():
    start = run.prior.old.inputs()['spec']['parameters']
    finish = run.inputs()['spec']['parameters']
    rows = run.model.specifications(start,finish)
    assert len(rows) == 4 and rows[-1]['parameters'] == finish
    for i,row in enumerate(rows,1):
        assert row['parameters']['b'] == .2
        assert row['parameters']['c'] == pytest.approx(start['c']-.005*i)


@pytest.mark.parametrize('fault',['none','input-collapse','one-solver','cross-history','adjacent','missing'])
def test_full_matrix_and_stopping_rule(fault):
    numerical,start = run.base.load(),run.prior.old.inputs()
    previous = start['folds']
    seen = []
    def measure(spec,candidates):
        nonlocal previous
        seen.append(spec['id'])
        rows = deepcopy(previous)
        for r in rows:
            for v in r['solvers']:
                for key in ('image_state','next_state'):
                    v['observations'][1][key][0] += .001
        if spec['id'] == 'substep-2':
            if fault in ('input-collapse','one-solver'):
                rows[-1]['qualified_in_region'] = False
                rows[-1]['solvers'][-1]['qualified'] = False
            elif fault == 'cross-history':
                rows[-1]['solvers'][-1]['observations'][1]['image_state'][0] += .01
            elif fault == 'adjacent':
                for r in rows:
                    for v in r['solvers']:
                        v['observations'][1]['image_state'][0] += 1.
            elif fault == 'missing':
                rows.pop()
        previous = rows
        return rows
    if fault == 'missing':
        with pytest.raises(ValueError,match='complete ordered'):
            run.model.follow(numerical,start,run.inputs()['spec']['parameters'],run.offset,measure)
        return
    result = run.model.follow(numerical,start,run.inputs()['spec']['parameters'],run.offset,measure)
    assert result['transport_completed'] == (fault == 'none')
    assert len(seen) == (4 if fault == 'none' else 2)
    if fault != 'none':
        assert all(r['reason'] == 'predecessor-unqualified' for r in result['progress'][2:])
    assert not result['symbolic_chains_verified']


def test_no_failed_predecessor_seed_and_no_mutation():
    p,start = run.base.load(),run.prior.old.inputs()
    spec = run.expected()['specifications'][0]
    before = deepcopy(p)
    candidates = run.model.candidates(p,start['folds'],spec,run.offset(spec['parameters']))
    assert p == before
    assert len(candidates) == 4
    assert all(c['parameters'] == spec['parameters'] for c in candidates)
    start['folds'][-1]['qualified_in_region'] = False
    with pytest.raises(ValueError,match='qualified predecessor'):
        run.model.candidates(p,start['folds'],spec,run.offset(spec['parameters']))


def test_scalar_and_vector_identity_agree():
    before = run.prior.old.inputs()['folds']
    after = deepcopy(before)
    for i,row in enumerate(after):
        for v in row['solvers']:
            v['observations'][1]['image_state'][0] += .001+i*1e-7
    a = run.model.assess(before,after,[15.,15.,.01])
    b = audit.scalar_assess(before,after,[15.,15.,.01])
    assert b['passed'] == a['transport_qualified']
    np.testing.assert_allclose([a['cross_history_spread'],a['adjacent_displacement']],
        [b['spread'],b['change']],rtol=1e-12,atol=1e-13)


def test_no_endpoint_claim_after_incomplete_transport():
    assert run.endpoint(dict(transport_completed=False)) is None


def test_authentic_clean_interpreter_consumer():
    child = subprocess.run([sys.executable,'-B','-m','scripts.run_exp510_fold_transport'],
        cwd=run.ROOT,capture_output=True,text=True,check=True)
    assert json.loads(child.stdout) == dict(valid=True,new_integrations=0,maximum_substeps=4,folds_per_step=4)
