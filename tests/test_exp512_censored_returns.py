"""Target-free selection, prefix preservation and honest reuse controls."""
from copy import deepcopy
import pytest
from scripts import run_exp512_censored_returns as run


@pytest.fixture(scope='module')
def previous():
    return run.inputs()


def test_fixed_all_censored_selection(previous):
    selected = run.model.selection(previous)
    assert [(r['curve'],r['node']) for r in selected]==[(0,1),(0,16),(0,17),(0,18),(0,19),(1,18),(1,19)]
    for spec in selected:
        old = previous['rows'][spec['curve']]
        assert spec['u']==old['samples'][spec['node']]['u']
        expected = dict(old['candidate'],horizon=old['candidate']['horizon']+15.)
        assert spec['candidate']==expected


@pytest.mark.parametrize('kind',['missing-sample','one-method','extra-uncertainty'])
def test_incomplete_selection_rejected(previous,kind):
    p = deepcopy(previous)
    if kind=='missing-sample':
        p['rows'][0]['samples'].pop(1)
    elif kind=='one-method':
        p['rows'][0]['samples'][1]['profiles'].pop()
    else:
        p['rows'][0]['samples'][1]['profiles'][0]['report']['uncertain_extrema']=[dict(time=1.)]
    with pytest.raises(ValueError):
        run.model.selection(p)


@pytest.mark.parametrize('kind',['unchanged','state','time','tangent','event-count','uncertainty','failed'])
def test_prefix_preservation(previous,kind):
    old = previous['rows'][0]['samples'][1]['profiles'][0]
    new = deepcopy(old)
    events = [e for e in new['report']['reconstructed'] if e['accepted']]
    if kind=='state':
        events[0]['state'][0]+=.1
    elif kind=='time':
        events[0]['time']+=.01
    elif kind=='tangent':
        events[0]['raw_tangent'][0]+=100.
    elif kind=='event-count':
        events[0]['accepted']=False
    elif kind=='uncertainty':
        new['report']['uncertain_extrema']=[dict(time=1.)]
    elif kind=='failed':
        new=dict(status='integration-failed')
    result = run.model.prefix(old,new,run.prior.load()['numerical']['thresholds'])
    assert result['passed']==(kind=='unchanged')


def test_reuse_does_not_promote_missing_ninth_return(previous):
    p = run.load()
    extensions = []
    for spec in p['selection']:
        profiles = deepcopy(previous['rows'][spec['curve']]['samples'][spec['node']]['profiles'])
        checks = [run.model.prefix(a,b,p['numerical']['thresholds']) for a,b in zip(profiles,profiles,strict=True)]
        extensions.append(dict(curve=spec['curve'],node=spec['node'],profiles=profiles,prefixes=checks))
    result = run.model.assemble(previous,extensions,p['selection'],run.prior.load()['selection']['targets'],p['numerical'])
    assert result['all_prefixes_preserved']
    assert not result['all_ninth_returns_observed']
    assert result['reused_samples']==33 and result['extended_samples']==7
    assert result['rows']==previous['rows']
    assert not result['symbolic_chains_verified']
    with pytest.raises(ValueError,match='complete fixed extension'):
        run.model.assemble(previous,extensions[:-1],p['selection'],[],p['numerical'])


def test_bounded_no_paid_review_plan():
    p = run.load()
    assert p['limits']['target_ivps']==28
    assert p['new_control_ivps']==0
    assert p['limits']['output_bytes']+p['limits']['minimum_free_bytes']<p['limits']['initial_free_bytes']
    assert p['paid_review']=='not-requested-human-approval-policy'
