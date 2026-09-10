import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from butterfly._paired_startup import sha256, write_json
from scripts import verify_exp515_public_precision as public
from scripts import render_exp515_precision_comparison as figure

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT/'docs/experiments/receipts/EXP-515-third-return-precision-result.json'
SHA = 'b924000f8abac6c68bd600b63a842cd36d1ed9b4e2d96c0e7938b8425aa963e5'


def test_public_replay_and_all_plot_cells():
    result = public.verify(RECEIPT, SHA)
    assert result['resolved_return_comparisons'] == 18
    assert result['failed_historical_comparisons'] == 8
    assert result['distinct_failed_historical_vectors'] == 4
    assert not result['full_raw_audit_repeated']
    data = figure.plot_data(json.loads(RECEIPT.read_bytes()), public.run.load())
    assert len(data) == 6
    assert sum(len(c['norms']) for r in data for c in r['curves']) == 72


@pytest.mark.parametrize('kind', ['source', 'input', 'count', 'claim', 'case', 'profile',
    'field', 'correction', 'norm', 'uncertainty', 'decision', 'control', 'event'])
def test_semantic_tamper_with_rehashed_receipt(tmp_path, kind):
    saved = json.loads(RECEIPT.read_bytes())
    m = saved['rows'][1]['profiles'][0]['measures'][2]
    if kind == 'source': saved['source_commit'] = '0'*40
    elif kind == 'input': saved['inputs'][public.run.RECEIPT] = '0'*64
    elif kind == 'count': saved['target_ivps'] = 10
    elif kind == 'claim': saved['symbolic_chains_verified'] = True
    elif kind == 'case': saved['rows'].pop()
    elif kind == 'profile': saved['rows'][0]['profiles'].pop()
    elif kind == 'field': m['field'][0] = '1'
    elif kind == 'correction': m['corrected'][0] = '0'
    elif kind == 'norm': m['scaled_norm'] = '1e-14'
    elif kind == 'uncertainty': m['box_relative_radius'] = '0'
    elif kind == 'decision': saved['rows'][1]['comparison']['historical'][0]['comparisons'][2]['comparison']['within_one_percent'] = True
    elif kind == 'control': saved['controls'].pop()
    elif kind == 'event': m['time'] = '16'
    path = tmp_path/'changed.json'
    write_json(path, saved)
    with pytest.raises(ValueError):
        public.verify(path, sha256(path))


def test_isolated_public_consumer_without_raw(tmp_path):
    names = set(public.run.SOURCES) | set(public.run.INPUTS) | {
        'scripts/verify_exp515_public_precision.py', RECEIPT.relative_to(ROOT).as_posix()}
    for name in names:
        target = tmp_path/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/name, target)
    assert not (tmp_path/'artifacts').exists()
    code = (f'import sys;from pathlib import Path;root=Path({str(tmp_path)!r});'
        f'sys.path[:0]={[str(tmp_path),str(tmp_path/"python")]!r};'
        'from scripts.verify_exp515_public_precision import verify;'
        f'r=verify(root/{RECEIPT.relative_to(ROOT).as_posix()!r},{SHA!r});'
        'assert r["resolved_return_comparisons"]==18;'
        'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
        'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    subprocess.run([sys.executable, '-I', '-B', '-c', code], cwd=tmp_path,
                   capture_output=True, text=True, check=True, timeout=60)
    assert not list(tmp_path.rglob('*.pyc'))
    assert all(sha256(tmp_path/n) == sha256(ROOT/n) for n in names)


def test_plot_refuses_missing_or_zero_observation():
    saved = json.loads(RECEIPT.read_bytes())
    saved['rows'][0]['profiles'][0]['measures'][0]['scaled_norm'] = '0'
    with pytest.raises(ValueError, match='nonpositive'):
        figure.plot_data(saved, public.run.load())
