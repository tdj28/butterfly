"""Recovery scope, complete-stage accounting, solver denial and failure controls."""
import ast
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import pytest
from scripts import audit_exp524_partial_calibration as a
from scripts import deploy_exp524_prax as deploy


def files():
    item = dict(bytes=1, sha256='a'*64)
    result = {n: deepcopy(item) for n in ('binding.json', 'startup.json', 'controls.json')}
    result.update({n+'/raw.npz': deepcopy(item) for n in a.IDS+['step-0-predictor']})
    return result


def test_partition_accounts_for_every_file_without_promoting_partial():
    ledger = files(); groups = a.partition(ledger)
    assert list(groups) == a.IDS+['step-0-predictor']
    assert sum(map(len, groups.values()))+3 == len(ledger)


@pytest.mark.parametrize('mutation', ['extra-stage', 'extra-common', 'missing-common', 'missing-stage',
                                    'completed-predictor', 'completed-cycle'])
def test_partition_rejects_unplanned_or_incomplete_accounting(mutation):
    ledger = files()
    if mutation == 'extra-stage': ledger['step-1-a-0/raw.npz'] = {}
    elif mutation == 'extra-common': ledger['summary.json'] = {}
    elif mutation == 'missing-common': del ledger['binding.json']
    elif mutation == 'missing-stage': del ledger[a.IDS[0]+'/raw.npz']
    elif mutation == 'completed-predictor': ledger['step-0-predictor/critical-point.json'] = {}
    else: ledger['step-0-predictor/cycle.json'] = {}
    with pytest.raises(ValueError): a.partition(ledger)


def failure_fixture():
    ledger = files()
    for i in range(1299-len(ledger)):
        ledger['step-0-predictor/extra-'+str(i)] = dict(bytes=1, sha256='a'*64)
    ledger['binding.json']['bytes'] = 3241861585-1298
    failure = dict(error_type='BudgetStop', message='EXP-523 wall deadline',
        point_progress=deepcopy(a.PROGRESS), target_ivps=875, segments=667500,
        utc='2026-09-11T04:22:18.280192+00:00', files=ledger)
    binding = dict(started_utc='2026-09-10T22:22:18.238851+00:00', source_commit=a.preservation.COMMIT,
                   plan_sha256=a.preservation.EXPECTED['plan'], runtime={'synthetic': True})
    return failure, binding


def test_authenticated_failure_semantics_and_global_inventory():
    failure, binding = failure_fixture()
    assert len(a.check_failure(failure, binding)) == 9


@pytest.mark.parametrize('field', ['target_ivps', 'segments', 'progress', 'message', 'files', 'bytes', 'clock', 'commit'])
def test_self_consistent_but_false_historical_semantics_rejected(field):
    f, b = failure_fixture()
    if field in ('target_ivps', 'segments'): f[field] += 1
    elif field == 'progress': f['point_progress'][-1]['status'] = 'completed'
    elif field == 'message': f['message'] = 'other failure'
    elif field == 'files': f['files'].pop('step-0-predictor/extra-0')
    elif field == 'bytes': f['files']['binding.json']['bytes'] += 1
    elif field == 'clock': f['utc'] = '2026-09-11T05:22:18.280192+00:00'
    else: b['source_commit'] = 'a'*40
    with pytest.raises(ValueError): a.check_failure(f, b)


def test_forbid_direct_alias_and_low_level_integrations_and_restore():
    import scipy.integrate
    original = scipy.integrate.solve_ivp
    # This module alias is discovered by the production guard.
    global retained_solver_alias
    retained_solver_alias = original
    with a.forbid_integrations():
        for call in (scipy.integrate.solve_ivp, retained_solver_alias, scipy.integrate.Radau.step):
            with pytest.raises(RuntimeError, match='forbids new integrations'): call(None)
        assert scipy.integrate.solve_ivp is not original
    assert scipy.integrate.solve_ivp is original and retained_solver_alias is original
    del retained_solver_alias


def test_response_only_checks_all_eight_without_predictor(monkeypatch):
    from test_exp523_refreshed_path import fixture
    source, measure = fixture()
    points = [measure(s, source) for axis in ('a', 'c') for s in a.parent.model.stencil(source['anchor'], 0, axis)]
    def forbidden(*args): raise AssertionError('audit may not propose or collect new data')
    monkeypatch.setattr(a.parent.model, 'proposal', forbidden)
    with a.forbid_integrations():
        assert a.response_audit(source, points)['qualified']
        points[0]['qualified'] = False
        assert not a.response_audit(source, points)['qualified']


def test_response_scalar_mutation_rejected(monkeypatch):
    from test_exp523_refreshed_path import fixture
    source, measure = fixture()
    points = [measure(s, source) for axis in ('a', 'c') for s in a.parent.model.stencil(source['anchor'], 0, axis)]
    old = a.parent.model.response
    def broken(*args):
        value = old(*args); value['a']['variants'][0]['fine'][0] += .1; return value
    monkeypatch.setattr(a.parent.model, 'response', broken)
    with pytest.raises(ValueError, match='scalar a response'): a.response_audit(source, points)


def test_exact_plan_and_isolated_physical_closure():
    # Full-suite imports include unrelated experiments; qualify only the exact
    # production import graph in the isolated child, not pytest's global graph.
    assert a.read(a.ROOT/a.PLAN) == a.expected()
    p = a.read(a.ROOT/a.PLAN)
    hashes = {n:a.sha256(a.ROOT/n) for n in p['source_paths']}
    receipt = deploy.rehearsal(a.ROOT, hashes)
    assert receipt['passed'] and not receipt['validation']['raw_inputs_opened']


def test_wrong_runtime_rejected(monkeypatch):
    monkeypatch.setattr(a.sys, 'base_prefix', '/not-managed')
    with pytest.raises(ValueError, match='managed runtime'): a.runtime_check()


def test_consumed_marker_rejected_before_raw_access(tmp_path, monkeypatch):
    monkeypatch.setattr(a, 'ROOT', tmp_path)
    monkeypatch.setattr(a, 'preflight', lambda c: {})
    marker = tmp_path/'artifacts/EXP-524/audit-once.json'
    marker.parent.mkdir(parents=True); marker.write_text('{}')
    def forbidden(): raise AssertionError('old raw accessed')
    monkeypatch.setattr(a.preservation, 'inspect', forbidden)
    with pytest.raises(ValueError, match='fresh recovery'): a.execute('a'*40)
    assert not (marker.parent/'audit-01').exists()


def test_forced_timeout_retains_new_failure_without_claiming_preservation(tmp_path, monkeypatch):
    root = a.ROOT
    monkeypatch.setattr(a, 'ROOT', tmp_path)
    monkeypatch.setattr(a, 'MIN_FREE', 0)
    monkeypatch.setattr(a, 'preflight', lambda c: {})
    monkeypatch.setattr(a, 'protect_historical_tree', lambda: None)
    for n in (a.PLAN, a.CYCLE):
        dest = tmp_path/n; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes((root/n).read_bytes())
    trace = []
    def handler(sig, func): trace.append(('handler',func)); return None
    monkeypatch.setattr(a.signal, 'signal', handler)
    monkeypatch.setattr(a.signal, 'alarm', lambda n: trace.append(('alarm',n)))
    def timeout():
        assert ('alarm',43200) in trace
        raise TimeoutError('forced pre-replay timeout')
    monkeypatch.setattr(a.preservation, 'inspect', timeout)
    with pytest.raises(TimeoutError): a.execute('a'*40)
    out = tmp_path/'artifacts/EXP-524/audit-01'
    failure = a.read(out/'failure.json')
    assert failure['error_type'] == 'TimeoutError' and not failure['preservation_verified']
    assert (out.parent/'audit-once.json').is_file() and not (out/'audit.json').exists()


def test_historical_write_guard_in_child(tmp_path):
    target = tmp_path/'retained'; target.mkdir(); (target/'raw').write_text('original')
    code = ('import sys;from pathlib import Path;sys.path[:0]=[".","python"];'
        'from scripts import audit_exp524_partial_calibration as a;'
        f'a.preservation.TASK=Path({str(target)!r});a.protect_historical_tree();'
        f'Path({str(target / "raw")!r}).write_text("changed")')
    result = subprocess.run([sys.executable,'-I','-B','-c',code],cwd=a.ROOT,text=True,capture_output=True)
    assert result.returncode != 0 and 'historical tree is read-only' in result.stderr
    assert (target/'raw').read_text() == 'original'


def test_deployment_uses_new_source_and_existing_runtime_without_upload():
    for launch in (False,True):
        code = deploy.bootstrap_code('a'*40, {'scripts/example.py':'b'*64}, launch)
        ast.parse(code)
        assert 'exp524-partial-audit-' in code and 'exp523-refreshed-eae6745d124c/source/.venv/bin/python' in code
        assert '--filter=blob:none' in code and 'start_new_session=True' in code
        assert 'scp' not in code and 'rsync' not in code and 'uv sync' not in code
        assert 'a.preflight(' in code and 'a.execute(' in code
