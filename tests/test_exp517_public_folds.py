"""Complete compact replay, semantic mutations, and a source-only consumer."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
from scripts import verify_exp517_public_folds as public

NAME='docs/experiments/receipts/EXP-517-earlier-return-folds-result.json'
RECEIPT=public.run.ROOT/NAME
SHA='0c1233986f4ac6463d8ded47ce0a92353a98a86a889089a3f2bafe78742adf76'


def test_real_complete_public_fold_replay():
    r=public.verify(RECEIPT,SHA)
    assert r['passed'] and r['candidates']==r['searched']==4
    assert r['qualified']==r['reference_restored']==4
    assert r['cross_representation']['original_eighth_return_restored'] is False
    assert not r['full_raw_audit_repeated'] and r['new_integrations']==0
    assert not r['symbolic_chains_verified']


@pytest.fixture(scope='module')
def authenticated_plan():
    return public.run.load()


@pytest.mark.parametrize('mutation',['hash','source','plan','claim','count','quota','candidate',
    'controls','midpoint-method','midpoint-slope','seed','fold-method','qualification','restoration',
    'earlier-accepted-event','trace-seed','residual','jacobian','step','angle','curvature',
    'reference-distance','cross-state','old-eighth','nan-trace-angle','overflow-number'])
def test_semantic_tampering_even_with_rehashed_packet(tmp_path,monkeypatch,authenticated_plan,mutation):
    monkeypatch.setattr(public.run,'load',lambda:deepcopy(authenticated_plan))
    saved=json.loads(RECEIPT.read_bytes())
    row=saved['rows'][0]
    trace=row['folds'][0]['shooting']['trace']
    if mutation=='source': saved['source_commit']='wrong'
    elif mutation=='plan': saved['plan_sha256']='0'*64
    elif mutation=='claim': saved['symbolic_chains_verified']=True
    elif mutation=='count': saved['target_ivps']-=1
    elif mutation=='quota': saved['output_bytes_including_summary']=saved['output_limit_bytes']+1
    elif mutation=='candidate': saved['rows'].pop()
    elif mutation=='controls': saved['controls']={}
    elif mutation=='midpoint-method': row['midpoints'].reverse()
    elif mutation=='midpoint-slope': row['midpoints'][0]['measurement']['observation']['x_graph_slope']+=1
    elif mutation=='seed': row['seeded_candidate']['seed_time']+=.1
    elif mutation=='fold-method': row['folds'].reverse()
    elif mutation=='qualification': row['folds'][0]['qualification']['qualified']=False
    elif mutation=='restoration': row['assessment']['reference_restored']=False
    elif mutation=='earlier-accepted-event':
        next(v for v in row['midpoints'][0]['report']['reconstructed'] if v['accepted'])['time']+=.01
    elif mutation=='trace-seed': trace[0]['u']+=.001
    elif mutation=='residual': trace[0]['residual'][0]+=.1
    elif mutation=='jacobian': trace[0]['jacobian'][0][0]+=1
    elif mutation=='step': trace[0]['newton_step'][0]+=.001
    elif mutation=='angle': trace[-1]['angle']+=.01
    elif mutation=='curvature': trace[-1]['event_second_derivative']+=1
    elif mutation=='reference-distance': row['assessment']['reference_distances'][0]['image_state']=.01
    elif mutation=='cross-state': saved['cross_representation']['full_state_spread']=1.
    elif mutation=='old-eighth': saved['cross_representation']['original_eighth_return_restored']=True
    elif mutation=='nan-trace-angle': trace[0]['angle']=float('nan')
    elif mutation=='overflow-number': trace[0]['determinant_scale']=float('inf')
    path=tmp_path/'changed.json'
    path.write_text(json.dumps(saved))
    with pytest.raises(ValueError):
        public.verify(path,SHA if mutation=='hash' else public.sha256(path))


def test_isolated_public_consumer_without_raw_artifacts(tmp_path,authenticated_plan):
    names=set(authenticated_plan['source_paths'])|set(public.run.INPUTS)|{NAME,'scripts/verify_exp517_public_folds.py'}
    for name in names:
        dest=tmp_path/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(public.run.ROOT/name,dest)
    code=(f'import sys;from pathlib import Path;root=Path({str(tmp_path)!r});'
          f'sys.path[:0]={[str(tmp_path),str(tmp_path/"python")]!r};'
          'import json;from scripts import verify_exp517_public_folds as p;'
          f'print(json.dumps(p.verify(root/{NAME!r},{SHA!r})));'
          'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
          'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    child=subprocess.run([sys.executable,'-I','-B','-c',code],cwd=tmp_path,
                         capture_output=True,text=True,check=True,timeout=180)
    assert json.loads(child.stdout)['reference_restored']==4
    assert not (tmp_path/'artifacts').exists()
    assert not list(tmp_path.rglob('*.pyc'))
    assert all(public.sha256(tmp_path/n)==public.sha256(public.run.ROOT/n) for n in names)
