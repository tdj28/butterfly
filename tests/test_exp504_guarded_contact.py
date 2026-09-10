"""Prospective controls; synthetic residuals are not Rössler evidence."""
from copy import deepcopy
import json
import subprocess
import sys

import numpy as np
import pytest
from scripts import run_exp504_guarded_contact as run

m = run.model


@pytest.fixture(scope='module')
def historical():
    return run.base.load(),run.inputs()


def synthetic():
    keys = [[str(i)] for i in range(256)]
    models = np.tile([[1.,0.],[0.,1.]],(256,1,1))
    current = dict(spec=dict(parameters=dict(a=.2,b=.2,c=7.)),
        vectors=[dict(key=k,value=[.1,20.]) for k in keys])
    return keys,models,current


def test_linear_clipped_scalar_step():
    keys,models,current = synthetic()
    result = m.propose(models,[1]*256,current,keys,current['spec']['parameters'],1)
    assert result['qualified']
    assert result['clipping_factor'] == .5
    np.testing.assert_allclose(result['realized_step'],[-.05,-10],atol=1e-11)
    assert result['spec']['parameters']['b'] == .2


def test_unclipped_linear_known_solution():
    keys,models,current = synthetic()
    for v in current['vectors']:
        v['value'] = [.1,2.]
    result = m.propose(models,[1]*256,current,keys,current['spec']['parameters'],1)
    assert result['clipping_factor'] == 1.
    np.testing.assert_allclose(result['unclipped_step'],[-.1,-2])


@pytest.mark.parametrize('kind',['singular','wrong-orientation','condition','nonfinite','missing'])
def test_bad_model_rejected(kind):
    _,models,_ = synthetic()
    if kind == 'singular':
        models[-1,1] = 0
    elif kind == 'wrong-orientation':
        models[-1,1,1] = -1
    elif kind == 'condition':
        models[-1,1,1] = 1e-5
    elif kind == 'nonfinite':
        models[-1,0,0] = np.nan
    else:
        models = models[:-1]
    assert not m.model_check(models,[1]*256)['passed']


@pytest.mark.parametrize('kind',['missing','reordered','duplicate','nan'])
def test_missing_or_invalid_variant_matrix_rejected(kind):
    keys,_,current = synthetic()
    vectors = deepcopy(current['vectors'])
    if kind == 'missing':
        vectors.pop()
    elif kind == 'reordered':
        vectors.reverse()
    elif kind == 'duplicate':
        vectors[-1]['key'] = vectors[0]['key']
    else:
        vectors[-1]['value'][0] = float('nan')
    with pytest.raises(ValueError):
        m.values(vectors,keys)


def test_broyden_scalar_and_secant_known_update():
    _,models,_ = synthetic()
    step = np.array([2.,-1.])
    change = np.tile([3.,-2.],(256,1))
    updated = m.update(models,step,change)
    np.testing.assert_allclose(updated[0],[[1.4,-.2],[-.4,1.2]])
    np.testing.assert_allclose(updated@step,change)
    with pytest.raises(ValueError):
        m.update(models,np.zeros(2),change)


@pytest.mark.parametrize('kind',['increasing-c','a-domain','c-domain','wrong-b'])
def test_out_of_domain_proposal_rejected(kind):
    keys,models,current = synthetic()
    origin = dict(current['spec']['parameters'])
    if kind == 'increasing-c':
        for v in current['vectors']:
            v['value'][1] = -20.
    elif kind == 'a-domain':
        current['spec']['parameters']['a'] += .003
    elif kind == 'c-domain':
        current['spec']['parameters']['c'] -= .199
    else:
        current['spec']['parameters']['b'] = .3
    assert not m.propose(models,[1]*256,current,keys,origin,1)['qualified']


def test_authentic_initialization_and_warm_seed_identity(historical):
    numerical,receipt = historical
    before = deepcopy(numerical)
    state = m.initialize(numerical,receipt)
    assert state['check']['passed']
    p = m.warm_plan(numerical,receipt['proposal'])
    assert numerical == before
    assert p['cycle_seed'] == receipt['proposal']['cycle']['profiles'][0]['correction']
    assert p['reference_cycle'] == receipt['proposal']['cycle']
    assert p['fold'] == numerical['fold'] and p['periodic'] == numerical['periodic']
    for c,old,row in zip(p['fold_candidates'],numerical['fold_candidates'],receipt['proposal']['folds'],strict=True):
        assert c['initial_state'] == old['initial_state']
        assert c['seed_time'] == np.mean([r['root']['time'] for r in row['solvers']])
        assert c['time_box'] == [c['seed_time']-1,c['seed_time']+1]
    assert len(state['models']) == 256


@pytest.mark.parametrize('kind',['fold-id','boundary-id','incomplete','unqualified'])
def test_corrupt_warm_predecessor_rejected(historical,kind):
    numerical,receipt = historical
    row = deepcopy(receipt['proposal'])
    if kind == 'fold-id':
        row['folds'][0]['id'] = 'foreign'
    elif kind == 'boundary-id':
        row['boundaries'][0]['id'] = 'foreign'
    elif kind == 'incomplete':
        row['boundaries'].pop()
    else:
        row['qualified'] = False
    with pytest.raises(ValueError):
        m.warm_plan(numerical,row)


@pytest.mark.parametrize('error,accepted',[(.099,True),(.101,False)])
def test_directional_prediction_acceptance_and_rejection(historical,error,accepted):
    numerical,receipt = historical
    before = deepcopy(receipt['proposal'])
    state = m.initialize(numerical,receipt)
    # Artificial target residuals only. All old flow metadata stays as a fixture.
    proposal = m.propose(state['models'],state['signs'],before,state['keys'],numerical['anchor'],1)
    after = deepcopy(before)
    after['spec'] = proposal['spec']
    prediction = np.asarray(state['models'])@np.asarray(proposal['realized_step'])
    for v,delta in zip(after['vectors'],prediction,strict=True):
        v['value'] = (np.asarray(v['value'])+(1+error)*delta).tolist()
    result = m.decide(numerical,state,state['models'],before,after,proposal)
    assert result['accepted'] is accepted
    assert result['maximum_prediction_error'] == pytest.approx(error)


@pytest.mark.parametrize('stop',[1,4,8])
def test_stop_ledger_never_measures_a_later_or_alternative_point(monkeypatch,stop):
    keys,models,current = synthetic()
    state = dict(models=models,keys=keys,signs=[1]*256)
    monkeypatch.setattr(m,'initialize',lambda *_:state)
    monkeypatch.setattr(m,'warm_plan',lambda p,row:dict(predecessor=row))
    count = []
    monkeypatch.setattr(m,'decide',lambda *args:dict(accepted=len(count)<stop,updated_models=models,current_norm=1.))
    def measure(p,spec):
        assert p['predecessor'] is (current if not count else count[-1])
        row = dict(current,spec=spec,joint_proximity=False)
        count.append(row)
        return row
    progress = m.ledger()
    result = m.follow(dict(anchor=current['spec']['parameters']),dict(proposal=current),measure,progress)
    assert len(count) == stop
    assert all(r['status'] == 'not-run' and r['reason'] == 'measured-step-rejected' for r in progress[stop:])
    assert result['analysis']['residual_reduction'] is None
    assert result['analysis']['reduction_at_least_twenty_percent'] is False


def test_freeze_plan_and_old_numerical_closure():
    p = run.load()
    assert p['steps'] == 8 and p['attempts'] == 1
    assert p['limits']['output_bytes'] == 10*1024**3
    assert p['limits']['initial_free_bytes'] == 19*1024**3
    assert p['limits']['minimum_free_bytes'] == 8*1024**3
    # The all-tests interpreter contains unrelated modules. Test the production
    # closure in its actual isolated consumer, not that polluted test process.
    code = (f'import sys;sys.path[:0]={[str(run.ROOT),str(run.ROOT/"python")]!r};'
        'from scripts.run_exp504_guarded_contact import main;main()')
    result = subprocess.run([sys.executable,'-I','-B','-c',code],capture_output=True,text=True,check=True)
    assert json.loads(result.stdout) == dict(valid=True,target_integrations=0,steps=8,variants=256)


def test_control_hash_tamper_rejected(tmp_path):
    run.write_json(tmp_path/'control.json',{'changed':True})
    with pytest.raises(ValueError,match='inventory'):
        run.controls(tmp_path,dict(controls={'control.json':dict(bytes=1,sha256='0'*64)}))


def test_plan_tamper_rejected(tmp_path,monkeypatch):
    p = run.load()
    p['maximum_directional_error'] = 1.
    path = tmp_path/'bad.json'
    run.write_json(path,p)
    monkeypatch.setattr(run,'PLAN',path)
    with pytest.raises(ValueError,match='frozen'):
        run.load()


def test_full_auditor_hashes_before_replay(tmp_path):
    from scripts import audit_exp504_guarded_contact as audit
    run.write_json(tmp_path/'summary.json',{})
    with pytest.raises(ValueError,match='byte identity'):
        audit.audit(tmp_path,tmp_path,'0'*64)


@pytest.mark.parametrize('joint_at',[1,8,None])
def test_accepted_path_stops_at_joint_contact_or_eight(monkeypatch,joint_at):
    keys,models,current = synthetic()
    state = dict(models=models,keys=keys,signs=[1]*256)
    monkeypatch.setattr(m,'initialize',lambda *_:state)
    monkeypatch.setattr(m,'warm_plan',lambda p,row:p)
    count = []
    monkeypatch.setattr(m,'decide',lambda *args:dict(accepted=True,updated_models=models,current_norm=10.))
    def measure(p,spec):
        count.append(spec)
        return dict(current,spec=spec,joint_proximity=len(count)==joint_at)
    progress = m.ledger()
    result = m.follow(dict(anchor=current['spec']['parameters']),dict(proposal=current),measure,progress)
    assert len(count) == (joint_at or 8)
    assert result['analysis']['joint_proximity'] is (joint_at is not None)
    assert result['analysis']['residual_reduction'] == .5
    assert all(r['status'] == 'not-run' and r['reason'] == 'joint-proximity' for r in progress[len(count):])


@pytest.mark.parametrize('kind',['fold','residual','original-cycle','point'])
def test_failed_scientific_gate_cannot_be_accepted(historical,kind):
    numerical,receipt = historical
    before = deepcopy(receipt['proposal'])
    state = m.initialize(numerical,receipt)
    proposal = m.propose(state['models'],state['signs'],before,state['keys'],numerical['anchor'],1)
    after = deepcopy(before)
    after['spec'] = proposal['spec']
    prediction = np.asarray(state['models'])@np.asarray(proposal['realized_step'])
    for v,delta in zip(after['vectors'],prediction,strict=True):
        v['value'] = (np.asarray(v['value'])+delta).tolist()
    if kind == 'fold':
        after['contact']['envelope']['pair_state_distance'][3] = .000101
    elif kind == 'residual':
        after['vectors'] = deepcopy(before['vectors'])
    elif kind == 'original-cycle':
        after['cycle']['profiles'][0]['metric']['windows'][0]['event_states']['historical'][0][0] += 100
    else:
        after['qualified'] = False
    assert not m.decide(numerical,state,state['models'],before,after,proposal)['accepted']
