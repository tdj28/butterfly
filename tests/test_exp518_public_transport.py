"""Complete compact transport replay and self-consistent tampering tests."""
from copy import deepcopy
import json
import shutil
import subprocess
import sys

import pytest
from scripts import verify_exp518_public_transport as public

NAME = 'docs/experiments/receipts/EXP-518-recovered-fold-transport-result.json'
RECEIPT = public.run.ROOT / NAME
SHA = 'f8a0b33cd13ff88d924928bc5f59a811468ae5a627ca007a0541702d194c8e01'


@pytest.fixture(scope='module')
def authenticated():
    return public.run.load(), public.run.inputs()


def test_real_transport_receipt():
    result = public.verify(RECEIPT, SHA)
    assert result['passed'] and result['executed_substeps'] == 2
    assert result['target_ivps'] == 200 and result['transport_completed']
    assert result['endpoint_fold_proximity'] is False
    assert not result['full_raw_audit_repeated'] and result['new_integrations'] == 0
    assert not result['symbolic_chains_verified']


@pytest.mark.parametrize('mutation', ['hash', 'source', 'plan', 'claim', 'count', 'quota', 'controls',
    'missing-stage', 'extra-stage', 'stage-parameters', 'candidate', 'midpoint-method', 'midpoint-slope',
    'seed', 'fold-method', 'qualification', 'earlier-event', 'trace-seed', 'residual', 'jacobian',
    'step', 'angle', 'curvature', 'nan', 'infinity', 'spread', 'displacement', 'transport', 'progress',
    'old-eighth', 'historical-reference', 'endpoint'])
def test_rehashed_semantic_tampering(tmp_path, monkeypatch, authenticated, mutation):
    p, start = authenticated
    monkeypatch.setattr(public.run, 'load', lambda: deepcopy(p))
    monkeypatch.setattr(public.run, 'inputs', lambda: deepcopy(start))
    saved = json.loads(RECEIPT.read_bytes())
    item = saved['result']['rows'][0]
    row = next(r for r in item['rows'] if r['folds'] is not None)
    trace = row['folds'][0]['shooting']['trace']
    if mutation == 'source': saved['source_commit'] = 'wrong'
    elif mutation == 'plan': saved['plan_sha256'] = '0'*64
    elif mutation == 'claim': saved['symbolic_chains_verified'] = True
    elif mutation == 'count': saved['target_ivps'] -= 1
    elif mutation == 'quota': saved['output_bytes_including_summary'] = saved['output_limit_bytes']+1
    elif mutation == 'controls': saved['controls'] = {}
    elif mutation == 'missing-stage': saved['result']['rows'].pop(0)
    elif mutation == 'extra-stage': saved['result']['rows'].append(deepcopy(item))
    elif mutation == 'stage-parameters': item['spec']['parameters']['a'] += .001
    elif mutation == 'candidate': item['rows'].pop()
    elif mutation == 'midpoint-method': row['midpoints'].reverse()
    elif mutation == 'midpoint-slope': row['midpoints'][0]['measurement']['observation']['x_graph_slope'] += 1
    elif mutation == 'seed': row['seeded_candidate']['seed_time'] += .1
    elif mutation == 'fold-method': row['folds'].reverse()
    elif mutation == 'qualification': row['folds'][0]['qualification']['qualified'] = not row['folds'][0]['qualification']['qualified']
    elif mutation == 'earlier-event': next(v for v in row['midpoints'][0]['report']['reconstructed'] if v['accepted'])['time'] += .01
    elif mutation == 'trace-seed': trace[0]['u'] += .001
    elif mutation == 'residual': trace[0]['residual'][0] += .1
    elif mutation == 'jacobian': trace[0]['jacobian'][0][0] += 1
    elif mutation == 'step': trace[0]['newton_step'][0] += .001
    elif mutation == 'angle': trace[-1]['angle'] += .01
    elif mutation == 'curvature': trace[-1]['event_second_derivative'] += 1
    elif mutation == 'nan': trace[0]['angle'] = float('nan')
    elif mutation == 'infinity': trace[0]['determinant_scale'] = float('inf')
    elif mutation == 'spread': item['decision']['cross_history_spread'] = 1
    elif mutation == 'displacement': item['decision']['adjacent_displacement'] = 1
    elif mutation == 'transport': saved['result']['transport_completed'] = not saved['result']['transport_completed']
    elif mutation == 'progress': saved['result']['progress'][0]['status'] = 'not-run'
    elif mutation == 'old-eighth': saved['result']['original_eighth_return_restored'] = True
    elif mutation == 'historical-reference': row['assessment']['historical_fixed_parameter_reference']['restored'] = not row['assessment']['historical_fixed_parameter_reference']['restored']
    elif mutation == 'endpoint': saved['endpoint_comparison'] = {'fold_proximity': True}
    path = tmp_path/'changed.json'
    path.write_text(json.dumps(saved))
    with pytest.raises(ValueError):
        public.verify(path, SHA if mutation == 'hash' else public.sha256(path))


def test_isolated_consumer_without_raw_data(tmp_path, authenticated):
    p, _ = authenticated
    names = set(p['source_paths']) | set(public.run.INPUTS) | {NAME, 'scripts/verify_exp518_public_transport.py'}
    for name in names:
        destination = tmp_path/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(public.run.ROOT/name, destination)
    code = (f'import sys;from pathlib import Path;root=Path({str(tmp_path)!r});'
        f'sys.path[:0]={[str(tmp_path), str(tmp_path/"python")]!r};'
        'from scripts import verify_exp518_public_transport as p;'
        f'assert p.verify(root/{NAME!r}, {SHA!r})["passed"];'
        'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
        'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    subprocess.run([sys.executable, '-I', '-B', '-c', code], cwd=tmp_path, capture_output=True, text=True, check=True, timeout=240)
    assert not (tmp_path/'artifacts').exists()
    assert not list(tmp_path.rglob('*.pyc'))
    assert all(public.sha256(tmp_path/n) == public.sha256(public.run.ROOT/n) for n in names)
