"""Tamper controls for the public comparison replay; no raw artifacts needed."""
import json
import pytest
from butterfly._paired_startup import sha256
from scripts import verify_exp510_public_transport as verify

PATH = verify.run.ROOT/'docs/experiments/receipts/EXP-510-four-substep-fold-transport-result.json'


def test_public_transport_replay():
    saved = json.loads(PATH.read_bytes())
    result = verify.verify(PATH,sha256(PATH))
    assert result['passed']
    assert result['transport_completed'] == saved['result']['transport_completed']
    assert not result['full_raw_audit_repeated']
    assert not result['symbolic_chains_verified']


@pytest.mark.parametrize('kind',['source','chain','raw-pass','resource','count','missing-stage',
    'missing-fold','qualified','parameters','decision','endpoint','ledger'])
def test_tamper_rejected_with_changed_outer_hash(tmp_path,kind):
    row = json.loads(PATH.read_bytes())
    if kind == 'source':
        row['source_commit'] = '0'*40
    elif kind == 'chain':
        row['symbolic_chains_verified'] = True
    elif kind == 'raw-pass':
        row['passed'] = False
    elif kind == 'resource':
        row['output_bytes_including_summary'] = row['output_limit_bytes']+1
    elif kind == 'count':
        row['counts'][0]['target_ivps'] += 1
    elif kind == 'missing-stage':
        row['result']['rows'].pop()
    elif kind == 'missing-fold':
        row['result']['rows'][0]['folds'].pop()
    elif kind == 'qualified':
        f = row['result']['rows'][0]['folds'][0]
        f['qualified_in_region'] = not f['qualified_in_region']
    elif kind == 'parameters':
        row['result']['rows'][0]['spec']['parameters']['c'] += .001
    elif kind == 'decision':
        d = row['result']['rows'][0]['decision']
        d['transport_qualified'] = not d['transport_qualified']
    elif kind == 'endpoint':
        row['endpoint_comparison'] = {'invented':True}
    elif kind == 'ledger':
        row['ledger'] = []
    path = tmp_path/'tampered.json'
    path.write_text(json.dumps(row))
    with pytest.raises(ValueError):
        verify.verify(path,sha256(path))
