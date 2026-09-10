"""Target-free controls for direct coverage and retained dense replay."""
from copy import deepcopy
import math
from types import SimpleNamespace
import numpy as np
import pytest
from scripts import run_exp511_curve_coverage as run
from scripts import audit_exp511_curve_coverage as audit


@pytest.fixture(scope='module')
def analytic():
    rows = []
    for kind in ('fold','no-fold','projection-degenerate'):
        c,u,p,(rhs,jac,section),k = run.control_case(kind)
        for method in ('DOP853','Radau'):
            raws,calls = {},[]
            profile = run.dense.capture(c,u,method,p,rhs,jac,section,
                lambda name,raw:raws.update({name:raw}),lambda yes:calls.append(yes))
            rows.append((kind,c,u,p,rhs,section,k,profile,raws,calls))
    return rows


@pytest.mark.parametrize('index',range(6))
def test_analytic_dense_replay(analytic,index):
    kind,c,u,p,rhs,section,k,profile,raws,calls = analytic[index]
    replay = run.dense.replay(profile,c,u,p,rhs,section,raws)
    assert run.public.equal(replay,profile)
    assert run.control_verdict(replay,c,u,k)['passed']
    assert calls==[True,True]
    assert replay['measurement']['observation']['valid']==(kind!='projection-degenerate')


@pytest.mark.parametrize('mutation',['coefficient','old','guard','event','configuration','omission'])
def test_dense_tampering_rejected(analytic,mutation):
    _,c,u,p,rhs,section,_,profile,raws,_ = deepcopy(analytic[0])
    if mutation=='coefficient':
        raws['main']['dense_coefficients'][0,0,0]+=.01
    elif mutation=='old':
        raws['main']['dense_old'][0,0]+=.01
    elif mutation=='guard':
        raws['guard']['augmented_states'][-1,0]+=.01
    elif mutation=='event':
        raws['main']['plane_augmented_states'][0,0]+=.01
    elif mutation=='configuration':
        p['guard']*=2
    else:
        del raws['main']
    with pytest.raises(ValueError):
        run.dense.replay(profile,c,u,p,rhs,section,raws)


def test_report_tamper_detected_by_comparison(analytic):
    _,c,u,p,rhs,section,_,profile,raws,_ = deepcopy(analytic[0])
    profile['report']['reconstructed'][0]['raw_tangent'][0]+=.01
    assert not run.public.equal(run.dense.replay(profile,c,u,p,rhs,section,raws),profile)


def test_failed_guard_retained_before_raise(monkeypatch):
    c,u,p,(rhs,jac,section),_ = run.control_case('fold')
    q = np.r_[np.asarray(c['initial_state'])+u*np.asarray(c['initial_tangent']),c['initial_tangent']]
    sol = SimpleNamespace(t=np.array([0.]),y=q[:,None],success=False,nfev=1,njev=0)
    monkeypatch.setattr(run.dense.section_census,'solve_ivp',lambda *a,**k:sol)
    raws = {}
    profile = run.dense.capture(c,u,'DOP853',p,rhs,jac,section,lambda n,r:raws.update({n:r}),lambda _:None)
    assert profile['status']=='integration-failed'
    assert list(raws)==['guard']
    assert run.dense.replay(profile,c,u,p,rhs,section,raws)==profile


def test_unexpected_error_not_silently_dropped(monkeypatch):
    c,u,p,(rhs,jac,section),_ = run.control_case('fold')
    def fail(*args,**kwargs):
        raise ValueError('unexpected')
    monkeypatch.setattr(run.dense.section_census,'solve_ivp',fail)
    with pytest.raises(ValueError,match='unexpected'):
        run.dense.capture(c,u,'DOP853',p,rhs,jac,section,lambda *a:None,lambda _:None)


def test_grid_complete_and_fixed():
    c = dict(u_box=[-.02,.02],epsilon=1e-6)
    grid = run.model.grid(c,[.003,.003])
    assert len(grid)==20 and grid[0]==-.02 and grid[-1]==.02
    assert all(x in grid for x in [.003-1e-6,.003,.003+1e-6])
    for roots in ([.03,.03],[float('nan'),0.],[0.]):
        with pytest.raises(ValueError):
            run.model.grid(c,roots)


def samples(slopes,turn=False,invalid=None):
    result = []
    for i,slope in enumerate(slopes):
        profiles = []
        for method in ('DOP853','Radau'):
            sign = -1 if turn and i==0 else 1
            before = dict(time=1.,state=[-1.,0.,.01],tangent=[sign,0.,0.])
            after = dict(time=2.,state=[-2.,0.,.01],tangent=[sign*slope,0.,0.])
            image = dict(status='returned',events=[before,after])
            observation = run.model.observe_curve(image)
            if i==invalid:
                observation.update(valid=False,x_graph_slope=None)
            profiles.append(dict(method=method,status='completed',measurement=dict(image=image,observation=observation)))
        result.append(dict(u=float(i),profiles=profiles,pair=run.model.pair(profiles,[15.,15.,.01])))
    return result


@pytest.mark.parametrize('slopes,turn,invalid,brackets',[
    ([-1.,1.],False,None,[[0,1]]),([-1.,1.],True,None,[]),
    ([-1.,1.],False,0,[]),([-1.,0.,1.],False,None,[[0,2]]),
    ([1.,1.,1.],False,None,[])])
def test_bracket_gaps_and_no_absence_claim(slopes,turn,invalid,brackets):
    data = samples(slopes,turn,invalid)
    c = dict(family_id='synthetic',grid=[s['u'] for s in data])
    targets = [dict(image_state=[-1.,0.,.01],next_state=[-2.,0.,.01])]*4
    result = run.model.analyze(c,data,targets)
    audit.scalar_check(c,data,targets,result)
    assert result['matched_candidate_brackets']==brackets
    assert not result['global_root_absence_proved']
    assert len(result['all_unsampled_cells_not_certified'])==len(data)-1
    with pytest.raises(ValueError,match='complete fixed grid'):
        run.model.analyze(c,data[:-1],targets)


def test_solver_disagreement_and_nonfinite():
    data = samples([1.,1.])
    profiles = deepcopy(data[0]['profiles'])
    profiles[1]['measurement']['image']['events'][0]['state'][0]+=.1
    assert not run.model.pair(profiles,[15.,15.,.01])['regular']
    profiles[1]['measurement']['image']['events'][0]['state'][0]=math.nan
    with pytest.raises(ValueError,match='nonfinite'):
        run.model.pair(profiles,[15.,15.,.01])
    with pytest.raises(ValueError,match='ordered solver pair'):
        run.model.pair(profiles[::-1],[15.,15.,.01])


def test_historical_inputs_and_bounds():
    p = run.load()
    assert len(p['selection']['curves'])==2
    assert sum(len(c['grid'])*4 for c in p['selection']['curves'])<=p['limits']['target_ivps']==160
    assert p['limits']['output_bytes']+p['limits']['minimum_free_bytes']<p['limits']['initial_free_bytes']
    assert p['newton_refinements']==0
    assert p['paid_review']=='not-requested-human-approval-policy'
