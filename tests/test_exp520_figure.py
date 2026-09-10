"""All plotted values remain bound to the complete audited census."""
from copy import deepcopy
import json

import numpy as np
import pytest
from scripts import render_exp520_census as figure


def test_complete_census_and_parameter_values_rederive():
    rows = figure.data(figure.ROOT/figure.SOURCE)
    assert len(rows) == 5
    for row in rows:
        assert len(row['contexts']) == 4 and all(len(c['gaps']) == 16 for c in row['contexts'])
        assert row['nearest_gaps'] == [c['gaps'][row['nearest_index']] for c in row['contexts']]
        assert row['mean_gap'] == np.mean(row['nearest_gaps'])
        assert row['minimum_gap'] == min(row['nearest_gaps'])
        assert row['maximum_gap'] == max(row['nearest_gaps'])
        assert row['maximum_gap'] < 0


@pytest.mark.parametrize('mutation', ['hash', 'count', 'source', 'point', 'solver', 'window', 'root', 'unresolved', 'nomination', 'gap', 'claim'])
def test_rehashed_missing_or_substituted_census_cannot_be_plotted(tmp_path, monkeypatch, mutation):
    packet = json.loads((figure.ROOT/figure.SOURCE).read_bytes())
    p = packet['points'][0]
    if mutation == 'count': packet['segments'] -= 1
    elif mutation == 'source': packet['source_commit'] = '0'*40
    elif mutation == 'point': packet['points'].reverse()
    elif mutation == 'solver': p['profiles'].pop()
    elif mutation == 'window': p['profiles'][0]['windows'].reverse()
    elif mutation == 'root': p['profiles'][0]['windows'][0]['events'].pop()
    elif mutation == 'unresolved': p['profiles'][0]['unresolved'].append([0, 1])
    elif mutation == 'nomination': p['comparison']['consistent_nearest'] = False
    elif mutation == 'gap': p['comparison']['nearest'][0]['signed_gap'] += .1
    elif mutation == 'claim': packet['symbolic_chains_verified'] = True
    path = tmp_path/'changed.json'; path.write_text(json.dumps(packet))
    if mutation != 'hash': monkeypatch.setattr(figure, 'SHA', figure.sha(path))
    with pytest.raises(ValueError): figure.data(path)


def test_empirical_figure_replay_is_byte_identical(tmp_path):
    first, second = tmp_path/'first', tmp_path/'second'
    a, b = figure.render(first), figure.render(second)
    assert a == b and a['plotted_data'] == figure.data(figure.ROOT/figure.SOURCE)
    assert a['provenance']['generator_sha256'] == figure.sha(figure.__file__)
    assert len(list(first.iterdir())) == 5
    for path in first.iterdir(): assert path.read_bytes() == (second/path.name).read_bytes()
    with pytest.raises(ValueError, match='fresh'): figure.render(first)


def test_published_outputs_and_update_numbers_are_receipt_bound():
    folder = figure.ROOT/'docs/figures'; stem = figure.STEM
    path = folder/(stem+'.receipt.json'); receipt = json.loads(path.read_bytes())
    assert receipt['data_source']['sha256'] == figure.SHA
    assert receipt['provenance']['source_commit'] == figure.FREEZE
    assert receipt['provenance']['generator_sha256'] == figure.sha(figure.__file__)
    assert receipt['plotted_data'] == figure.data(figure.ROOT/figure.SOURCE)
    assert set(receipt['provenance']['outputs']) == {stem+'.'+s for s in ('svg', 'pdf', 'png')}
    for name, expected in receipt['provenance']['outputs'].items():
        assert figure.sha(folder/name) == expected['sha256']
        assert (folder/name).stat().st_size == expected['bytes']
    assert json.loads((folder/(stem+'.index.json')).read_bytes()) == dict(figure_id=stem, receipts={path.name: figure.sha(path)})
    text = (figure.ROOT/'docs/updates/2026-09-10-exp520-periodic-stationarity-census.md').read_text()
    source = json.loads((figure.ROOT/figure.SOURCE).read_bytes())
    assert f"{source['segments']:,}" in text
    for row in receipt['plotted_data']:
        assert f"{row['a']}" in text and f"{row['mean_gap']:.6f}" in text
    nearest = source['points'][-1]['comparison']['nearest']
    for key, places in (('z_separation', 4), ('speed', 3), ('acceleration', 4)):
        assert f'{np.mean([e[key] for e in nearest]):.{places}f}' in text
