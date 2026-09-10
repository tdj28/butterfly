"""Public-figure identity and explicit failed-parent controls; no integrations."""
from copy import deepcopy
import json
import pytest
from scripts import render_exp522_refinement as figure


def inputs():
    return json.loads((figure.ROOT/figure.SOURCE).read_bytes()), figure.run.inputs()


def test_complete_variants_both_references_and_failed_trial():
    r, source = inputs(); rows = figure.table(r, source)
    assert len(rows) == 3
    assert rows[1]['outcome'] == 'rejected predictor' and rows[2]['outcome'] == 'accepted refinement'
    assert all(len(v['full_state_distances']) == 16 and len(v['raw_signed_gaps']) == 8 for v in rows)
    assert rows[1]['parameters']['c'] == rows[2]['parameters']['c']
    assert rows[2]['net_gap_improvement_percent'][0] < rows[1]['net_gap_improvement_percent'][0]
    assert all(x < 0 for row in rows for x in row['raw_signed_gaps'])


@pytest.mark.parametrize('kind', ['source','claim','reference','spec','vector','gap'])
def test_semantic_tampering_rejected(kind):
    receipt, source = inputs(); r = deepcopy(receipt)
    if kind == 'source': r['source_commit'] = 'a'*40
    elif kind == 'claim': r['parent_predictor_qualified'] = True
    elif kind == 'reference': r['progress_anchor'] = source['anchor']
    elif kind == 'spec': r['result']['correction']['spec']['parameters']['c'] += .01
    elif kind == 'vector': r['result']['correction']['vectors'].pop()
    else: r['result']['correction']['gaps'][0]['residual'] = float('nan')
    with pytest.raises(ValueError): figure.table(r, source)


def test_actual_redraw_deterministic_and_hash_bound(tmp_path):
    first = figure.render(tmp_path/'first'); second = figure.render(tmp_path/'second')
    assert first == second
    assert first['minimum_contact_improvement_factor'] > 115
    for name, record in first['outputs'].items():
        assert figure.sha256(tmp_path/'first'/name) == record['sha256']
    with pytest.raises(ValueError, match='fresh'): figure.render(tmp_path/'first')
