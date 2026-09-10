#!/usr/bin/env python3
"""Render all EXP-523 trials and the accepted prefix only after a full raw audit."""
import argparse
import json
import math
import platform
from pathlib import Path
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy
from butterfly._paired_startup import sha256
from scripts import run_exp523_refreshed_path as run
from scripts import audit_exp523_refreshed_path as audit

ROOT = Path(__file__).resolve().parents[1]
STEM = 'EXP-523-refreshed-contact-path'
TITLE = 'Contact-path continuation: every prediction tested'
COMMIT = 'eae6745d124c2fa59efc4eff337929e9ff71607d'
CLAIMS = ('symbolic_chains_verified', 'D_identified', 'exact_critical_locus_proved')


def table(receipt, source):
    if (receipt['experiment_id'] != 'EXP-523' or receipt['passed'] is not True
            or receipt['source_commit'] != COMMIT or receipt['inputs'] != run.INPUTS
            or receipt['plan_sha256'] != sha256(run.PLAN) or receipt['new_integrations'] != 0
            or any(receipt[k] is not False for k in CLAIMS) or receipt['initial_anchor'] != source['anchor']):
        raise ValueError('complete authenticated raw-audit identity and claim boundary required')
    result = receipt['result']; points = []
    for step in result['steps']:
        points.extend(step['a_points']+step['c_points'])
        points.extend(p for p in (step['predictor'], step['refinement']) if p is not None)
    queue = iter(points); used = []
    def replay(spec, current):
        point = next(queue, None)
        if point is None: raise ValueError('prescribed measurement missing')
        if point['spec'] != spec: raise ValueError('complete ordered prescribed point set required')
        used.append(spec['id']); return point
    rebuilt = run.model.follow(source, replay)
    if next(queue, None) is not None or not run.prior.coverage.public.equal(rebuilt, result):
        raise ValueError('compact deterministic result replay differs')
    audit.scalar_check(result, source)
    if len(used) != len(set(used)): raise ValueError('duplicate measured point identity')
    rows = []
    def record(point, kind, label, accepted, prediction):
        f = [] if point['vectors'] is None else np.max(np.abs(run.model.local.fold.values(point['vectors'])), axis=1).tolist()
        g = [] if point['gaps'] is None else (15*run.model.local.gvalues(point['gaps'])).tolist()
        rows.append(dict(id=point['spec']['id'], parameters=point['spec']['parameters'], kind=kind,
            label=label, accepted=accepted, prediction_qualified=prediction, geometry_qualified=point['qualified'],
            full_state_distances=f, signed_gaps=g))
    record(dict(spec=dict(id='initial-EXP-522', parameters=source['anchor']), qualified=True,
        vectors=source['vectors'], gaps=source['gaps']), 'initial', 'Start', True, None)
    for step in result['steps']:
        for p in step['a_points']+step['c_points']: record(p, 'calibration', p['spec']['id'], False, None)
        for kind, symbol in [('predictor', 'P'), ('refinement', 'R')]:
            p = step[kind]
            if p is not None:
                record(p, kind, symbol+str(step['index']+1), step['accepted'] == p['spec'], step[kind+'_decision']['qualified'])
    return rows


def draw(output, rows, completed_steps, *, synthetic=False):
    output = Path(output)
    if output.exists(): raise ValueError('fresh figure output directory required')
    output.mkdir(parents=True)
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10, 'svg.hashsalt':STEM,
        'axes.spines.top':False, 'axes.spines.right':False})
    fig, axes = plt.subplots(1, 3, figsize=(14, 6))
    fig.subplots_adjust(left=.065, right=.98, top=.73, bottom=.29, wspace=.38)
    title = TITLE
    if synthetic: title = 'SYNTHETIC CONTROL - '+title
    fig.suptitle(title, x=.065, ha='left', y=.97, fontsize=15)
    trials = [r for r in rows if r['kind'] != 'calibration']
    failed = sum(r['kind'] == 'predictor' and r['prediction_qualified'] is False for r in rows)
    invalid = sum(not r['geometry_qualified'] for r in rows)
    fig.text(.065,.88,f'{completed_steps}/2 continuation steps accepted; {len(rows)-1} measurements; '
        f'{failed} failed predictor(s) retained; {invalid} unqualified geometry point(s).',fontsize=11)
    fig.text(.065,.82,'P = predictor; R = normal refinement. Acceptance requires all tests, not just proximity.',color='#414956')
    colors = dict(initial='#59646f', accepted='#087f78', trial='#b64d32', calibration='#a4abb2')
    a0 = rows[0]['parameters']['a']
    for row in rows:
        p = row['parameters']; calibration = row['kind'] == 'calibration'
        color = colors['calibration' if calibration else ('accepted' if row['accepted'] else 'trial')]
        marker = '+' if calibration else ('D' if row['kind'] == 'initial' else ('o' if row['accepted'] else 'X'))
        axes[0].scatter(p['c'], 1e6*(p['a']-a0), s=38 if calibration else 75,
            marker=marker, color=color, linewidth=1.2, zorder=2 if calibration else 4)
        if not calibration:
            axes[0].annotate(row['label'], (p['c'],1e6*(p['a']-a0)), xytext=(5,-16 if row['kind'] == 'refinement' else 7),
                textcoords='offset points', fontsize=8)
    accepted = [r for r in rows if r['accepted']]
    axes[0].plot([r['parameters']['c'] for r in accepted], [1e6*(r['parameters']['a']-a0) for r in accepted],
        color=colors['accepted'], linestyle=':', linewidth=1, zorder=1)
    axes[0].set(title='A  Measured parameter samples', xlabel='c', ylabel=r'$10^6(a-a_0)$')
    axes[0].ticklabel_format(useOffset=False, axis='x'); axes[0].margins(x=.18, y=.2)
    for i, row in enumerate(trials):
        color = colors['accepted' if row['accepted'] else 'trial']; values = row['full_state_distances']
        if values:
            axes[1].vlines(i, max(min(values),1e-18), max(max(values),1e-18), color=color, linewidth=3)
            axes[1].scatter(i, max(max(values),1e-18), color=color, marker='o' if row['accepted'] else 'X', s=65,zorder=3)
        for j, (color, marker) in enumerate([('#176887','o'),('#aa621e','s')]):
            g = row['signed_gaps'][j::2]
            if g:
                mean = math.fsum(g)/4
                axes[2].errorbar(i+[-.045,.045][j],mean,yerr=[[mean-min(g)],[max(g)-mean]],
                    fmt=marker,color=color,capsize=3,markersize=6,
                    label=f'Maximum {j+1} (root {[5,13][j]})' if i == 0 else None)
    axes[1].axhline(1e-4,color='#939ba5',linestyle='--',linewidth=1,label='Proximity gate')
    axes[1].axhline(1e-7,color=colors['accepted'],linestyle=':',linewidth=1.2,label='Accepted-point gate')
    axes[1].set_yscale('log'); axes[1].set(title='B  All 16 contact variants',ylabel='Scaled full-state distance')
    axes[1].legend(loc='best',fontsize=8,frameon=False)
    axes[2].axhline(0,color='#59646f',linestyle='--',linewidth=1)
    axes[2].set(title='C  Distance from section grazing',ylabel=r'Signed maximum height $y-y_*$')
    axes[2].legend(loc='upper right',bbox_to_anchor=(1,.88),fontsize=8,frameon=False)
    for ax in axes[1:]:
        ax.set_xticks(range(len(trials)),[r['label'] for r in trials]); ax.set_xlim(-.4,len(trials)-.6)
        ax.set_xlabel('Measurement stage (not a continuous trajectory)')
    for ax in axes: ax.grid(alpha=.14)
    fig.text(.065,.09,'A: gray crosses are all calibration samples; teal circles are accepted endpoints; red crosses are unaccepted trials.\n'
        'P/R samples can overlap in A. B/C show Start, P and R; calibration values remain in the receipt.\n'
        'Dotted parameter segments only guide the eye. B/C retain all numerical variant ranges, not confidence intervals.\n'
        'Zero height in C is section grazing. No C/D identification, grazing endpoint, exact locus, homoclinic orbit or Jones arrow is established.',
        fontsize=9,color='#414956')
    outputs = {}
    for ext in ('svg','pdf','png'):
        path = output/(STEM+'.'+ext)
        metadata = {'Date':None} if ext == 'svg' else ({'CreationDate':None,'ModDate':None} if ext == 'pdf' else {})
        fig.savefig(path,dpi=300,metadata=metadata); outputs[path.name] = dict(bytes=path.stat().st_size,sha256=sha256(path))
    plt.close(fig)
    return outputs


def render(receipt_path, expected_sha, output):
    path = Path(receipt_path)
    if not re.fullmatch('[0-9a-f]{64}',expected_sha) or sha256(path) != expected_sha:
        raise ValueError('explicit audited receipt byte identity required')
    receipt = json.loads(path.read_bytes()); source = run.inputs(); rows = table(receipt,source)
    outputs = draw(output,rows,receipt['result']['completed_steps'])
    product = dict(figure_id=STEM,source_commit=COMMIT,source_receipt_sha256=expected_sha,
        input_sources=run.INPUTS,manifest_sha256=sha256(run.PLAN),generator='scripts/render_exp523_path.py',
        generator_sha256=sha256(Path(__file__)),matplotlib=matplotlib.__version__,numpy=np.__version__,
        outputs=outputs,plotted_data=rows,completed_steps=receipt['result']['completed_steps'],
        selection='All measured calibration, predictor and refinement points; accepted prefix distinguished from trials.',
        panel_selection=dict(A='All rows: initial point, calibration samples, predictors and refinements.',
            B='Initial point, predictors and refinements only; all available 16-variant contact ranges.',
            C='Initial point, predictors and refinements only; all available four-context ranges for both gaps.',
            calibration_values='Retained in plotted_data; not displayed in B/C.'),
        interval_semantics='All 16 full-state variants and four contexts per gap; ranges are not confidence intervals.',
        transforms=dict(parameter_a='1e6*(a-initial a)',contact='max abs component per six-vector; plot floor 1e-18',
            gap='15 times normalized signed gap; mean and full four-context range'),
        alt_text='Panel A includes all parameter samples. Panels B/C show only the initial point, predictors and refinements: their contact residual ranges against both gates and both tracked maxima relative to zero-height grazing. Calibration values remain in the receipt. Dotted segments are not a proved continuous locus.',
        claims_excluded=['continuous qualified path','exact critical locus','C/D identification','grazing endpoint','homoclinic connection','Jones arrow'])
    product.update(
        title=TITLE,
        description=(f"{product['completed_steps']} of two bounded continuation steps accepted; "
            f"{len(rows)-1} measured points retained, including every attempted calibration, "
            "predictor and refinement. Panels distinguish parameter samples, full-state "
            "contact residuals and the two tracked section-height maxima."),
        data_source=dict(
            artifact=path.name, sha256=expected_sha,
            schema_fields=['experiment_id', 'passed', 'source_commit', 'inputs', 'plan_sha256',
                'initial_anchor', 'result.completed_steps', 'result.steps[].a_points',
                'result.steps[].c_points', 'result.steps[].predictor', 'result.steps[].refinement',
                'result.steps[].accepted', 'result.steps[].predictor_decision',
                'result.steps[].refinement_decision'],
            measurement_fields=['spec.id', 'spec.parameters', 'qualified', 'vectors', 'gaps'],
            initial_point='EXP-522 inputs bound by input_sources; initial_anchor checked against those inputs.',
            selection=product['selection'], panel_selection=product['panel_selection'],
            transforms=product['transforms']),
        provenance=dict(source_commit=COMMIT, audit_receipt_sha256=expected_sha,
            manifest_sha256=product['manifest_sha256'], input_sources=run.INPUTS,
            generator=product['generator'], generator_sha256=product['generator_sha256'],
            libraries=dict(python=platform.python_version(), numpy=np.__version__,
                scipy=scipy.__version__, matplotlib=matplotlib.__version__),
            outputs=outputs,
            scope='Compact controller and scalar replay of an authenticated full-raw-audit receipt; not independent replication.'),
        accessibility=dict(
            noncolor_channels=['Initial diamond, accepted circle, unaccepted X, calibration plus in A.',
                'P/R text labels distinguish predictions and normal refinements.',
                'Accepted circles and unaccepted X markers in B.',
                'Circle/square markers and root-number legend distinguish the two maxima in C.',
                'Dashed/dotted lines distinguish the two contact thresholds.'],
            overlap='Near-coincident P/R samples may overlap in A; B/C show only Start, P and R separately, not calibration samples.',
            missing_data='Unqualified points remain in A and the displayed count; unavailable vectors/gaps are not imputed.'),
        hard_guards=['Explicit audit-receipt SHA-256 before drawing.',
            'Passed full-raw-audit identity, immutable source, manifest, inputs and claim boundaries.',
            'Initial anchor matches bound EXP-522 inputs.',
            'Complete ordered compact controller replay, including failed and unaccepted measurements.',
            'Separate scalar decision checks; unique measurement identifiers.',
            'Fresh output directory only; no overwrite.',
            'Output byte counts/hashes and receipt hash index.'])
    output = Path(output); receipt_file = output/(STEM+'.receipt.json')
    receipt_file.write_text(json.dumps(product,sort_keys=True,indent=2,allow_nan=False)+'\n')
    (output/(STEM+'.index.json')).write_text(json.dumps(dict(figure_id=STEM,receipts={receipt_file.name:sha256(receipt_file)}),sort_keys=True,indent=2)+'\n')
    return product


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt',type=Path,required=True); parser.add_argument('--expected-sha256',required=True)
    parser.add_argument('--output',type=Path,required=True); args=parser.parse_args()
    render(args.receipt,args.expected_sha256,args.output)
