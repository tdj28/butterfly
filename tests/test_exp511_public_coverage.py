"""Public compact replay and claim/matrix tampering; no raw artifacts needed."""
from copy import deepcopy
import json
import pytest
from scripts import verify_exp511_public_coverage as public

RECEIPT = public.run.ROOT/'docs/experiments/receipts/EXP-511-direct-curve-coverage-result.json'
SHA = '245610c6116eed25f76bc775cc77be6cce66eacd4193d466a069c23b1892eb85'


def test_public_replay():
    result = public.verify(RECEIPT,SHA)
    assert result['passed']
    assert [r['regular_samples'] for r in result['analyses']]==[14,17]
    assert all(r['matched_candidate_brackets']==[] for r in result['analyses'])
    assert result['full_raw_audit_repeated'] is False
    assert result['new_integrations']==0
    assert result['symbolic_chains_verified'] is False


@pytest.mark.parametrize('mutation',[
    'byte-identity','source','claim','count','quota','curve','node','method',
    'measurement','pair','analysis','absence','config','event-angle','partition','controls'])
def test_public_tampering_rejected(tmp_path,mutation):
    saved = json.loads(RECEIPT.read_bytes())
    profile = saved['rows'][0]['samples'][0]['profiles'][0]
    if mutation=='source':
        saved['source_commit']='wrong'
    elif mutation=='claim':
        saved['symbolic_chains_verified']=True
    elif mutation=='count':
        saved['target_ivps']-=1
    elif mutation=='quota':
        saved['output_bytes_including_summary']=saved['output_limit_bytes']+1
    elif mutation=='curve':
        saved['rows'].pop()
    elif mutation=='node':
        saved['rows'][0]['samples'].pop()
    elif mutation=='method':
        saved['rows'][0]['samples'][0]['profiles'].reverse()
    elif mutation=='measurement':
        profile['measurement']['observation']['x_graph_slope']+=1
    elif mutation=='pair':
        saved['rows'][0]['samples'][0]['pair']['regular']=False
    elif mutation=='analysis':
        saved['rows'][0]['analysis']['regular_samples']+=1
    elif mutation=='absence':
        saved['rows'][0]['analysis']['global_root_absence_proved']=True
    elif mutation=='config':
        profile['report']['rtol']*=10
    elif mutation=='event-angle':
        profile['report']['reconstructed'][0]['angle']*=.5
    elif mutation=='partition':
        profile['report']['knots'].pop()
    elif mutation=='controls':
        saved['controls']['rows'][0]['verdict']['errors'][0]=1.
    path = tmp_path/'changed.json'
    path.write_text(json.dumps(saved))
    with pytest.raises(ValueError):
        public.verify(path,SHA if mutation=='byte-identity' else public.sha256(path))


def test_symbolic_flags_cannot_be_promoted(tmp_path):
    saved = deepcopy(json.loads(RECEIPT.read_bytes()))
    saved['rows'][0]['analysis']['exact_flow_root_isolation']=True
    path = tmp_path/'changed.json'
    path.write_text(json.dumps(saved))
    with pytest.raises(ValueError,match='curve analysis'):
        public.verify(path,public.sha256(path))
