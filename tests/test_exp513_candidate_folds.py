"""Target-free controls for midpoint-seeded all-candidate qualification."""
from copy import deepcopy
import json
from types import SimpleNamespace
import numpy as np
import pytest
from butterfly.poincare import PoincareSection
from scripts import run_exp513_candidate_folds as run


def settings():
    return json.loads((run.ROOT/'experiments/manifests/EXP-512-censored-return-extension.json').read_bytes())['numerical']


def synthetic():
    p=settings()
    c=dict(id='synthetic',family_id='synthetic',count=3,seed_u=0.,time_box=[1e-8,4.],epsilon=1e-6)
    rhs=lambda t,q:np.array([-1.,-1.,0.])
    section=PoincareSection((0.,1.,0.),0.,-1)
    def report(offset):
        events=[dict(time=float(i),state=[-float(i),0.,.01],raw_tangent=[1. if i<3 else offset,0.,0.],
            angle=2**-.5,residual=0.,accepted=True) for i in (1,2,3)]
        return dict(reconstructed=events,uncertain_extrema=[])
    rows=[]
    for method in p['solvers']:
        censuses=[dict(offset=e,report=report(e)) for e in (-1e-6,0.,1e-6)]
        observations=[run.model.curve.observation(v['report'],c,rhs,section,p['thresholds'])['observation'] for v in censuses]
        rows.append(dict(method=method,censuses=censuses,qualification=dict(qualified=True,observations=observations)))
    targets=[dict(id=str(i),method='synthetic',image_state=[-2.,0.,.01],next_state=[-3.,0.,.01]) for i in range(4)]
    return c,rows,targets,p,rhs,section


def test_all_five_selection():
    previous=json.loads((run.ROOT/run.RECEIPT).read_bytes())
    candidates=run.model.selection(previous)
    assert [(c['direction'],c['indices']) for c in candidates]==[(0,[1,2]),(0,[15,16]),(0,[16,17]),(1,[17,18]),(1,[18,19])]
    assert all(c['seed_time'] is None and c['count']==9 and c['horizon']>70 for c in candidates)
    previous['result']['rows'][1]['analysis']['matched_candidate_brackets'].pop()
    with pytest.raises(ValueError,match='complete five'):
        run.model.selection(previous)


@pytest.mark.parametrize('kind',['positive','failed','early-time','zero-input','methods'])
def test_midpoint_seed_admission(kind):
    c,rows,_,p,rhs,section=synthetic()
    profiles=[dict(method=r['method'],status='completed',measurement=run.model.curve.observation(
        r['censuses'][1]['report'],c,rhs,section,p['thresholds'])) for r in rows]
    if kind=='failed':
        profiles[0]=dict(method='DOP853',status='integration-failed')
    elif kind=='early-time':
        profiles[0]['measurement']['image']['events'][0]['time']+=.01
    elif kind=='zero-input':
        profiles[0]['measurement']['observation']['valid']=False
    elif kind=='methods':
        with pytest.raises(ValueError):
            run.model.seed(c,profiles[::-1],p)
        return
    candidate,pair=run.model.seed(c,profiles,p)
    assert pair['regular']==(kind=='positive')
    assert (candidate is not None)==(kind=='positive')
    if candidate is not None:
        assert candidate['seed_time']==3. and candidate['seed_u']==0.


@pytest.mark.parametrize('kind',['positive','earlier-event','missing-census','unqualified','far-z','fourth-reference','missing-reference'])
def test_complete_prefix_and_reference_gate(kind):
    c,rows,targets,p,rhs,section=synthetic()
    if kind=='earlier-event':
        rows[1]['censuses'][0]['report']['reconstructed'][0]['time']+=.01
    elif kind=='missing-census':
        rows[0]['censuses'].pop()
        with pytest.raises(ValueError):
            run.model.assessment(c,rows,dict(qualified=True),targets,p,rhs,section)
        return
    elif kind=='unqualified':
        rows[0]['qualification']['qualified']=False
    elif kind=='far-z':
        targets[0]['next_state'][2]+=.001
    elif kind=='fourth-reference':
        targets[3]['image_state'][0]+=.001
    elif kind=='missing-reference':
        with pytest.raises(ValueError):
            run.model.assessment(c,rows,dict(qualified=True),targets[:-1],p,rhs,section)
        return
    r=run.model.assessment(c,rows,dict(qualified=kind!='unqualified'),targets,p,rhs,section)
    assert r['qualified']==(kind not in ('earlier-event','unqualified'))
    assert r['reference_restored']==(kind=='positive')
    assert not r['symbolic_chains_verified'] and not r['global_root_absence_proved']


def test_complete_execution_does_not_stop_at_failed_midpoint():
    candidates=[dict(id=str(i)) for i in range(5)]
    seen=[]
    def probe(c):
        seen.append(c['id'])
        return (None if c['id']=='1' else c),[],dict(regular=c['id']!='1')
    rows=run.model.follow(candidates,probe,lambda c:[],lambda c,r:dict(qualified=False))
    assert seen==['0','1','2','3','4']
    assert rows[1]['status']=='midpoint-unqualified' and rows[1]['folds'] is None
    assert rows[-1]['status']=='searched'


def test_failed_census_mesh_retained_before_raise(tmp_path,monkeypatch):
    fake=SimpleNamespace(t=np.array([0.,.1]),y=np.zeros((6,2)),success=False,nfev=4)
    monkeypatch.setattr(run.base.section_census,'solve_ivp',lambda *a,**k:fake)
    with pytest.raises(RuntimeError):
        with run.retain_failed_censuses(tmp_path,dict(id='synthetic'),'DOP853'):
            run.base.section_census.solve_ivp(None,(0.,1.),None)
            raise RuntimeError('collector failed')
    with np.load(tmp_path/'synthetic--DOP853--failed-census-0.npz',allow_pickle=False) as raw:
        assert not raw['success'] and np.array_equal(raw['times'],fake.t)


def test_source_plan_resource_contract():
    p=run.load()
    assert p['limits']['target_ivps']==5*2*(2+8+3*2)
    assert p['limits']['output_bytes']+p['limits']['minimum_free_bytes']<p['limits']['initial_free_bytes']
    assert p['new_control_ivps']==0 and p['numerical']==settings()
    assert p['paid_review']=='not-requested-human-approval-policy'
