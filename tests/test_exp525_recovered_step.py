"""Single-step recovery cannot regenerate calibration or relax scientific gates."""
from copy import deepcopy
import ast
import json
import pytest
from scripts import exp525_recovered_step as m
from scripts import run_exp525_recovered_step as run
from scripts import deploy_exp525_prax as deploy


def fixture():
    from test_exp523_refreshed_path import fixture as base
    source,measure=base()
    points=[measure(s,source) for axis in ('a','c') for s in m.prior.stencil(source['anchor'],0,axis)]
    calibration=dict(points=points,response=m.prior.response(source,points[:4],points[4:],0))
    return source,measure,calibration


def test_one_new_measurement_with_historical_calibration_and_scalar_check():
    source,measure,calibration=fixture(); names=[]
    def record(spec,current): names.append(spec['id']); return measure(spec,current)
    result=m.follow(source,calibration['response'],record)
    assert result['qualified'] and names==['step-0-predictor']
    assert result['maximum_steps']==1 and not result['symbolic_chains_verified']
    m.scalar_check(result,source,calibration)


def test_failed_predictor_retained_then_at_most_one_normal_correction():
    import numpy as np
    source,measure,calibration=fixture(); names=[]
    def shifted(spec,current):
        names.append(spec['id']); point=measure(spec,current)
        for row in point['vectors']:
            row['residual']=(np.asarray(row['residual'])+2e-7*np.array([1.,0.,.2,1.,0.,.2])).tolist()
        return point
    result=m.follow(source,calibration['response'],shifted)
    assert names==['step-0-predictor','step-0-refinement']
    assert not result['step']['predictor_decision']['qualified']
    assert result['step']['refinement_decision']['qualified'] and result['qualified']
    m.scalar_check(result,source,calibration)


@pytest.mark.parametrize('bad',['geometry','gap','wrong-point','refinement','a-center'])
def test_unchanged_failures_stop_without_further_steps(bad):
    source,measure,calibration=fixture(); names=[]
    if bad=='a-center': calibration['response']['center']=dict(source['anchor'],a=0.)
    def broken(spec,current):
        names.append(spec['id']); point=measure(spec,current)
        if bad=='geometry': point['qualified']=False
        elif bad=='gap': point['gaps'][0]['residual']+=1
        elif bad=='wrong-point': point['spec']['parameters']['a']+=1
        elif bad=='refinement':
            for row in point['vectors']: row['residual'][0]+=1e-3
        return point
    if bad in ('a-center','wrong-point'):
        with pytest.raises(ValueError): m.follow(source,calibration['response'],broken)
    else:
        result=m.follow(source,calibration['response'],broken)
        assert not result['qualified'] and len(names)==1
        m.scalar_check(result,source,calibration)


def test_scalar_rejects_false_acceptance():
    source,measure,calibration=fixture(); result=m.follow(source,calibration['response'],measure)
    result['qualified']=False
    with pytest.raises(ValueError,match='single fresh'): m.scalar_check(result,source,calibration)


def test_outcome_free_exact_sparse_closure():
    p=run.load(); hashes={n:run.sha256(run.ROOT/n) for n in p['source_paths']}
    r=deploy.rehearsal(run.ROOT,hashes)
    assert r['passed'] and not r['validation']['historical_calibration_checked']
    assert r['validation']['new_integrations']==0


def test_authentic_private_calibration_startup_when_available():
    path=run.ROOT/run.calibrated.RECEIPT
    if not path.is_file(): pytest.skip('Access-controlled completed calibration is available only on evidence hosts.')
    p=run.load(); hashes={n:run.sha256(run.ROOT/n) for n in p['source_paths']}
    r=deploy.rehearsal(run.ROOT,hashes,path)
    assert r['validation']['calibration_qualified'] and r['validation']['new_integrations']==0


def test_no_calibration_bytes_in_public_deployment():
    for launch in (False,True):
        code=deploy.bootstrap_code('a'*40,{'scripts/example.py':'b'*64},launch)
        ast.parse(code)
        assert 'exp525-recovered-step-' in code and 'codex/exp525-prax-execution' in code
        assert 'run_exp525_recovered_step as a' in code and 'artifacts/EXP-525/target-once.json' in code
        assert 'scp' not in code and 'rsync' not in code and 'audit.json' not in code


def test_fresh_attempt_required_before_any_new_measurement(tmp_path,monkeypatch):
    source,measure,calibration=fixture(); p=deepcopy(run.load())
    monkeypatch.setattr(run,'preflight',lambda c:{})
    monkeypatch.setattr(run,'load',lambda:p); monkeypatch.setattr(run,'inputs',lambda p:(source,calibration))
    monkeypatch.setattr(run,'ROOT',tmp_path)
    root=tmp_path/'artifacts/EXP-525'; root.mkdir(parents=True); (root/'target-once.json').write_text('{}')
    with pytest.raises(ValueError,match='fresh successor'): run.execute('a'*40)
    assert not (root/'target-01').exists()


def test_plan_reserves_full_output_and_forbids_second_step():
    p=run.load(); limits=p['limits']
    assert limits['initial_free_bytes'] >= limits['output_bytes']+limits['minimum_free_bytes']
    assert p['maximum_steps']==1 and p['maximum_new_points']==2
    assert limits['wall_seconds']==21600 and p['paid_api_calls']==p['new_provider_creates']==0
    assert run.calibrated.RECEIPT not in p['source_paths']


def test_real_collection_writer_and_raw_census_audit_with_synthetic_geometry(tmp_path,monkeypatch):
    import numpy as np
    p=deepcopy(run.load()); p['source_paths']=[]
    p['limits'].update(initial_free_bytes=0,minimum_free_bytes=0)
    source=run.old.inputs(); spec=dict(id='step-0-predictor',parameters=source['anchor'])
    calibration=dict(response={})
    monkeypatch.setattr(run,'ROOT',tmp_path); monkeypatch.setattr(run,'load',lambda:p)
    monkeypatch.setattr(run,'inputs',lambda path:(source,calibration))
    private=tmp_path/'private.json'; private.write_text('{}')
    monkeypatch.setattr(run,'RAW_CALIBRATION',private)
    monkeypatch.setattr(run.calibrated,'SHA',run.sha256(private))
    plan=tmp_path/run.PLAN; plan.parent.mkdir(parents=True); plan.write_text('{}')
    monkeypatch.setattr(run,'preflight',lambda c:dict(source_hashes={},runtime={'synthetic':True}))
    monkeypatch.setattr(run.calibrated.audit,'protect_historical_tree',lambda:None)
    def summarize(spec,rows,cycle,p,current):
        return dict(spec=spec,qualified=False,vectors=None,cycle=cycle,rows=[],fold_identity={},contact=None)
    def measure(spec,output,p,current,budget,save):
        stage=output/spec['id']; stage.mkdir(); configs=[]
        candidates=run.old.prior.model.candidates(current['rows'],spec,run.old.prior.prior.transport.offset(spec['parameters']))
        save(spec['id']+'/inputs.json',dict(spec=spec,candidates=candidates))
        for method in p['solvers']:
            budget(True)
            raw=dict(times=np.array([0.,1.,2.5]),states=np.ones((3,3)),dense_old=np.ones((2,3)),
                dense_coefficients=np.zeros((2,7,3) if method=='DOP853' else (2,3,3)),
                historical_extrema_times=np.array([]),historical_extrema_states=np.empty((0,3)))
            np.savez(stage/(spec['id']+'--'+method+'--observation.npz'),**raw)
            configs.append(dict(method=method,correction=dict(period_time=1.)))
        cycle=dict(profiles=configs); point=summarize(spec,[],cycle,p,current)
        save(spec['id']+'/cycle.json',cycle); save(spec['id']+'/point.json',point)
        return point
    monkeypatch.setattr(run.old.prior,'measure',measure); monkeypatch.setattr(run.old.prior,'summarize',summarize)
    monkeypatch.setattr(run.full.folds,'check_rows',lambda *args:([],set(),0))
    monkeypatch.setattr(run.full.folds.raw.old,'check_cycle',lambda stage,cycle,spec,seed,p:
        ({spec['id']+'--'+m+'--observation.npz' for m in ('DOP853','Radau')},2))
    monkeypatch.setattr(run.full.folds.transport_audit,'scalar_decision',lambda *args:None)
    monkeypatch.setattr(run.model,'follow',lambda current,response,measure:dict(point=measure(spec,current),qualified=False))
    monkeypatch.setattr(run.model,'scalar_check',lambda *args:None)
    run.execute('a'*40)
    out=tmp_path/'artifacts/EXP-525/target-01'; receipt=run.old.read(out/'audit.json')
    assert receipt['passed'] and receipt['target_ivps']==2 and receipt['segments']==4
    assert not receipt['result']['qualified'] and not receipt['symbolic_chains_verified']
    assert (out.parent/'target-once.json').is_file() and not (out/'failure.json').exists()


def test_timeout_receipt_preserves_started_attempt(tmp_path,monkeypatch):
    p=deepcopy(run.load()); p['limits']['minimum_free_bytes']=0
    source,_,calibration=fixture()
    monkeypatch.setattr(run,'ROOT',tmp_path); monkeypatch.setattr(run,'load',lambda:p)
    monkeypatch.setattr(run,'inputs',lambda path:(source,calibration))
    monkeypatch.setattr(run,'preflight',lambda c:dict(source_hashes={},runtime={'synthetic':True}))
    plan=tmp_path/run.PLAN; plan.parent.mkdir(parents=True); plan.write_text('{}')
    monkeypatch.setattr(run.calibrated.audit,'protect_historical_tree',lambda:None)
    trace=[]
    monkeypatch.setattr(run.signal,'signal',lambda *args:None)
    monkeypatch.setattr(run.signal,'alarm',lambda n:trace.append(n))
    def fail(*args):
        assert 21600 in trace
        raise TimeoutError('forced collection timeout')
    monkeypatch.setattr(run.model,'follow',fail)
    with pytest.raises(TimeoutError): run.execute('a'*40)
    out=tmp_path/'artifacts/EXP-525/target-01'
    assert run.old.read(out/'failure.json')['error_type']=='TimeoutError'
    assert (out.parent/'target-once.json').is_file() and not (out/'audit.json').exists()
