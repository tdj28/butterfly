"""Prospective synthetic controls; never open EXP-508 target evidence here."""
from copy import deepcopy
import json
import subprocess
import sys
import pytest
from scripts import replay_exp509_failed_predictor as run


def context():
    old = run.old
    return old.base.load(),old.prior.prior.inputs(),old.prior.inputs(),old.inputs()


@pytest.mark.parametrize('kind', ['none-contact','none-envelope','empty-envelope','short',
    'nan','infinity','negative','bool','string','unqualified'])
def test_incomplete_contact_cannot_license_corrector(kind):
    numerical,first,rejected,start = context()
    original_qualification = run.old.model.qualification
    seen = []
    def measure(p,spec):
        seen.append(spec['id'])
        assert seen == ['predictor']
        point = deepcopy(start)
        point['spec'] = spec
        if kind == 'none-contact':
            point['contact'] = None
        elif kind == 'none-envelope':
            point['contact']['envelope'] = None
        elif kind == 'empty-envelope':
            point['contact']['envelope'] = {}
        elif kind == 'short':
            point['contact']['envelope']['pair_state_distance'] = [0.]
        elif kind == 'unqualified':
            point['qualified'] = False
        else:
            value = {'nan':float('nan'),'infinity':float('inf'),'negative':-1.,'bool':True,'string':'0'}[kind]
            point['contact']['envelope']['pair_state_distance'][3] = value
        return point
    progress = run.old.model.ledger()
    result = run.follow(numerical,first,rejected,start,measure,progress)
    assert seen == ['predictor']
    assert result['analysis']['status'] == 'predictor-unqualified'
    assert not result['analysis']['accepted']
    assert not result['analysis']['joint_proximity']
    assert result['entries'][0]['changes'] == []
    assert progress[1] == dict(id='corrector',status='not-run',reason='predictor-unqualified')
    assert run.old.model.qualification is original_qualification


def test_valid_point_decision_unchanged():
    numerical,_,_,start = context()
    assert run.qualification(numerical,start,start) == run.old.model.qualification(numerical,start,start)


def test_frozen_defect_is_preserved():
    numerical,_,_,start = context()
    point = deepcopy(start)
    point['qualified'] = False
    point['contact']['envelope'] = None
    with pytest.raises(TypeError):
        run.old.model.qualification(numerical,start,point)
    assert not run.qualification(numerical,start,point)['qualified']


def test_controller_does_not_mutate_globals_after_failure():
    numerical,first,rejected,start = context()
    original = run.old.model.qualification
    def measure(*_):
        raise RuntimeError('synthetic evaluator failed')
    with pytest.raises(RuntimeError,match='synthetic evaluator'):
        run.follow(numerical,first,rejected,start,measure,run.old.model.ledger())
    assert run.old.model.qualification is original


def test_plan_is_replay_only():
    p = run.load()
    assert p['new_integrations'] == 0 and p['attempts'] == 1
    assert set(run.old.load()['source_paths']) <= set(p['source_paths'])


def test_successor_consumer_in_clean_interpreter():
    child = subprocess.run([sys.executable,'-B','-m','scripts.replay_exp509_failed_predictor'],
        cwd=run.ROOT,capture_output=True,text=True,check=True)
    assert json.loads(child.stdout) == dict(valid=True,new_integrations=0)


def test_hash_failure_precedes_any_scientific_inventory_read(monkeypatch):
    monkeypatch.setattr(run,'sha256',lambda _: 'wrong')
    def forbidden(*args,**kwargs):
        raise AssertionError('raw inventory read before identity check')
    monkeypatch.setattr(run,'inventory',forbidden)
    with pytest.raises(ValueError,match='original failure, point or marker identity'):
        run.authenticate()
