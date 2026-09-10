from copy import deepcopy
import math
import pytest
from scripts import exp518_fold_transport as m


def rows():
    out=[]
    for h,d in m.CASES:
        c=dict(id=f'old-{h}-{d}',history=h,direction=d,parameters=dict(a=.21,b=.2,c=7.162),
               initial_state=[-6.,-.02,.01],initial_tangent=[15.,0.,0.],count=h+1,epsilon=1e-6)
        obs=dict(image_state=[-6.,-.02,.01],next_state=[-11.,-.02,.02])
        profiles=[dict(method=method,shooting=dict(trace=[dict(u=.01,time=30.)]),
                       qualification=dict(qualified=True,observations=[deepcopy(obs) for _ in range(3)]))
                  for method in m.METHODS]
        out.append(dict(candidate=c,seeded_candidate=deepcopy(c),folds=profiles,assessment=dict(qualified=True)))
    return out


def specs():
    return [dict(id=f'substep-{i}',parameters=dict(a=.21,b=.2,c=c))
            for i,c in enumerate([7.167,7.162,7.157,7.152],1)]


def test_exact_saved_specs_no_reinterpolation():
    old=specs();new=m.specifications(old,rows()[0]['candidate']['parameters'])
    assert new==old[2:]
    new[0]['parameters']['c']=0
    assert old[2]['parameters']['c']==7.157


@pytest.mark.parametrize('kind',['start','missing','order','b','nonfinite','direction'])
def test_bad_parameter_path(kind):
    old=specs();start=rows()[0]['candidate']['parameters']
    if kind=='start': start['a']+=.001
    elif kind=='missing':old.pop()
    elif kind=='order':old.reverse()
    elif kind=='b':old[2]['parameters']['b']=.3
    elif kind=='nonfinite':old[2]['parameters']['a']=math.nan
    else:old[2]['parameters']['c']=7.2
    with pytest.raises(ValueError):m.specifications(old,start)


def test_warm_roots_preserve_actual_curve_and_history():
    before=rows();saved=deepcopy(before)
    cs=m.candidates(before,specs()[2],-.03)
    assert before==saved
    for c,r in zip(cs,before,strict=True):
        assert (c['history'],c['direction'])==(r['candidate']['history'],r['candidate']['direction'])
        assert c['count']==c['history']+1
        assert c['initial_state']==[-6.,-.03,.01]
        assert c['initial_tangent']==[15.,0.,0.]
        assert c['seed_u']==.01 and c['seed_time']==30
        assert c['u_box']==[-.01,.03] and c['time_box']==[29.,31.]
        assert c['horizon']==33.


@pytest.mark.parametrize('kind',['missing-case','missing-method','bad-state','prefix-failure','spread'])
def test_bad_predecessor_cannot_seed(kind):
    r=rows()
    if kind=='missing-case':r.pop()
    elif kind=='missing-method':r[0]['folds'].pop()
    elif kind=='bad-state':r[0]['folds'][0]['qualification']['observations'][1]['next_state'][2]=math.nan
    elif kind=='prefix-failure':r[0]['assessment']['qualified']=False
    else:r[0]['folds'][0]['qualification']['observations'][1]['next_state'][2]+=.001
    with pytest.raises(ValueError):m.candidates(r,specs()[2],-.03)


def test_cross_history_and_adjacent_displacement_are_distinct():
    before=rows();after=deepcopy(before)
    for r in after:
        for p in r['folds']:p['qualification']['observations'][1]['next_state'][2]+=.00011
    q=m.decision(before,after)
    assert q['cross_history_spread']==0
    assert q['adjacent_displacement']>.01 and not q['transport_qualified']
    assert not q['original_eighth_return_restored'] and not q['symbolic_chains_verified']


@pytest.mark.parametrize('failure',[None,0,1])
def test_controller_complete_matrix_and_conditional_second_stage(failure):
    start=rows();calls=[]
    def measure(spec,candidates):
        r=rows()
        for v,c in zip(r,candidates,strict=True):v.update(candidate=deepcopy(c),seeded_candidate=deepcopy(c))
        if len(calls)==failure:r[3]['assessment']['qualified']=False
        calls.append(spec['id'])
        return r
    result=m.follow(start,specs()[2:],lambda _: -.02,measure)
    assert len(calls)==(1 if failure==0 else 2)
    assert result['transport_completed']==(failure is None)
    assert all(len(r['rows'])==4 for r in result['rows'])
    if failure==0:assert result['progress'][1]['reason']=='predecessor-unqualified'


def test_controller_rejects_missing_measured_candidate():
    with pytest.raises(ValueError):m.follow(rows(),specs()[2:],lambda _: -.02,lambda s,c:[])


@pytest.mark.parametrize('times,regular,expected',[
    ([29.5,30.5],True,30.),([28.,28.],True,None),([31.,31.],True,None),
    ([30.,30.],False,None)])
def test_midpoint_seed_keeps_fixed_time_box(monkeypatch,times,regular,expected):
    from scripts import run_exp518_fold_transport as run
    monkeypatch.setattr(run.coverage.model,'pair',lambda profiles,scales:dict(regular=regular))
    c=dict(time_box=[29.,31.],seed_time=30.,seed_u=.01)
    profiles=[dict(measurement=dict(image=dict(events=[dict(time=t)]))) for t in times]
    seeded,pair=run.midpoint_seed(c,profiles,dict(numerical=dict(scales=m.SCALES)))
    if expected is None:
        assert seeded is None
        if regular:assert pair['seed_failure']=='observed-midpoint-outside-fixed-time-box'
    else:assert seeded['seed_time']==expected
    assert c['time_box']==[29.,31.] and c['seed_time']==30.


def test_endpoint_comparison_is_not_run_after_transport_failure(monkeypatch):
    from scripts import run_exp518_fold_transport as run
    def forbidden():raise AssertionError('failed transport accessed endpoint')
    monkeypatch.setattr(run.transport,'inputs',forbidden)
    assert run.endpoint(dict(transport_completed=False)) is None


def test_separate_transport_arithmetic_detects_wrong_distance():
    from scripts import audit_exp518_fold_transport as audit
    a=rows();b=deepcopy(a)
    for r in b:
        for p in r['folds']:p['qualification']['observations'][1]['image_state'][0]+=.001
    d=m.decision(a,b);audit.scalar_decision(a,b,d)
    d['adjacent_displacement']=0.
    with pytest.raises(ValueError):audit.scalar_decision(a,b,d)


@pytest.mark.parametrize('change_prefix',[False,True])
def test_actual_local_qualification_keeps_complete_event_prefix(monkeypatch,change_prefix):
    import json
    from scripts import run_exp518_fold_transport as run
    saved=json.loads((run.ROOT/run.RECEIPT).read_bytes())
    p=json.loads(run.prior.PLAN.read_bytes())
    p['historical_targets']=p['targets']
    monkeypatch.setattr(run.prior,'load',lambda:p)
    row=saved['rows'][0];profiles=deepcopy(row['folds'])
    if change_prefix:
        next(v for v in profiles[0]['censuses'][0]['report']['reconstructed'] if v['accepted'])['time']+=.01
    assessed=run.assess(row['seeded_candidate'],profiles,p)
    assert assessed['qualified']==(not change_prefix)
    assert len(assessed['prefix_pairs'])==3
    assert not assessed['symbolic_chains_verified']


def test_reused_cycle_cannot_be_compared_at_different_parameters(monkeypatch):
    from scripts import run_exp518_fold_transport as run
    old=dict(spec=dict(parameters=dict(a=.22,b=.2,c=7.152)))
    monkeypatch.setattr(run.transport,'inputs',lambda:old)
    result=dict(transport_completed=True,rows=[{},dict(spec=specs()[-1],rows=rows())])
    with pytest.raises(ValueError,match='exact endpoint'):run.endpoint(result)
