"""Authentic direct parents, sealed consumer, plan and one-shot controls."""
from copy import deepcopy
import json
import pytest
from scripts import run_exp522_nonlinear_refinement as run


def test_authentic_sealed_consumer_and_two_distinct_references():
    p = run.load(); source = run.inputs(); receipt = run.startup(p)
    assert receipt['passed'] and receipt['validation']['new_integrations'] == 0
    assert p['maximum_corrections'] == 1 and len(p['source_paths']) == 193
    assert source['anchor']['c'] != source['progress_anchor']['c']
    assert source['anchor'] != source['a_derivative_center']
    assert p['proposal']['spec']['parameters']['c'] == source['anchor']['c']
    assert p['limits']['initial_free_bytes'] >= p['limits']['output_bytes']+p['limits']['minimum_free_bytes']


@pytest.mark.parametrize('key', ['maximum_corrections', 'progress_anchor', 'maximum_residual_ratio', 'proposal', 'source_paths'])
def test_plan_cannot_drift(tmp_path, monkeypatch, key):
    p = deepcopy(run.load()); p.pop(key)
    path = tmp_path/'plan.json'; path.write_text(json.dumps(p)); monkeypatch.setattr(run, 'PLAN', path)
    with pytest.raises(ValueError, match='plan differs'): run.load()


def test_changed_parent_bytes_rejected(tmp_path, monkeypatch):
    for name in run.INPUTS:
        path = tmp_path/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes((run.ROOT/name).read_bytes())
    path = tmp_path/run.R521; path.write_bytes(path.read_bytes()+b'\n')
    monkeypatch.setattr(run, 'ROOT', tmp_path)
    with pytest.raises(ValueError, match='bytes differ'): run.inputs()


def test_consumed_attempt_rejected_before_new_output(tmp_path, monkeypatch):
    marker = tmp_path/'target-once.json'; marker.write_text('{}')
    monkeypatch.setattr(run, 'MARKER', marker)
    monkeypatch.setattr(run, 'validate', lambda: {})
    monkeypatch.setattr(run, 'startup', lambda p: {})
    def git(args, **kwargs):
        if args[1] == 'status': return ''
        if args[1] == 'ls-remote': return 'a'*40+' refs/heads/synthetic'
        return 'a'*40
    monkeypatch.setattr(run.subprocess, 'check_output', git)
    with pytest.raises(ValueError, match='unconsumed'): run.execute(tmp_path/'run', 'a'*40, 'refs/heads/synthetic')
    assert not (tmp_path/'run').exists()


def test_runtime_load_does_not_reexecute_parent_authorization(monkeypatch):
    def forbidden(): raise AssertionError('recursive authorization attempted')
    monkeypatch.setattr(run.parent, 'load', forbidden)
    monkeypatch.setattr(run.prior, 'load', forbidden)
    assert run.inputs()['anchor'] == run.load()['anchor']


def test_real_writer_census_auditor_and_one_shot_with_synthetic_geometry(tmp_path, monkeypatch):
    import numpy as np
    from scripts import audit_exp522_nonlinear_refinement as audit
    p = deepcopy(run.load()); p['source_paths'] = []; p['ancillary_inputs'] = {}
    p['limits'].update(initial_free_bytes=0, minimum_free_bytes=0)
    root = tmp_path/'EXP-522'; root.mkdir(); marker = root/'target-once.json'
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
    def summary(spec, rows, cycle, p, source):
        return dict(spec=spec, qualified=False, vectors=None, cycle=cycle, rows=[], fold_identity={}, contact=None)
    def measure(spec, output, p, source, budget, save):
        stage = output/spec['id']; stage.mkdir()
        candidates = run.prior.model.candidates(source['rows'], spec, run.prior.prior.transport.offset(spec['parameters']))
        save(spec['id']+'/inputs.json', dict(spec=spec, candidates=candidates)); configs = []
        for method in p['solvers']:
            budget(True)
            raw = dict(times=np.array([0., 1., 2.5]), states=np.ones((3, 3)), dense_old=np.ones((2, 3)),
                dense_coefficients=np.zeros((2, 7, 3) if method == 'DOP853' else (2, 3, 3)),
                historical_extrema_times=np.array([]), historical_extrema_states=np.empty((0, 3)))
            np.savez(stage/(spec['id']+'--'+method+'--observation.npz'), **raw)
            configs.append(dict(method=method, correction=dict(period_time=1.)))
        cycle = dict(profiles=configs); point = summary(spec, [], cycle, p, source)
        save(spec['id']+'/cycle.json', cycle); save(spec['id']+'/point.json', point)
        return point
    monkeypatch.setattr(run.prior, 'measure', measure); monkeypatch.setattr(run.prior, 'summarize', summary)
    monkeypatch.setattr(audit.folds, 'check_rows', lambda *args: ([], set(), 0))
    monkeypatch.setattr(audit.folds.raw.old, 'check_cycle', lambda stage, cycle, spec, seed, p:
        ({spec['id']+'--'+m+'--observation.npz' for m in ('DOP853', 'Radau')}, 2))
    monkeypatch.setattr(audit.folds.transport_audit, 'scalar_decision', lambda *args: None)
    output = root/'run'; run.execute(output, 'a'*40, 'refs/heads/synthetic')
    receipt = audit.audit(output, run.sha256(output/'summary.json'))
    assert receipt['passed'] and receipt['target_ivps'] == 2 and receipt['segments'] == 4
    assert receipt['result']['correction'] is not None and not receipt['result']['decision']['qualified']
    assert receipt['parent_predictor_qualified'] is False and not receipt['symbolic_chains_verified']
    with pytest.raises(ValueError, match='unconsumed'): run.execute(root/'second', 'a'*40, 'refs/heads/synthetic')
    assert not (root/'second').exists()
