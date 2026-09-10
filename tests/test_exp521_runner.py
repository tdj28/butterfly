"""Authentic input, isolated consumer and prospective configuration checks."""
from copy import deepcopy
import json
import pytest
from scripts import run_exp521_critical_response as run
from scripts import audit_exp521_critical_response as audit


def test_authentic_sealed_startup_and_inputs():
    plan = run.load(); source = run.inputs()
    assert len(plan['specifications']) == 4 and plan['maximum_corrections'] == 1
    assert source['anchor']['a'] != source['a_center']
    assert len(source['historical_matches']) == 5
    # Validate in the actual sealed consumer, not pytest's process containing
    # unrelated modules imported during collection of the entire test suite.
    receipt = run.startup(plan)
    assert receipt['validation']['new_integrations'] == 0 and receipt['passed']


def test_target_loader_does_not_recursively_rerun_ancestral_authorization(monkeypatch):
    def forbidden(): raise AssertionError('historical recursive authorization called')
    monkeypatch.setattr(run.prior, 'load', forbidden)
    monkeypatch.setattr(run.prior, 'inputs', forbidden)
    assert run.inputs()['anchor'] == run.load()['anchor']


def test_parent_authentication_rejects_rewritten_receipt(tmp_path, monkeypatch):
    for name in run.INPUTS:
        dest = tmp_path/name; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes((run.ROOT/name).read_bytes())
    path = tmp_path/run.R520; value = json.loads(path.read_bytes()); value['passed'] = False; path.write_text(json.dumps(value))
    monkeypatch.setattr(run, 'ROOT', tmp_path)
    with pytest.raises(ValueError, match='bytes differ'): run.inputs()


@pytest.mark.parametrize('key', ['maximum_corrections', 'census', 'normalized_increments', 'inputs', 'source_paths'])
def test_frozen_plan_cannot_silently_drift(tmp_path, monkeypatch, key):
    p = deepcopy(run.load())
    if key == 'maximum_corrections': p[key] = 2
    elif key == 'census': p[key]['objects'] = [5]
    elif key == 'normalized_increments': p[key]['c'] = .1
    elif key == 'inputs': p[key].pop(run.R520)
    else: p[key].pop()
    path = tmp_path/'plan.json'; path.write_text(json.dumps(p)); monkeypatch.setattr(run, 'PLAN', path)
    with pytest.raises(ValueError, match='plan differs'): run.load()


def test_no_missing_source_or_ancillary_paths():
    p = run.load()
    assert set(run.EXPLICIT) <= set(p['source_paths'])
    for name in set(p['source_paths']) | set(p['inputs']) | set(p['ancillary_inputs']):
        assert (run.ROOT/name).is_file()
    assert p['limits']['initial_free_bytes'] >= p['limits']['output_bytes']+p['limits']['minimum_free_bytes']


def test_consumed_namespace_fails_before_target(tmp_path, monkeypatch):
    p = run.load(); marker = tmp_path/'target-once.json'; marker.write_text('{}')
    monkeypatch.setattr(run, 'MARKER', marker)
    monkeypatch.setattr(run, 'validate', lambda: {})
    monkeypatch.setattr(run, 'startup', lambda p: {})
    def git(args, **kwargs):
        if args[1] == 'status': return ''
        if args[1] == 'ls-remote': return 'a'*40+' refs/heads/synthetic'
        return 'a'*40
    monkeypatch.setattr(run.subprocess, 'check_output', git)
    with pytest.raises(ValueError, match='unconsumed'):
        run.execute(tmp_path/'new', 'a'*40, 'refs/heads/synthetic')
    assert not (tmp_path/'new').exists()


def test_synthetic_real_writer_polynomial_auditor_and_one_shot(tmp_path, monkeypatch):
    """Synthetic fold authority only; real files, census, marker and full ledger."""
    import numpy as np
    p = deepcopy(run.load()); p['source_paths'] = []; p['ancillary_inputs'] = {}
    p['limits'].update(initial_free_bytes=0, minimum_free_bytes=0)
    source = run.inputs(); root = tmp_path/'EXP-521'; root.mkdir(); marker = root/'target-once.json'
    monkeypatch.setattr(run, 'MARKER', marker); monkeypatch.setattr(run, 'load', lambda: deepcopy(p))
    validation = dict(valid=True, synthetic_fold_authority=True)
    monkeypatch.setattr(run, 'validate', lambda: validation)
    handshake = dict(passed=True, isolated=True, target_data_opened=False,
        sources={n: run.sha256(run.ROOT/n) for n in run.INPUTS}, validation=validation)
    monkeypatch.setattr(run, 'startup', lambda p: handshake)
    def git(args, **kwargs):
        if args[1] == 'status': return ''
        if args[1] == 'ls-remote': return 'a'*40+' refs/heads/synthetic'
        return 'a'*40
    monkeypatch.setattr(run.subprocess, 'check_output', git)
    def summary(spec, rows, cycle, p, s):
        return dict(spec=spec, qualified=False, vectors=None, cycle=cycle, rows=[], fold_identity={}, contact=None)
    def measure(spec, output, p, s, budget, save):
        stage = output/spec['id']; stage.mkdir()
        candidates = run.prior.model.candidates(s['rows'], spec, run.prior.prior.transport.offset(spec['parameters']))
        save(spec['id']+'/inputs.json', dict(spec=spec, candidates=candidates))
        configs = []
        for method in p['solvers']:
            budget(True)
            raw = dict(times=np.array([0., 1., 2.5]), states=np.ones((3, 3)), dense_old=np.ones((2, 3)),
                dense_coefficients=np.zeros((2, 7, 3) if method == 'DOP853' else (2, 3, 3)),
                historical_extrema_times=np.array([]), historical_extrema_states=np.empty((0, 3)))
            np.savez(stage/(spec['id']+'--'+method+'--observation.npz'), **raw)
            configs.append(dict(method=method, correction=dict(period_time=1.)))
        cycle = dict(profiles=configs); point = summary(spec, [], cycle, p, s)
        save(spec['id']+'/cycle.json', cycle); save(spec['id']+'/point.json', point)
        return point
    monkeypatch.setattr(run.prior, 'measure', measure)
    monkeypatch.setattr(run.prior, 'summarize', summary)
    monkeypatch.setattr(audit.folds, 'check_rows', lambda *args: ([], set(), 0))
    monkeypatch.setattr(audit.folds.raw.old, 'check_cycle', lambda stage, cycle, spec, seed, p:
        ({spec['id']+'--'+m+'--observation.npz' for m in ('DOP853', 'Radau')}, 2))
    monkeypatch.setattr(audit.folds.transport_audit, 'scalar_decision', lambda *args: None)
    output = root/'run'; run.execute(output, 'a'*40, 'refs/heads/synthetic')
    receipt = audit.audit(output, run.sha256(output/'summary.json'))
    assert receipt['passed'] and receipt['target_ivps'] == 8 and receipt['segments'] == 16
    assert receipt['result']['correction'] is None and not receipt['result']['response']['qualified']
    assert not receipt['symbolic_chains_verified']
    with pytest.raises(ValueError, match='unconsumed'):
        run.execute(root/'second', 'a'*40, 'refs/heads/synthetic')
    assert not (root/'second').exists()
