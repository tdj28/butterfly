"""Synthetic transport-figure controls; no new target integrations."""
from copy import deepcopy
import json

import pytest
from scripts import render_exp518_transport as figure


def fixture():
    rows = []
    for h, d in figure.public.run.model.CASES:
        profiles = [dict(method=m, qualification=dict(observations=[dict(image_state=[1., 0., .1], next_state=[2., 0., .2])]*3))
                    for m in figure.public.run.model.METHODS]
        rows.append(dict(candidate=dict(id=f'h{h}-d{d}', history=h, direction=d, parameters=dict(a=.2, b=.2, c=7.)),
                         assessment=dict(qualified=True), folds=profiles))
    next_rows = deepcopy(rows)
    for r in next_rows:
        r['candidate']['parameters']['c'] = 6.995
    decision = dict(qualified=True, transport_qualified=True, cross_history_spread=2e-12, adjacent_displacement=.001)
    return dict(result=dict(rows=[dict(spec=dict(id='substep-3', parameters=dict(a=.2, b=.2, c=6.995)), rows=next_rows, decision=decision)])), rows


def test_all_cases_both_solvers_and_separate_gate_denominators():
    saved, start = fixture()
    data = figure.plot_data(saved, start)
    assert len(data) == 2 and all(len(s['points']) == 4 for s in data)
    assert sum(len(p['values']) for s in data for p in s['points']) == 16
    assert data[1]['ratios'] == dict(spread=2e-6, displacement=.1)


@pytest.mark.parametrize('kind', ['case', 'method', 'sample', 'parameters', 'nan', 'negative-ratio', 'infinite-ratio'])
def test_incomplete_or_nonfinite_figure_rejected(kind):
    saved, start = fixture()
    stage = saved['result']['rows'][0]
    row = stage['rows'][0]
    if kind == 'case': stage['rows'].pop()
    elif kind == 'method': row['folds'].pop()
    elif kind == 'sample': row['folds'][0]['qualification']['observations'].pop()
    elif kind == 'parameters': stage['spec']['parameters']['c'] += 1
    elif kind == 'nan': row['folds'][0]['qualification']['observations'][1]['image_state'][0] = float('nan')
    elif kind == 'negative-ratio': stage['decision']['cross_history_spread'] = -1
    elif kind == 'infinite-ratio': stage['decision']['adjacent_displacement'] = float('inf')
    with pytest.raises(ValueError): figure.plot_data(saved, start)


def test_failure_remains_a_counted_case_without_fabricated_coordinates():
    saved, start = fixture()
    stage = saved['result']['rows'][0]
    stage['rows'][0].update(assessment=None, folds=None)
    stage['decision'].update(qualified=False, transport_qualified=False)
    data = figure.plot_data(saved, start)
    assert len(data[1]['points']) == 4
    assert data[1]['points'][0]['values'] == []
    assert data[1]['ratios'] is None


def endpoint_fixture():
    saved, _ = fixture()
    rows = []
    for item in saved['result']['rows'][-1]['rows']:
        c = item['candidate']; c['family_id'] = c['id']
        variants = [dict(method=m, phase=t, pair_x_distance=[.00009]*6, pair_state_distance=[.00014]*6)
                    for m, t in [('DOP853', .25), ('DOP853', 1.25), ('Radau', .25), ('Radau', 1.25)]]
        rows.append(dict(id=c['id'], family_id=c['family_id'], variants=variants))
    saved['endpoint_comparison'] = dict(contact=dict(rows=rows))
    return saved


def test_endpoint_shows_projection_pass_beside_state_failure():
    data = figure.endpoint_data(endpoint_fixture())
    assert len(data) == 16
    assert all(r['x_ratio'] < 1 < r['state_ratio'] for r in data)


@pytest.mark.parametrize('kind', ['case', 'variant', 'family', 'nan', 'negative'])
def test_endpoint_does_not_drop_or_mislabel_a_variant(kind):
    saved = endpoint_fixture()
    rows = saved['endpoint_comparison']['contact']['rows']
    if kind == 'case': rows.pop()
    elif kind == 'variant': rows[0]['variants'].pop()
    elif kind == 'family': rows[0]['family_id'] = 'wrong'
    elif kind == 'nan': rows[0]['variants'][0]['pair_state_distance'][3] = float('nan')
    elif kind == 'negative': rows[0]['variants'][0]['pair_x_distance'][3] = -1
    with pytest.raises(ValueError): figure.endpoint_data(saved)


def test_ineligible_endpoint_has_no_invented_distance():
    assert figure.endpoint_data(dict(endpoint_comparison=None)) == []


def test_published_figure_sources_values_outputs_and_paper_copy_are_bound():
    root = figure.public.run.ROOT
    stem = 'EXP-518-recovered-fold-transport'
    folder = root/'docs/figures'
    receipt = folder/(stem+'.receipt.json')
    meta = json.loads(receipt.read_bytes())
    source = meta['data_source']
    assert source['sha256'] == 'f8a0b33cd13ff88d924928bc5f59a811468ae5a627ca007a0541702d194c8e01'
    assert figure.sha256(root/source['artifact']) == source['sha256']
    assert source['anchor'] == figure.public.run.RECEIPT
    assert source['anchor_sha256'] == figure.public.run.INPUTS[source['anchor']]
    assert figure.sha256(root/source['anchor']) == source['anchor_sha256']
    saved = json.loads((root/source['artifact']).read_bytes())
    start = json.loads((root/source['anchor']).read_bytes())['rows']
    assert meta['plotted_data'] == figure.plot_data(saved, start)
    assert meta['endpoint_variants'] == figure.endpoint_data(saved)
    provenance = meta['provenance']
    assert provenance['source_commit'] == figure.public.SOURCE
    for role in ('generator', 'public_verifier'):
        assert figure.sha256(root/provenance[role]) == provenance[role+'_sha256']
    assert set(provenance['outputs']) == {stem+'.'+extension for extension in ('svg', 'pdf', 'png')}
    assert all(figure.sha256(folder/name) == digest for name, digest in provenance['outputs'].items())
    assert json.loads((folder/(stem+'.index.json')).read_bytes()) == dict(receipts={stem+'.receipt.json': figure.sha256(receipt)})
    assert (root/'paper/figures/fig38-exp518-recovered-fold-transport.png').read_bytes() == (folder/(stem+'.png')).read_bytes()
