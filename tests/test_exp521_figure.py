"""Plot-schema guards and deterministic synthetic output, not target results."""
from copy import deepcopy
import json
import pytest
from scripts import render_exp521_response as plot
from tests.test_exp521_critical_response import fixture
from scripts import exp521_critical_response as model


def synthetic():
    source, measure = fixture()
    parents = [json.loads((plot.ROOT/name).read_bytes()) for name in plot.PARENTS]
    receipt = dict(experiment_id='EXP-521', source_commit=plot.FREEZE, passed=True,
        symbolic_chains_verified=False, D_identified=False, exact_critical_locus_proved=False,
        result=model.follow(source, measure))
    return receipt, parents


def test_complete_plot_table_with_all_robustness_variants():
    source, parents = synthetic(); rows = plot.table(source, *parents)
    assert len(rows) == 6
    assert all(len(r['full_state_distances']) == 16 for r in rows)
    assert all([len(v) for v in r['gaps']] == [4, 4] for r in rows)
    assert rows[-1]['normalized_a'] != 0


@pytest.mark.parametrize('kind', ['missing', 'reordered', 'duplicate', 'wrong-c', 'wrong-step', 'wrong-source', 'false-claim', 'nonfinite'])
def test_semantic_mutation_cannot_make_a_plausible_plot(kind):
    source, parents = synthetic()
    if kind == 'missing': source['result']['points'].pop()
    elif kind == 'reordered': source['result']['points'].reverse()
    elif kind == 'duplicate': source['result']['points'][1] = deepcopy(source['result']['points'][0])
    elif kind == 'wrong-c': source['result']['points'][0]['spec']['parameters']['c'] += .01
    elif kind == 'wrong-step': source['result']['correction']['spec']['parameters']['a'] += .01
    elif kind == 'wrong-source': source['source_commit'] = 'a'*40
    elif kind == 'false-claim': source['symbolic_chains_verified'] = True
    else: source['result']['points'][0]['gaps'][0]['residual'] = float('nan')
    with pytest.raises(ValueError): plot.table(source, *parents)


def test_unqualified_point_is_retained_as_missing_not_zero():
    source, parents = synthetic()
    source['result'].update(correction=None, proposal=None)
    source['result']['points'][0].update(qualified=False, vectors=None, gaps=None)
    rows = plot.table(source, *parents)
    assert len(rows) == 5 and rows[1]['gaps'] == [] and rows[1]['distance_range'] is None


def test_synthetic_figures_and_receipt_reproduce_byte_identically(tmp_path, monkeypatch):
    source, parents = synthetic(); rows = plot.table(source, *parents)
    monkeypatch.setattr(plot, 'load', lambda digest: (source, rows))
    first, second = tmp_path/'one', tmp_path/'two'
    a = plot.render(first, 'a'*64); b = plot.render(second, 'a'*64)
    assert a == b
    assert len(list(first.iterdir())) == 5
    for path in first.iterdir(): assert path.read_bytes() == (second/path.name).read_bytes()
    for name, metadata in a['provenance']['outputs'].items():
        assert plot.sha(first/name) == metadata['sha256']
    assert a['plotted_data'] == rows and 'not confidence' in a['interval_semantics']


def test_unqualified_retained_geometry_and_both_correction_ranges_are_visible(tmp_path, monkeypatch):
    source, parents = synthetic(); source['result']['points'][0]['qualified'] = False
    rows = plot.table(source, *parents)
    monkeypatch.setattr(plot, 'load', lambda digest: (source, rows))
    calls = []; original = plot.plt.Axes.errorbar
    def observed(self, *args, **kwargs):
        calls.append(kwargs.copy()); return original(self, *args, **kwargs)
    monkeypatch.setattr(plot.plt.Axes, 'errorbar', observed)
    receipt = plot.render(tmp_path/'visible-failure', 'a'*64)
    assert receipt['unqualified_points'] == ['c-coarse--1']
    assert receipt['unavailable_geometry'] == []
    assert sum(c.get('markerfacecolor') == 'white' for c in calls) == 2
    corrected = [c for c in calls if c['fmt'] in ('*', 'P')]
    assert len(corrected) == 2 and {c['fmt'] for c in corrected} == {'*', 'P'}
    assert all('yerr' in c and len(c['yerr']) == 2 for c in corrected)
