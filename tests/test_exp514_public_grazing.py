"""Real public replay plus self-hashed mutations of the current result."""
from copy import deepcopy
import json
import pytest
from scripts import verify_exp514_public_grazing as public

RECEIPT = public.run.ROOT/'docs/experiments/receipts/EXP-514-candidate-grazing-boundaries-result.json'
SHA = '825b6298900cf644b5b1e6e6b433c1e42bf3e791af8f0d89d90fd2ebc977d4bc'


def test_real_public_grazing_replay():
    r = public.verify(RECEIPT, SHA)
    assert r['passed'] and r['candidates'] == 5
    assert r['qualified'] == 5
    assert not r['full_raw_audit_repeated'] and r['new_integrations'] == 0
    assert not r['symbolic_chains_verified']


@pytest.fixture(scope='module')
def authenticated_plan():
    return public.run.load()


@pytest.mark.parametrize('mutation', ['hash', 'source', 'claim', 'count', 'quota', 'candidate',
    'root-method', 'seed', 'residual', 'raw-label', 'side-input', 'missing-dose', 'side-method',
    'event-accepted', 'earlier-accepted-event', 'qualification', 'fold-claim', 'ratio'])
def test_grazing_packet_tampering(tmp_path, monkeypatch, authenticated_plan, mutation):
    monkeypatch.setattr(public.run, 'load', lambda:deepcopy(authenticated_plan))
    saved = json.loads(RECEIPT.read_bytes())
    row = saved['rows'][0]
    if mutation == 'source': saved['source_commit'] = 'wrong'
    elif mutation == 'claim': saved['symbolic_chains_verified'] = True
    elif mutation == 'count': saved['target_ivps'] -= 1
    elif mutation == 'quota': saved['output_bytes_including_summary'] = 2*1024**3+1
    elif mutation == 'candidate': saved['rows'].pop()
    elif mutation == 'root-method': row['roots'].reverse()
    elif mutation == 'seed': row['roots'][0]['shooting']['trace'][0]['u'] += .001
    elif mutation == 'residual': row['roots'][0]['shooting']['trace'][-1]['residual'][0] += .01
    elif mutation == 'raw-label': row['roots'][0]['shooting']['raw_files'].pop()
    elif mutation == 'side-input': row['sides'][0]['u'] += 1e-10
    elif mutation == 'missing-dose': row['sides'].pop()
    elif mutation == 'side-method': row['sides'][0]['profiles'].reverse()
    elif mutation == 'event-accepted': row['sides'][0]['profiles'][0]['report']['reconstructed'][0]['accepted'] ^= True
    elif mutation == 'earlier-accepted-event':
        next(e for e in row['sides'][0]['profiles'][0]['report']['reconstructed'] if e['accepted'])['time'] += .01
    elif mutation == 'qualification': row['decision']['qualified'] = not row['decision']['qualified']
    elif mutation == 'fold-claim': row['decision']['projected_fold_qualified'] = True
    elif mutation == 'ratio': row['decision']['analysis']['solvers'][0]['square_root_ratio'] += .01
    path = tmp_path/'changed.json'
    path.write_text(json.dumps(saved))
    with pytest.raises(ValueError):
        public.verify(path, SHA if mutation=='hash' else public.sha256(path))
