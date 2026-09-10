"""Synthetic figure reductions; no target data or integrations."""
from copy import deepcopy
import json
import numpy as np
import pytest
from scripts import render_exp519_response as figure
from tests.test_exp519_fold_response import ANCHOR, linear_measure, result


def packet():
    return dict(result=result()), dict(anchor=deepcopy(ANCHOR),
        anchor_vectors=linear_measure(dict(parameters=ANCHOR))['vectors'])


def test_complete_points_and_signed_full_state_reductions():
    saved, source = packet()
    before = deepcopy((saved, source))
    rows = figure.point_data(saved, source)
    assert (saved, source) == before
    assert [r['id'] for r in rows] == ['anchor', 'coarse--1', 'coarse-+1', 'fine--1', 'fine-+1', 'correction']
    for row in rows:
        v = np.asarray([r['residual'] for r in row['vectors']])
        assert len(row['signed_x']) == 16
        assert row['signed_x'] == v[:, 0].tolist()
        assert row['full_distance'] == np.max(np.abs(v), axis=1).tolist()
        assert row['component_maximum'] == np.max(np.abs(v), axis=0).tolist()
        assert row['x_distance'] == np.max(np.abs(v[:, [0, 3]]), axis=1).tolist()
    assert rows[0]['full_distance'][0] > figure.RADIUS
    assert rows[-1]['full_distance'][0] < figure.RADIUS


def test_missing_qualification_is_not_zero_imputed():
    saved, source = packet()
    saved['result']['points'][0].update(qualified=False, vectors=None)
    saved['result']['correction'] = None
    rows = figure.point_data(saved, source)
    assert len(rows) == 5
    assert not rows[1]['qualified']
    for key in ('signed_x', 'x_distance', 'full_distance', 'component_maximum'):
        assert rows[1][key] is None


@pytest.mark.parametrize('kind', ['b', 'c', 'missing-variant', 'duplicate-variant', 'nan', 'unqualified-values'])
def test_incomplete_or_substituted_figure_input_rejected(kind):
    saved, source = packet(); point = saved['result']['points'][0]
    if kind in ('b', 'c'): point['spec']['parameters'][kind] += .001
    elif kind == 'missing-variant': point['vectors'].pop()
    elif kind == 'duplicate-variant': point['vectors'][-1] = deepcopy(point['vectors'][0])
    elif kind == 'nan': point['vectors'][0]['residual'][2] = float('nan')
    else: point['qualified'] = False
    with pytest.raises(ValueError): figure.point_data(saved, source)


def test_response_bars_retain_all_variants_and_worst_error():
    saved, _ = packet()
    rows = saved['result']['response']['variants']
    for i, row in enumerate(rows):
        row['x_relative_error'], row['full_relative_error'] = i/100, (16-i)/100
    groups = figure.response_data(saved)
    assert len(groups) == 4 and sum(len(g['variants']) for g in groups) == 16
    for group in groups:
        assert len(group['variants']) == 4
        assert group['maximum_x_error'] == max(v['x_relative_error'] for v in group['variants'])
        assert group['maximum_full_error'] == max(v['full_relative_error'] for v in group['variants'])


def test_response_absence_and_incomplete_order():
    saved, _ = packet()
    saved['result']['response']['variants'].reverse()
    with pytest.raises(ValueError): figure.response_data(saved)
    saved['result']['response']['variants'] = []
    assert figure.response_data(saved) == []


def test_synthetic_render_is_byte_reproducible_and_data_bound(tmp_path, monkeypatch):
    """Mock only receipt authentication: this is not an empirical figure."""
    saved, source = packet(); saved['source_commit'] = 'synthetic-control-only'
    path = tmp_path/'synthetic.json'; path.write_text(json.dumps(saved))
    expected = figure.sha256(path)
    def authenticate(receipt, digest):
        assert receipt == path and digest == expected and figure.sha256(receipt) == digest
        return dict(synthetic_control_only=True)
    monkeypatch.setattr(figure.public, 'verify', authenticate)
    monkeypatch.setattr(figure.public.run, 'inputs', lambda: deepcopy(source))
    monkeypatch.setattr(figure.public.run, 'ROOT', tmp_path)
    first, second = tmp_path/'first', tmp_path/'second'
    a = figure.render(path, expected, first)
    b = figure.render(path, expected, second)
    assert a == b
    assert a['provenance']['audit'] == dict(synthetic_control_only=True)
    assert a['plotted_data']['points'] == figure.point_data(saved, source)
    assert len(list(first.iterdir())) == 5
    for f in first.iterdir():
        assert f.read_bytes() == (second/f.name).read_bytes()
    with pytest.raises(ValueError, match='fresh figure output'):
        figure.render(path, expected, first)


def test_published_figure_and_manuscript_numbers_rederive_from_receipts():
    root = figure.public.run.ROOT; folder = root/'docs/figures'; stem = figure.STEM
    path = folder/(stem+'.receipt.json'); meta = json.loads(path.read_bytes())
    source = meta['data_source']; provenance = meta['provenance']
    assert source['sha256'] == '92ff9159ca3de7794a481e9d682d02626b945495f3ad87e6c7d095137f0117ec'
    assert figure.sha256(root/source['path']) == source['sha256']
    assert source['anchor_receipt'] == figure.public.run.RECEIPT
    assert source['anchor_sha256'] == figure.public.run.INPUTS[source['anchor_receipt']]
    assert figure.sha256(root/source['anchor_receipt']) == source['anchor_sha256']
    saved = json.loads((root/source['path']).read_bytes())
    parent = json.loads((root/source['anchor_receipt']).read_bytes())
    contact = deepcopy(parent['endpoint_comparison']['contact'])
    for row, (h, d) in zip(contact['rows'], figure.public.run.model.folds.CASES, strict=True):
        row['family_id'] = f'exp519-history-{h}-direction-{d}'
    anchor = dict(anchor=parent['result']['rows'][-1]['spec']['parameters'],
                  anchor_vectors=figure.public.run.model.vectors(contact))
    assert meta['plotted_data']['points'] == figure.point_data(saved, anchor)
    assert meta['plotted_data']['response'] == figure.response_data(saved)
    assert provenance['source_commit'] == figure.public.SOURCE
    for role in ('generator', 'verifier'):
        assert figure.sha256(root/provenance[role]) == provenance[role+'_sha256']
    assert set(provenance['outputs']) == {stem+'.'+e for e in ('svg', 'pdf', 'png')}
    for name, expected in provenance['outputs'].items():
        assert figure.sha256(folder/name) == expected['sha256']
        assert (folder/name).stat().st_size == expected['bytes']
    assert json.loads((folder/(stem+'.index.json')).read_bytes()) == dict(
        figure_id=meta['figure_id'], receipts={path.name: figure.sha256(path)})
    assert (root/'paper/figures/fig39-exp519-fixed-c-fold-response.png').read_bytes() == (folder/(stem+'.png')).read_bytes()
    text = (root/'paper/sections/04-results.tex').read_text()
    r = saved['result']; variants = r['decision']['variants']
    assert f"All {saved['target_ivps']} integrations" in text
    assert f"{r['correction']['spec']['parameters']['a']:.7f}" in text
    assert f"{100*max(v['full_relative_error'] for v in r['response']['variants']):.3f}\\%" in text
    assert f"{100*max(v['prediction_error'] for v in variants):.2f}\\%" in text
    mantissa, exponent = format(max(v['full_state_distance'] for v in variants), '.2e').split('e')
    assert f'{mantissa}\\times10^{{{int(exponent)}}}' in text
