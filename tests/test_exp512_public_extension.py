"""Real public integration check, then unit tampering of the current packet."""
from copy import deepcopy
import json
import pytest
from scripts import verify_exp512_public_extension as public

RECEIPT = public.run.ROOT/'docs/experiments/receipts/EXP-512-censored-return-extension-result.json'
SHA = 'c89bb30f90bf26a4f4902e349459b234201a66b00d3d2b4a500d6849fdb96e76'


def test_real_public_extension_replay():
    result = public.verify(RECEIPT,SHA)
    assert result['passed'] and result['all_prefixes_preserved'] and result['all_ninth_returns_observed']
    assert [r['regular_samples'] for r in result['analyses']]==[19,19]
    assert [r['matched_candidate_brackets'] for r in result['analyses']]==[[[1,2],[15,16],[16,17]],[[17,18],[18,19]]]
    assert not result['full_raw_audit_repeated'] and result['new_integrations']==0
    assert not result['symbolic_chains_verified']


@pytest.fixture(scope='module')
def authenticated_inputs():
    # Only the current packet is mutated below. Authenticate the immutable
    # historical inputs once; the integration test above exercises real I/O.
    return public.run.load(),public.run.inputs(),public.run.prior.load()


@pytest.mark.parametrize('mutation',[
    'byte-identity','source','claim','count','quota','selection','solver','prefix',
    'measurement','horizon','angle','reuse','ninth','analysis','absence','controls'])
def test_current_packet_tampering(tmp_path,monkeypatch,authenticated_inputs,mutation):
    plan,old,prior_plan = authenticated_inputs
    monkeypatch.setattr(public.run,'load',lambda:deepcopy(plan))
    monkeypatch.setattr(public.run,'inputs',lambda:deepcopy(old))
    monkeypatch.setattr(public.run.prior,'load',lambda:deepcopy(prior_plan))
    saved = json.loads(RECEIPT.read_bytes())
    profile = saved['extensions'][0]['profiles'][0]
    if mutation=='source':
        saved['source_commit']='wrong'
    elif mutation=='claim':
        saved['symbolic_chains_verified']=True
    elif mutation=='count':
        saved['target_ivps']-=1
    elif mutation=='quota':
        saved['output_bytes_including_summary']=saved['output_limit_bytes']+1
    elif mutation=='selection':
        saved['extensions'].pop()
    elif mutation=='solver':
        saved['extensions'][0]['profiles'].reverse()
    elif mutation=='prefix':
        saved['extensions'][0]['prefixes'][0]['passed']=False
    elif mutation=='measurement':
        profile['measurement']['observation']['x_graph_slope']+=1
    elif mutation=='horizon':
        profile['report']['horizon']-=1
    elif mutation=='angle':
        profile['report']['reconstructed'][0]['angle']*=.5
    elif mutation=='reuse':
        saved['result']['rows'][0]['samples'][0]['pair']['regular']=False
    elif mutation=='ninth':
        saved['result']['all_ninth_returns_observed']=False
    elif mutation=='analysis':
        saved['result']['rows'][0]['analysis']['regular_samples']+=1
    elif mutation=='absence':
        saved['result']['rows'][0]['analysis']['global_root_absence_proved']=True
    elif mutation=='controls':
        saved['controls']['passed']=False
    path = tmp_path/'changed.json'
    path.write_text(json.dumps(saved))
    with pytest.raises(ValueError):
        public.verify(path,SHA if mutation=='byte-identity' else public.sha256(path))
