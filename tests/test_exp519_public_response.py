"""Whole-receipt authentication, semantic mutations and isolated public replay."""
from copy import deepcopy
import json
import shutil
import subprocess
import sys

import pytest
from scripts import verify_exp519_public_response as public

NAME = 'docs/experiments/receipts/EXP-519-fixed-c-fold-response-result.json'
SHA = '92ff9159ca3de7794a481e9d682d02626b945495f3ad87e6c7d095137f0117ec'
RECEIPT = public.run.ROOT/NAME


@pytest.fixture(scope='module')
def authenticated():
    return public.run.load(), public.run.inputs()


def test_real_complete_response_receipt():
    result = public.verify(RECEIPT, SHA)
    saved = json.loads(RECEIPT.read_bytes())
    assert result['passed'] and result['target_ivps'] == saved['target_ivps']
    assert result['points'] == 4+int(saved['result']['correction'] is not None)
    assert result['decision'] == saved['result']['decision']
    assert not result['symbolic_chains_verified'] and not result['full_raw_audit_repeated']
    assert result['new_integrations'] == 0


@pytest.mark.parametrize('mutation', [
    'hash', 'source', 'plan', 'input', 'claim', 'paid', 'count', 'quota', 'controls',
    'missing-point', 'duplicate-point', 'reorder-point', 'parameter', 'missing-fold',
    'midpoint-method', 'midpoint-slope', 'seed', 'fold-method', 'trace', 'qualification',
    'cycle-method', 'cycle-count', 'primitive', 'correspondence', 'point-qualified',
    'vector', 'vector-order', 'response-slope', 'response-error', 'response-qualified',
    'proposal-step', 'proposal-prediction', 'correction-parameter', 'decision-distance',
    'decision-prediction', 'decision-contact', 'exact-claim', 'nan'])
def test_rehashed_semantic_changes_are_rejected(tmp_path, monkeypatch, authenticated, mutation):
    plan, source = authenticated
    monkeypatch.setattr(public.run, 'load', lambda: deepcopy(plan))
    monkeypatch.setattr(public.run, 'inputs', lambda: deepcopy(source))
    saved = json.loads(RECEIPT.read_bytes()); result = saved['result']
    point = result['points'][0]; row = point['rows'][0]
    if mutation == 'source': saved['source_commit'] = 'substitute'
    elif mutation == 'plan': saved['plan_sha256'] = '0'*64
    elif mutation == 'input': saved['inputs'] = {}
    elif mutation == 'claim': saved['symbolic_chains_verified'] = True
    elif mutation == 'paid': saved['paid_review'] = 'fabricated-review'
    elif mutation == 'count': saved['target_ivps'] -= 1
    elif mutation == 'quota': saved['output_bytes_including_summary'] = saved['output_limit_bytes']+1
    elif mutation == 'controls': saved['controls'] = {}
    elif mutation == 'missing-point': result['points'].pop()
    elif mutation == 'duplicate-point': result['points'].append(deepcopy(point))
    elif mutation == 'reorder-point': result['points'].reverse()
    elif mutation == 'parameter': point['spec']['parameters']['a'] += .001
    elif mutation == 'missing-fold': point['rows'].pop()
    elif mutation == 'midpoint-method': row['midpoints'].reverse()
    elif mutation == 'midpoint-slope': row['midpoints'][0]['measurement']['observation']['x_graph_slope'] += 1
    elif mutation == 'seed': row['seeded_candidate']['seed_time'] += .1
    elif mutation == 'fold-method': row['folds'].reverse()
    elif mutation == 'trace': row['folds'][0]['shooting']['trace'][0]['u'] += .01
    elif mutation == 'qualification': row['assessment']['qualified'] = not row['assessment']['qualified']
    elif mutation == 'cycle-method': point['cycle']['profiles'].reverse()
    elif mutation == 'cycle-count': point['cycle']['profiles'][0]['metric']['windows'][0]['counts']['historical'] += 1
    elif mutation == 'primitive': point['cycle']['profiles'][0]['metric']['windows'][0]['conditional_minimal_period'] = False
    elif mutation == 'correspondence': point['anchor_correspondence']['passed'] = False
    elif mutation == 'point-qualified': point['qualified'] = not point['qualified']
    elif mutation == 'vector': point['vectors'][0]['residual'][2] += .001
    elif mutation == 'vector-order': point['vectors'].reverse()
    elif mutation == 'response-slope': result['response']['variants'][0]['fine'][0] += .001
    elif mutation == 'response-error': result['response']['variants'][0]['full_relative_error'] += .1
    elif mutation == 'response-qualified': result['response']['qualified'] = not result['response']['qualified']
    elif mutation == 'proposal-step': result['proposal']['realized_normalized_step'] += .1
    elif mutation == 'proposal-prediction': result['proposal']['predicted_vectors'][0]['residual'][2] += .001
    elif mutation == 'correction-parameter': result['correction']['spec']['parameters']['a'] += .001
    elif mutation == 'decision-distance': result['decision']['variants'][0]['full_state_distance'] += .1
    elif mutation == 'decision-prediction': result['decision']['variants'][0]['prediction_error'] += .1
    elif mutation == 'decision-contact': result['decision']['full_state_contact'] = not result['decision']['full_state_contact']
    elif mutation == 'exact-claim': result['exact_contact_verified'] = True
    elif mutation == 'nan': point['vectors'][0]['residual'][0] = float('nan')
    changed = tmp_path/'changed.json'; changed.write_text(json.dumps(saved))
    with pytest.raises(ValueError):
        public.verify(changed, SHA if mutation == 'hash' else public.sha256(changed))


def test_isolated_public_consumer_without_raw_data(tmp_path, authenticated):
    plan, _ = authenticated
    names = set(plan['source_paths']) | set(public.run.INPUTS) | {NAME, 'scripts/verify_exp519_public_response.py'}
    for name in names:
        destination = tmp_path/name; destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(public.run.ROOT/name, destination)
    code = (f'import sys;from pathlib import Path;root=Path({str(tmp_path)!r});'
        f'sys.path[:0]={[str(tmp_path), str(tmp_path/"python")]!r};'
        'from scripts import verify_exp519_public_response as p;'
        f'assert p.verify(root/{NAME!r}, {SHA!r})["passed"];'
        'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
        'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    # This post-run portability check has its own bounded software-test timeout;
    # it does not change the frozen target startup's 240-second limit.
    subprocess.run([sys.executable, '-I', '-B', '-c', code], cwd=tmp_path,
                   capture_output=True, text=True, check=True, timeout=600)
    assert not (tmp_path/'artifacts').exists() and not list(tmp_path.rglob('*.pyc'))
    assert all(public.sha256(tmp_path/n) == public.sha256(public.run.ROOT/n) for n in names)
