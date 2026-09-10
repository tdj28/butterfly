"""Public receipt tamper controls; no local raw archive is required."""
from copy import deepcopy
import json
import pytest
from butterfly._paired_startup import sha256
from scripts import verify_exp509_public_replay as verify

PATH = verify.run.ROOT/'docs/experiments/receipts/EXP-509-failed-predictor-replay-result.json'


def test_public_replay():
    result = verify.verify(PATH,sha256(PATH))
    assert result['passed'] and result['reconstructed_status'] == 'predictor-unqualified'
    assert not result['original_run_completed']
    assert not result['full_raw_audit_repeated']
    assert not result['symbolic_chains_verified']


@pytest.mark.parametrize('kind',['completion','chain','source','raw-pass','new-ivp','failure',
    'point-identity','missing-fold','missing-boundary','accepted','corrector','count','ledger','marker'])
def test_tampering_rejected_even_with_new_outer_hash(tmp_path,kind):
    row = json.loads(PATH.read_bytes())
    if kind == 'completion':
        row['original_run_completed'] = True
    elif kind == 'chain':
        row['symbolic_chains_verified'] = True
    elif kind == 'source':
        row['binding']['source_commit'] = '0'*40
    elif kind == 'raw-pass':
        row['raw_replay_passed'] = False
    elif kind == 'new-ivp':
        row['new_integrations'] = 1
    elif kind == 'failure':
        row['original_failure']['message'] = 'hidden failure'
    elif kind == 'point-identity':
        row['original_point_sha256'] = '0'*64
    elif kind == 'missing-fold':
        row['reconstructed_result']['entries'][0]['point']['folds'].pop()
    elif kind == 'missing-boundary':
        row['reconstructed_result']['entries'][0]['point']['boundaries'].pop()
    elif kind == 'accepted':
        row['reconstructed_result']['analysis']['accepted'] = True
    elif kind == 'corrector':
        row['reconstructed_result']['entries'].append(deepcopy(row['reconstructed_result']['entries'][0]))
    elif kind == 'count':
        row['counts'][0]['target_ivps'] += 1
    elif kind == 'ledger':
        row['original_ledger'] = []
    elif kind == 'marker':
        row['replay_marker_sha256'] = '0'*64
    path = tmp_path/'tampered.json'
    path.write_text(json.dumps(row))
    with pytest.raises(ValueError):
        verify.verify(path,sha256(path))
