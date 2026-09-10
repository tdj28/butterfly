"""Exact public receipt and semantic tampering, with raw-scope limits explicit."""
from copy import deepcopy
import json
from pathlib import Path

import pytest
from butterfly._paired_startup import sha256, write_json
from scripts import verify_exp507_public_restoration as public

RECEIPT = public.run.ROOT/'docs/experiments/receipts/EXP-507-fixed-c-fold-restoration-result.json'
SHA = 'b6d550882b761fb499a9b6e3f4d415aa05c0dc1d1f98f424bcffc2dacaba386d'


def test_public_receipt_complete_replay():
    out = public.verify(RECEIPT,SHA)
    assert out['passed'] and out['target_ivps'] == 158
    assert out['decision']['fold_restored']
    assert out['decision']['half_signed_fold_reduction']
    assert not out['decision']['joint_proximity']
    assert not out['symbolic_chains_verified']
    assert not out['full_raw_audit_repeated']
    assert len(out['decision']['variant_changes']) == 256


def test_wrong_hash_before_json_parse(tmp_path):
    path = tmp_path/'invalid.json'
    path.write_bytes(b'not json')
    with pytest.raises(ValueError,match='byte identity'):
        public.verify(path,'0'*64)


@pytest.mark.parametrize('kind',['source','plan','claim','quota','scope','decision','proposal','missing-boundary','cycle','count'])
def test_self_consistent_tampering_still_rejected(tmp_path,kind):
    saved = json.loads(RECEIPT.read_bytes())
    if kind == 'source':
        saved['source_commit'] = '0'*40
    elif kind == 'plan':
        saved['plan_sha256'] = '0'*64
    elif kind == 'claim':
        saved['symbolic_chains_verified'] = True
    elif kind == 'quota':
        saved['output_bytes_including_summary'] = saved['output_limit_bytes']+1
    elif kind == 'scope':
        saved['protocol_compliant'] = False
    elif kind == 'decision':
        saved['decision']['joint_proximity'] = True
    elif kind == 'proposal':
        saved['proposal']['spec']['parameters']['c'] += .001
        saved['point']['spec'] = deepcopy(saved['proposal']['spec'])
        saved['point']['cycle']['spec'] = deepcopy(saved['proposal']['spec'])
    elif kind == 'missing-boundary':
        saved['point']['boundaries'].pop()
    elif kind == 'cycle':
        saved['point']['cycle']['profiles'][0]['metric']['windows'][0]['counts']['historical'] = 3
    else:
        saved['target_ivps'] = saved['inherited_archive_products']-1
    point = tmp_path/'point.json'
    write_json(point,saved['point'])
    saved['point_sha256'] = sha256(point)
    path = tmp_path/'modified.json'
    write_json(path,saved)
    with pytest.raises(ValueError):
        public.verify(path,sha256(path))
