"""Prospective figure controls use synthetic data, never unaudited target output."""
from copy import deepcopy
import json
import runpy
from pathlib import Path
import pytest
from scripts import render_exp523_path as figure


def fixture():
    controls = runpy.run_path(str(Path(__file__).with_name('test_exp523_refreshed_path.py')))
    source, measure = controls['fixture']()
    result = figure.run.model.follow(source, measure)
    receipt = dict(experiment_id='EXP-523', passed=True, source_commit=figure.COMMIT,
        inputs=figure.run.INPUTS, plan_sha256=figure.sha256(figure.run.PLAN), new_integrations=0,
        symbolic_chains_verified=False, D_identified=False, exact_critical_locus_proved=False,
        initial_anchor=source['anchor'], result=result)
    return receipt, source


def test_all_calibration_and_actual_variants_included():
    receipt, source = fixture(); rows = figure.table(receipt, source)
    assert len(rows) == 19 and sum(r['kind'] == 'calibration' for r in rows) == 16
    assert sum(r['accepted'] for r in rows) == 3
    assert all(len(r['full_state_distances']) == 16 and len(r['signed_gaps']) == 8 for r in rows)


@pytest.mark.parametrize('bad', ['source','audit','claim','manifest','input','anchor','decision','missing','extra','vector'])
def test_unaudited_or_changed_result_cannot_be_plotted(bad):
    receipt, source = fixture(); row = receipt['result']['steps'][0]
    if bad == 'source': receipt['source_commit'] = 'a'*40
    elif bad == 'audit': receipt['passed'] = False
    elif bad == 'claim': receipt['symbolic_chains_verified'] = True
    elif bad == 'manifest': receipt['plan_sha256'] = 'b'*64
    elif bad == 'input': receipt['inputs'] = {}
    elif bad == 'anchor': receipt['initial_anchor'] = dict(source['anchor'], c=7.)
    elif bad == 'decision': row['predictor_decision']['qualified'] = False
    elif bad == 'missing': row['a_points'].pop()
    elif bad == 'extra': row['c_points'].append(deepcopy(row['c_points'][0]))
    else: row['predictor']['vectors'][0]['residual'][1] = float('nan')
    with pytest.raises(ValueError): figure.table(receipt, source)


def test_draw_is_deterministic_and_labels_synthetic_data(tmp_path):
    receipt, source = fixture(); rows = figure.table(receipt, source)
    first = figure.draw(tmp_path/'one',rows,2,synthetic=True)
    second = figure.draw(tmp_path/'two',rows,2,synthetic=True)
    assert first == second
    assert 'SYNTHETIC CONTROL' in (tmp_path/'one'/(figure.STEM+'.svg')).read_text()
    for name, item in first.items(): assert figure.sha256(tmp_path/'one'/name) == item['sha256']
    with pytest.raises(ValueError,match='fresh'): figure.draw(tmp_path/'one',rows,2,synthetic=True)


def test_receipt_bytes_verified_before_any_drawing(tmp_path):
    path=tmp_path/'audit.json'; path.write_text('{}')
    with pytest.raises(ValueError,match='byte identity'): figure.render(path,'a'*64,tmp_path/'figure')
    assert not (tmp_path/'figure').exists()


def test_raw_audited_failure_still_displays_complete_attempted_stencil():
    receipt, source = fixture(); controls=runpy.run_path(str(Path(__file__).with_name('test_exp523_refreshed_path.py')))
    _, measure=controls['fixture']()
    def failed(spec,current):
        p=measure(spec,current)
        if spec['id']=='step-0-a-0': p['qualified']=False
        return p
    receipt['result']=figure.run.model.follow(source,failed)
    rows=figure.table(receipt,source)
    assert len(rows)==9 and sum(r['accepted'] for r in rows)==1
    assert any(not r['geometry_qualified'] for r in rows)


def test_complete_receipt_renderer_binds_artifacts_and_all_data(tmp_path,monkeypatch):
    receipt,source=fixture(); path=tmp_path/'synthetic-audit.json'
    path.write_text(json.dumps(receipt)); digest=figure.sha256(path)
    monkeypatch.setattr(figure.run,'inputs',lambda:deepcopy(source))
    original=figure.draw
    monkeypatch.setattr(figure,'draw',lambda output,rows,steps:original(output,rows,steps,synthetic=True))
    product=figure.render(path,digest,tmp_path/'figure')
    assert product['source_receipt_sha256']==digest and len(product['plotted_data'])==19
    saved=tmp_path/'figure'/(figure.STEM+'.receipt.json')
    assert json.loads(saved.read_bytes())==product
    index=json.loads((tmp_path/'figure'/(figure.STEM+'.index.json')).read_bytes())
    assert index['receipts'][saved.name]==figure.sha256(saved)
    assert all(figure.sha256(tmp_path/'figure'/name)==entry['sha256'] for name,entry in product['outputs'].items())
    assert product['title']==figure.TITLE
    assert '18 measured points' in product['description']
    data=product['data_source']; provenance=product['provenance']
    assert data['artifact']==path.name and data['sha256']==digest
    assert data['selection']==product['selection'] and data['transforms']==product['transforms']
    assert data['panel_selection']==product['panel_selection']
    for panel in ('B','C'):
        assert 'Initial point, predictors and refinements only' in product['panel_selection'][panel]
    assert 'not displayed in B/C' in product['panel_selection']['calibration_values']
    assert 'not calibration samples' in product['accessibility']['overlap']
    assert 'Calibration values remain in the receipt' in product['alt_text']
    assert 'result.steps[].refinement_decision' in data['schema_fields']
    assert data['measurement_fields']==['spec.id','spec.parameters','qualified','vectors','gaps']
    assert provenance['audit_receipt_sha256']==digest and provenance['outputs']==product['outputs']
    assert provenance['generator_sha256']==figure.sha256(Path(figure.__file__))
    assert set(provenance['libraries'])=={'python','numpy','scipy','matplotlib'}
    assert len(product['accessibility']['noncolor_channels'])==5
    assert 'not imputed' in product['accessibility']['missing_data']
    assert len(product['hard_guards'])==7
