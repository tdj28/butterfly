"""Frozen design, authentic isolated startup and hostile metadata controls."""
from copy import deepcopy
import json
from pathlib import Path

import numpy as np
import pytest
from scripts import run_exp520_periodic_census as run
from scripts import audit_exp520_periodic_census as auditor


def test_complete_result_free_plan_and_isolated_production_consumer():
    plan = run.load()
    assert len(plan['trials']) == 5 and len(plan['observations']) == 10
    assert plan['total_segments'] == 417460
    assert plan['new_integrations'] == 0 and not plan['symbolic_chains_verified']
    assert plan['windows'] == [.25, 1.25]
    assert run.startup(plan)['passed']
    assert run.controls()['passed']


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'order', 'dtype', 'shape', 'count', 'hash', 'source'])
def test_self_consistent_input_metadata_mutations_rejected(tmp_path, monkeypatch, mutation):
    meta = json.loads(run.META.read_bytes())
    if mutation == 'missing': meta['observations'].pop()
    elif mutation == 'duplicate': meta['observations'].append(deepcopy(meta['observations'][0]))
    elif mutation == 'order': meta['observations'].reverse()
    elif mutation == 'dtype': meta['observations'][0]['arrays']['dense_old.npy']['dtype'] = 'float32'
    elif mutation == 'shape': meta['observations'][0]['arrays']['dense_coefficients.npy']['shape'][1] = 6
    elif mutation == 'count':
        for row in meta['observations']:
            for array in row['arrays'].values(): array['shape'][0] -= 1
    elif mutation == 'hash': meta['observations'][0]['sha256'] = 'bad'
    else: meta['raw_summary_sha256'] = '0'*64
    path = tmp_path/'metadata.json'; path.write_text(json.dumps(meta))
    monkeypatch.setattr(run, 'META', path)
    with pytest.raises(ValueError): run.expected()


def test_parent_byte_mutation_cannot_supply_a_self_consistent_new_audit(tmp_path, monkeypatch):
    (tmp_path/'parent.json').write_text('{}')
    monkeypatch.setattr(run, 'ROOT', tmp_path); monkeypatch.setattr(run, 'PARENT', 'parent.json')
    with pytest.raises(ValueError, match='immutable'): run.parent_points()


def test_input_header_reader_never_needs_values(tmp_path):
    path = tmp_path/'control.npz'
    np.savez(path, times=np.array([0., 1.]), dense_old=np.ones((1, 3)), dense_coefficients=np.ones((1, 7, 3)))
    header = run.headers(path)
    assert header['dense_coefficients.npy'] == dict(shape=[1, 7, 3], fortran=False, dtype='float64')


def test_auditor_structural_boolean_and_nonfinite_rejection():
    assert auditor.same(dict(a=[.006, True]), dict(a=[.006+1e-18, True]))
    assert not auditor.same(dict(a=[.006, True]), dict(a=[.006, 1]))
    assert not auditor.same([.006], [.00601])
    assert not auditor.same([float('nan')], [float('nan')])
    assert not auditor.same([1], [1, 2])
    assert not auditor.same(dict(a=1), dict(a=1, b=2))


def test_public_input_paths_and_source_closure_exist():
    plan = run.load()
    assert run.PARENT in plan['inputs']
    assert set(run.EXPLICIT) <= set(plan['source_paths'])
    for name in set(plan['source_paths']) | set(plan['inputs']):
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert (run.ROOT/name).is_file()
    assert all(not n.startswith('artifacts/') for n in plan['source_paths'])


def test_synthetic_execution_and_audit_preserve_unqualified_results(tmp_path, monkeypatch):
    """Exercise real writers and census/auditor, with synthetic authority only."""
    plan = deepcopy(run.load())
    plan['source_paths'] = []; plan['inputs'] = {}
    plan['total_segments'] = 20
    plan['limits']['initial_free_bytes'] = 0
    plan['limits']['minimum_free_bytes'] = 0
    rawdir = tmp_path/'raw'; rawdir.mkdir()
    for row in plan['observations']:
        config = next(p for t in plan['trials'] if t['id'] == row['point'] for p in t['profiles'] if p['method'] == row['method'])
        path = rawdir/row['raw_path']; path.parent.mkdir(exist_ok=True)
        coeff = np.zeros((2, 7, 3) if row['method'] == 'DOP853' else (2, 3, 3))
        np.savez(path, times=np.linspace(0., 2.5*config['period'], 3),
            states=np.ones((3, 3)), dense_old=np.ones((2, 3)), dense_coefficients=coeff,
            historical_extrema_times=np.array([]), historical_extrema_states=np.empty((0, 3)))
    marker = tmp_path/'marker.json'; fake_source = 'a'*40; ref = 'refs/heads/synthetic'
    monkeypatch.setattr(run, 'RAW', rawdir); monkeypatch.setattr(run, 'MARKER', marker)
    monkeypatch.setattr(run, 'load', lambda: deepcopy(plan))
    monkeypatch.setattr(run, 'startup', lambda p: dict(passed=True, target_data_opened=False, synthetic_authority_only=True))
    monkeypatch.setattr(run, 'authenticate_raw', lambda p: {})
    def git(args, **kwargs):
        return fake_source+'\n' if args[1] == 'rev-parse' else fake_source+'\t'+ref+'\n'
    monkeypatch.setattr(run.subprocess, 'check_output', git)
    output = tmp_path/'out'
    run.execute(output, fake_source, ref)
    result = auditor.audit(output)
    assert result['passed'] and result['segments'] == 20
    assert not result['all_profiles_qualified'] and not result['all_nearest_consistent']
    assert not result['symbolic_chains_verified']
    assert len(list(output.iterdir())) == 12
    before = marker.read_bytes()
    with pytest.raises(ValueError, match='one-shot'): run.execute(tmp_path/'retry', fake_source, ref)
    assert marker.read_bytes() == before and not (tmp_path/'retry').exists()
    bad = json.loads((output/'summary.json').read_bytes()); bad['all_profiles_qualified'] = True
    (output/'summary.json').write_text(json.dumps(bad))
    with pytest.raises(ValueError, match='qualifications'): auditor.audit(output)
