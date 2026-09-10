"""Synthetic plotting controls, not target flow results."""
from copy import deepcopy

import pytest

from scripts import render_exp517_earlier_folds as figure


def fixture():
    rows=[]
    for h,d in [(4,0),(4,1),(7,0),(7,1)]:
        profiles=[]
        for method in ['DOP853','Radau']:
            obs=[dict(image_state=[-6.+15.*x,0.,.01],
                next_state=[-11.+15.*(1e-10*x-x*x),0.,.01],x_graph_slope=1e-10)
                for x in [-1e-5,0.,1e-5]]
            profiles.append(dict(method=method,qualification=dict(observations=obs,scaled_curvature=-2.),
                censuses=[dict(offset=e) for e in [-1e-6,0.,1e-6]]))
        rows.append(dict(candidate=dict(id=f'h{h}-d{d}',history=h,direction=d),
            assessment=dict(qualified=True,reference_restored=True,
                reference_distances=[dict(image_state=1e-12,next_state=2e-12) for _ in range(8)]),folds=profiles))
    return dict(rows=rows)


def test_all_four_profiles_and_measured_nonzero_slope():
    rows=figure.plot_data(fixture())
    assert len(rows)==4
    assert sum(3*len(r['curves']) for r in rows)==24
    assert all(c['center_slope']==1e-10 for r in rows for c in r['curves'])
    assert all(r['worst_reference_distance']==2e-12 for r in rows)


@pytest.mark.parametrize('kind',['missing-row','missing-method','missing-offset','missing-reference','inconsistent-verdict',
    'flat','nonfinite-sample','nonfinite-last-reference','negative-last-reference'])
def test_never_hide_a_missing_or_bad_measurement(kind):
    value=fixture()
    q=value['rows'][0]['folds'][0]['qualification']
    if kind=='missing-row':value['rows'].pop()
    elif kind=='missing-method':value['rows'][0]['folds'].pop()
    elif kind=='missing-offset':value['rows'][0]['folds'][0]['censuses'].pop()
    elif kind=='missing-reference':value['rows'][0]['assessment']['reference_distances'].pop()
    elif kind=='inconsistent-verdict':value['rows'][0]['assessment']['qualified']=False
    elif kind=='flat':q['scaled_curvature']=0.
    elif kind=='nonfinite-sample':q['observations'][0]['image_state'][0]=float('nan')
    elif kind=='nonfinite-last-reference':value['rows'][0]['assessment']['reference_distances'][-1]['next_state']=float('nan')
    else:value['rows'][0]['assessment']['reference_distances'][-1]['next_state']=-1.
    with pytest.raises(ValueError):figure.plot_data(value)


def test_missing_midpoint_and_failed_search_remain_visible():
    value=fixture()
    value['rows'][0].update(assessment=None,folds=None,status='midpoint-unqualified')
    other=deepcopy(value['rows'][1])
    other['assessment']['qualified']=False
    other['assessment']['reference_restored']=False
    for p in other['folds']:
        p['shooting']=dict(reason='fixed search box exceeded')
        p['qualification']['reason']='unqualified root'
    value['rows'][1]=other
    rows=figure.plot_data(value)
    assert len(rows)==4
    assert rows[0]['failure']==[dict(status='midpoint-unqualified')]
    assert len(rows[1]['failure'])==2
    assert rows[0]['worst_reference_distance'] is rows[1]['worst_reference_distance'] is None
