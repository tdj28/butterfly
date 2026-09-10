"""Artifact-free controls for the prospective historical sensitivity."""
from copy import deepcopy
import json
from types import SimpleNamespace

import numpy as np
import pytest
from scripts import run_exp505_legacy_impact as run


def test_analytic_controls_remove_inflection_but_keep_extrema():
    result = run.geometry.controls()
    assert result['passed'] and len(result['cases']) == 5
    row = result['cases'][0]['geometry']
    assert row['legacy'] == [.5] and row['filtered'] == []
    assert row['candidates'][0]['opposite_derivatives'] is False
    assert row['candidates'][0]['extremum_heights'] is False


def test_separate_pair_constructor_matches_production_with_shuffled_ids():
    states = np.array([[1.,0.,10.],[2.,0.,20.],[3.,0.,30.],[4.,0.,40.]])
    times,ids = np.array([3.,0.,2.,1.]),np.array([2,1,2,1])
    raw = SimpleNamespace(midpoint_states=states,midpoint_times=times,midpoint_trajectory_ids=ids)
    for axis in (0,2):
        independent = run.geometry.pairs(states,times,ids,axis)
        production = run.historical.survivor_return_pairs(raw,axis)
        assert all(np.array_equal(a,b) for a,b in zip(independent,production,strict=True))
    np.testing.assert_array_equal(run.geometry.pairs(states,times,ids,0)[0],[2.,3.])


@pytest.mark.parametrize('kind',['duplicate-time','nonfinite','bad-axis','floating-id'])
def test_invalid_pair_evidence_rejected(kind):
    states,times,ids,axis = np.zeros((2,3)),np.array([0.,1.]),np.array([1,1]),0
    if kind == 'duplicate-time':
        times[:] = 0
    elif kind == 'nonfinite':
        states[0,0] = np.nan
    elif kind == 'bad-axis':
        axis = 1
    else:
        ids = ids.astype(float)
    with pytest.raises(ValueError):
        run.geometry.pairs(states,times,ids,axis)


def synthetic_manifest():
    return dict(oracle_common=dict(minimum_bin_points=4,grid_size=4097,minimum_prominence=.03,
        maximum_conditional_spread_ratio=.1,minimum_domain_coverage=.6,bootstrap_samples=3,
        minimum_bootstrap_consensus=.8,random_seed=186),
        oracle_variants=[dict(name=f'v{i}',options=dict(bin_count=n,smoothing=1e-5))
            for i,n in enumerate((10,12,14,12,12))],
        acceptance=dict(maximum_normalized_critical_span=.05))


def test_identical_synthetic_bootstrap_population_and_restored_helper():
    source = np.linspace(0,1,500)
    target = -(source-.5)**2
    original = run.legacy._critical_points
    a,b = [],[]
    first = run.oracle(source,target,synthetic_manifest(),'original',a)
    second = run.oracle(source,target,synthetic_manifest(),'filtered',b)
    assert first == second
    assert first['resolved'] and first['branch_count'] == 2
    assert len(a) == len(b) == 20
    assert [(r['variant'],r['ordinal']) for r in a] == [(r['variant'],r['ordinal']) for r in b]
    assert run.legacy._critical_points is original


def test_failed_fit_preserves_partial_trace_and_restores_shared_helper():
    source = np.linspace(0,1,500)
    original = run.legacy._critical_points
    trace = []
    def stop():
        raise RuntimeError('synthetic resource failure')
    with pytest.raises(RuntimeError,match='synthetic'):
        run.oracle(source,-(source-.5)**2,synthetic_manifest(),'filtered',trace,stop)
    assert len(trace) == 1
    assert run.legacy._critical_points is original


def test_fits_rejected_before_spline_creation_are_not_omitted():
    source = np.tile([0.,.2,.8,1.],125)
    trace = []
    result = run.oracle(source,-(source-.5)**2,synthetic_manifest(),'original',trace)
    assert not result['resolved']
    assert len(trace) == 5
    assert all(r['status'] == 'completed' and r['geometry'] is None and r['fit_result'][0] is None for r in trace)
    assert all(len(r['sample_sha256']) == 64 for r in trace)


def test_invalid_mode_rejected_before_any_fit():
    with pytest.raises(ValueError,match='declared'):
        run.oracle([],[],{},'alternative',[])


def test_public_plan_is_explicitly_saved_data_only():
    p = json.loads(run.PLAN.read_bytes())
    assert p['target_integrations'] == 0 and p['attempts'] == 1
    assert p['limits']['wall_seconds'] == 600
    assert p['inputs']['python/butterfly/return_map.py'] == 'd6d74c1cf34dd21a1e99a5e431f1d4451d228449e33cfbe1e0046488aabfc58b'
    assert p['historical_receipts_modified'] is False


def test_historical_hash_tamper_rejected(tmp_path,monkeypatch):
    path = tmp_path/'input.json'
    run.write_json(path,{'synthetic':True})
    monkeypatch.setattr(run,'ROOT',tmp_path)
    monkeypatch.setattr(run,'INPUTS',{'input.json':'0'*64})
    with pytest.raises(ValueError,match='historical raw'):
        run.inputs()


def test_nonfinite_metadata_has_explicit_json_representation():
    assert run.plain(dict(x=float('inf'),y=(float('-inf'),))) == dict(x='Infinity',y=['-Infinity'])
