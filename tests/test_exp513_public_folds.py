"""Real public replay and mutations of the current all-five result packet."""
from copy import deepcopy
import json
import pytest
from scripts import verify_exp513_public_folds as public

RECEIPT=public.run.ROOT/'docs/experiments/receipts/EXP-513-candidate-fold-qualification-result.json'
SHA='64e60c557edf02ce0fabe17305e6049a6a043e3088812039e1dd07a9c2452741'


def test_real_public_fold_replay():
    r=public.verify(RECEIPT,SHA)
    assert r['passed'] and r['candidates']==5 and r['searched']==5
    assert r['qualified']==0 and r['reference_restored']==0
    assert not r['full_raw_audit_repeated'] and r['new_integrations']==0
    assert not r['symbolic_chains_verified']


@pytest.fixture(scope='module')
def authenticated_plan():
    # Unit mutations touch only the current packet; the test above uses real I/O.
    return public.run.load()


@pytest.mark.parametrize('mutation',['hash','source','claim','count','quota','candidate','midpoint-method',
    'midpoint-slope','seed','fold-method','qualification','restoration','earlier-accepted-event','trace-seed','box','absence'])
def test_current_packet_tampering(tmp_path,monkeypatch,authenticated_plan,mutation):
    monkeypatch.setattr(public.run,'load',lambda:deepcopy(authenticated_plan))
    saved=json.loads(RECEIPT.read_bytes())
    row=saved['rows'][0]
    if mutation=='source': saved['source_commit']='wrong'
    elif mutation=='claim': saved['symbolic_chains_verified']=True
    elif mutation=='count': saved['target_ivps']-=1
    elif mutation=='quota': saved['output_bytes_including_summary']=saved['output_limit_bytes']+1
    elif mutation=='candidate': saved['rows'].pop()
    elif mutation=='midpoint-method': row['midpoints'].reverse()
    elif mutation=='midpoint-slope': row['midpoints'][0]['measurement']['observation']['x_graph_slope']+=1
    elif mutation=='seed': row['seeded_candidate']['seed_time']+=.1
    elif mutation=='fold-method': row['folds'].reverse()
    elif mutation=='qualification': row['folds'][0]['qualification']['qualified']=True
    elif mutation=='restoration': row['assessment']['reference_restored']=True
    elif mutation=='earlier-accepted-event':
        next(v for v in row['midpoints'][0]['report']['reconstructed'] if v['accepted'])['time']+=.01
    elif mutation=='trace-seed': row['folds'][0]['shooting']['trace'][0]['u']+=.001
    elif mutation=='box': row['folds'][0]['shooting']['trace'][-1]['newton_step']=[0.,0.]
    elif mutation=='absence': row['assessment']['global_root_absence_proved']=True
    path=tmp_path/'changed.json'
    path.write_text(json.dumps(saved))
    with pytest.raises(ValueError):
        public.verify(path,SHA if mutation=='hash' else public.sha256(path))
