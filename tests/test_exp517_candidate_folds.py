from copy import deepcopy
import json
from pathlib import Path

import pytest

from scripts import exp517_candidate_folds as model

ROOT=Path(__file__).resolve().parents[1]


def data():
    folder=ROOT/'docs/experiments/receipts'
    return {k:json.loads((folder/n).read_bytes()) for k,n in [
        ('screen','EXP-516-event-ordinal-coverage-result.json'),
        ('coverage','EXP-512-censored-return-extension-result.json'),
        ('grazing','EXP-514-candidate-grazing-boundaries-result.json')]}


def test_complete_ledger_and_prospective_mapping():
    source=data()
    value=model.selection(source)
    assert len(value['nomination_ledger'])==11
    assert sum(bool(r['known_prefix_grazing_ids']) for r in value['nomination_ledger'])==9
    assert [(c['history'],c['direction'],c['count']) for c in value['candidates']]==[(4,0,5),(4,1,5),(7,0,8),(7,1,8)]
    for a,b in zip(value['candidates'][::2],value['candidates'][1::2],strict=True):
        assert a['u_box']==a['source_u_box']
        for u,v in zip(a['u_box'],b['u_box'],strict=True):
            assert abs(a['initial_state'][0]+u*a['initial_tangent'][0]-b['initial_state'][0]-v*b['initial_tangent'][0])<1e-12
        assert b['u_box'][1]>source['coverage']['result']['rows'][1]['candidate']['grid'][-1]
        assert a['initial_tangent']!=b['initial_tangent']
        assert a['family_id']!=a['parent_family_id']
        assert a['horizon']==b['horizon']==55.670662229876534


@pytest.mark.parametrize('kind',['missing-cell','missing-cut','failed-cut','late-cut','extra-candidate'])
def test_omissions_or_changed_grazing_classification_cannot_select_a_new_matrix(kind):
    value=data()
    if kind=='missing-cell':value['screen']['analysis']['rows'][0]['ordinals'][3]['cells'][17]['endpoint_candidate']=False
    elif kind=='missing-cut':value['grazing']['rows'].pop()
    elif kind=='failed-cut':value['grazing']['rows'][0]['decision']['qualified']=False
    elif kind=='late-cut':value['grazing']['rows'][0]['candidate']['accepted_prefix']=20
    elif kind=='extra-candidate':value['screen']['analysis']['rows'][1]['ordinals'][3]['cells'][0]['endpoint_candidate']=True
    with pytest.raises(ValueError):model.selection(value)


def results():
    return [dict(candidate=dict(history=h,direction=d),assessment=dict(qualified=True,reference_restored=True),
        folds=[dict(method=m,qualification=dict(observations=[{},dict(image_state=[-6.,0.,.01],next_state=[-11.,0.,.02]),{}])) for m in ['DOP853','Radau']])
        for h,d in [(4,0),(4,1),(7,0),(7,1)]]


def test_all_four_decision_and_no_relabeling():
    value=model.cross_representation(results(),[15.,15.,.01])
    assert value['all_representations_qualified'] and value['all_references_restored']
    assert value['full_state_spread']==0
    assert value['history_returns']==[4,7]
    assert not value['original_eighth_return_restored'] and not value['symbolic_chains_verified']


@pytest.mark.parametrize('kind',['missing','failed','unsearched','reference','state'])
def test_never_average_away_a_failed_direction_history_solver_or_reference(kind):
    rows=results()
    if kind=='missing':
        rows.pop()
        with pytest.raises(ValueError):model.cross_representation(rows,[15.,15.,.01])
        return
    if kind=='failed':rows[-1]['assessment']['qualified']=False
    elif kind=='unsearched':rows[-1]['assessment']=None
    elif kind=='reference':rows[-1]['assessment']['reference_restored']=False
    elif kind=='state':rows[-1]['folds'][-1]['qualification']['observations'][1]['image_state'][2]+=.01
    value=model.cross_representation(rows,[15.,15.,.01])
    assert not value['all_references_restored']
    assert not value['original_eighth_return_restored']


def test_controller_continues_after_midpoint_failure():
    cs=[dict(id=str(i)) for i in range(4)]
    seen=[]
    def probe(c):
        seen.append(c['id'])
        return (None if c['id']=='0' else deepcopy(c)),[],dict(regular=c['id']!='0')
    rows=model.follow(cs,probe,lambda c:[],lambda c,r:dict(qualified=False))
    assert seen==['0','1','2','3']
    assert rows[0]['status']=='midpoint-unqualified'
    assert [r['status'] for r in rows[1:]]==['searched']*3


@pytest.mark.parametrize('kind',['method','nonfinite','scale'])
def test_full_solver_state_and_scale_matrix_required(kind):
    rows=results()
    scales=[15.,15.,.01]
    if kind=='method':rows[0]['folds'].pop()
    elif kind=='nonfinite':rows[0]['folds'][0]['qualification']['observations'][1]['next_state'][0]=float('nan')
    else:scales[2]=0.
    with pytest.raises(ValueError):model.cross_representation(rows,scales)


@pytest.mark.parametrize('history',[4,7])
@pytest.mark.parametrize('bad_prefix',[False,True])
def test_actual_earlier_ordinal_selection_and_whole_prefix(history,bad_prefix):
    import numpy as np
    from butterfly.poincare import PoincareSection
    from scripts.exp511_curve_coverage import observation
    settings=json.loads((ROOT/'experiments/manifests/EXP-511-direct-curve-coverage.json').read_bytes())['numerical']
    c=dict(count=history+1,seed_u=0.,time_box=[1e-8,12.])
    section=PoincareSection((0.,1.,0.),0.,-1)
    rhs=lambda t,q:np.array([-1.,-1.,0.])
    profiles=[]
    for method in ['DOP853','Radau']:
        report=dict(reconstructed=[dict(time=float(i),state=[-float(i),0.,.01],
            raw_tangent=[1.,0.,0.],angle=2**-.5,residual=0.,accepted=True) for i in range(1,10)],
            uncertain_extrema=[])
        if bad_prefix and method=='Radau':report['reconstructed'][0]['time']+=.001
        profiles.append(dict(method=method,status='completed',
            measurement=observation(report,c,rhs,section,settings['thresholds'])))
    seeded,pair=model.seed(c,profiles,settings)
    assert pair['regular'] is not bad_prefix
    if bad_prefix:assert seeded is None
    else:assert seeded['seed_time']==history+1
