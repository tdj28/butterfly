"""Byte-preservation checks do not treat timeout evidence as a scientific pass."""
from pathlib import Path
import json
import pytest
from scripts import inspect_exp523_failure as check


def fixture(tmp_path):
    (tmp_path/'nested').mkdir(); (tmp_path/'nested/raw.npz').write_bytes(b'retained bytes')
    (tmp_path/'failure.json').write_text('{}')
    p=tmp_path/'nested/raw.npz'
    return {'nested/raw.npz':dict(bytes=p.stat().st_size,sha256=check.digest(p))}


def test_complete_inventory(tmp_path):
    ledger=fixture(tmp_path)
    assert check.verify_inventory(tmp_path,ledger,omit=('failure.json',))==dict(files=1,bytes=14)


@pytest.mark.parametrize('mutation',['missing','extra','bytes','hash','link','directory-link'])
def test_inventory_tampering_rejected(tmp_path,mutation):
    ledger=fixture(tmp_path); p=tmp_path/'nested/raw.npz'
    if mutation=='missing': p.unlink()
    elif mutation=='extra': (tmp_path/'extra').write_text('unrecorded')
    elif mutation=='bytes': p.write_bytes(b'changed')
    elif mutation=='hash': p.write_bytes(b'replaced bytes')
    elif mutation=='link': p.unlink(); p.symlink_to(tmp_path/'failure.json')
    else: (tmp_path/'alias').symlink_to(tmp_path/'nested',target_is_directory=True)
    with pytest.raises(ValueError): check.verify_inventory(tmp_path,ledger,omit=('failure.json',))


@pytest.mark.parametrize('name',['../outside','/absolute','nested/../failure.json','nested//raw.npz',''])
def test_noncanonical_or_escaping_paths_rejected(tmp_path,name):
    fixture(tmp_path)
    with pytest.raises(ValueError): check.safe_file(tmp_path,name)


def test_source_symlink_rejected(tmp_path):
    fixture(tmp_path); (tmp_path/'alias').symlink_to(tmp_path/'nested',target_is_directory=True)
    with pytest.raises(ValueError): check.safe_file(tmp_path,'alias/raw.npz')


def test_inspector_has_no_numerical_imports_or_target_entrypoint():
    import ast
    tree=ast.parse(Path(check.__file__).read_text())
    imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
    imports += [a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names]
    assert set(imports)=={'argparse','datetime','hashlib','json','pathlib','subprocess'}


def test_public_receipt_preserves_failure_and_scope():
    path=Path(__file__).resolve().parents[1]/'docs/experiments/receipts/EXP-523-timeout-preservation.json'
    assert check.digest(path)=='0c440f75221792c55b5c83b0dcc2c7175dbd9a9057bbc32fb380ed4c3783a19a'
    receipt=json.loads(path.read_bytes())
    assert receipt['diagnostic_sha256']==check.EXPECTED
    assert receipt['inspector_sha256']==check.digest(Path(check.__file__))
    assert receipt['status']=='timeout-bytes-preserved-not-scientifically-audited'
    assert receipt['new_integrations']==0
    assert all(receipt[k] is False for k in ('complete_raw_audit','complete_run_summary','symbolic_chains_verified'))
    assert receipt['retained_inventory']==dict(files=1299,bytes=3241861585)
    assert receipt['total_run_bytes']==receipt['retained_inventory']['bytes']+receipt['failure_receipt_bytes']
    assert receipt['target_ivp_calls_started']==875 and receipt['periodic_census_segments']==667500
    completed=[dict(id=f'step-0-{axis}-{i}',status='completed') for axis in ('a','c') for i in range(4)]
    assert receipt['point_progress']==completed+[dict(id='step-0-predictor',status='started')]
    assert 21600<=receipt['elapsed_seconds']<21601
