#!/usr/bin/env python3
"""Show the original anchor, rejected trial, and separately accepted refinement."""
import argparse
import json
import math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from butterfly._paired_startup import sha256
from scripts import exp521_critical_response as model
from scripts import run_exp522_nonlinear_refinement as run

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'docs/experiments/receipts/EXP-522-nonlinear-contact-refinement-result.json'
SOURCE_SHA = '0f942da7d44560dc57feed927263198f68e389bb53472f0f0e6028927d52c866'
STEM = 'EXP-522-nonlinear-contact-refinement'


def table(receipt, source):
    if (receipt['experiment_id'] != 'EXP-522' or receipt['passed'] is not True
            or receipt['source_commit'] != '41bb1943fdcd0756a1f8077241287272afbf8548'
            or any(receipt[k] is not False for k in ('parent_predictor_qualified',
                'symbolic_chains_verified', 'D_identified', 'exact_critical_locus_proved'))):
        raise ValueError('fixed audited identity and claim limits required')
    r = receipt['result']; p = r['correction']
    if p is None or p['spec'] != r['proposal']['spec'] or r['proposal'] != run.model.proposal(source):
        raise ValueError('prescribed refinement identity required')
    # Separate references remain explicit. No reuse of an old audit as a new one.
    if receipt['prediction_anchor'] != source['anchor'] or receipt['progress_anchor'] != source['progress_anchor']:
        raise ValueError('prediction and progress references differ')
    original = run.parent.inputs()
    records = [dict(id='Original anchor', parameters=source['progress_anchor'], qualified=True,
                   vectors=original['vectors'], gaps=source['progress_gaps']),
        dict(id='EXP-521 trial', parameters=source['anchor'], qualified=True,
             vectors=source['vectors'], gaps=source['gaps']),
        dict(id='EXP-522 refinement', parameters=p['spec']['parameters'], qualified=p['qualified'],
             vectors=p['vectors'], gaps=p['gaps'])]
    rows = []; initial = model.gvalues(source['progress_gaps'])
    for i, point in enumerate(records):
        f = [] if point['vectors'] is None else np.max(np.abs(model.fold.values(point['vectors'])), axis=1).tolist()
        g = [] if point['gaps'] is None else model.gvalues(point['gaps']).tolist()
        improvement = [] if not g else (100*(1-np.abs(g)/np.abs(initial))).tolist()
        rows.append(dict(id=point['id'], parameters=point['parameters'], geometry_qualified=point['qualified'],
            outcome=['accepted original contact', 'rejected predictor', 'accepted refinement' if r['decision']['qualified'] else 'rejected refinement'][i],
            full_state_distances=f, raw_signed_gaps=[x*15 for x in g], net_gap_improvement_percent=improvement))
    return rows


def render(output):
    if sha256(ROOT/SOURCE) != SOURCE_SHA: raise ValueError('fixed audited source bytes differ')
    receipt = json.loads((ROOT/SOURCE).read_bytes()); source = run.inputs(); rows = table(receipt, source)
    output = Path(output)
    if output.exists(): raise ValueError('fresh output directory required')
    output.mkdir(parents=True)
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10, 'svg.hashsalt':STEM,
        'axes.spines.top':False, 'axes.spines.right':False})
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.6))
    fig.subplots_adjust(left=.09, right=.98, top=.76, bottom=.29, wspace=.28)
    fig.suptitle('A fresh nonlinear correction repairs the contact prediction', x=.09, ha='left', y=.975, fontsize=15)
    decision = receipt['result']['decision']; local = decision['local']
    ferror = max(r['prediction_error'] for r in local['folds']); gerror = max(r['prediction_error'] for r in local['gaps'])
    factor = min(r['before']/r['actual'] for r in decision['reduction'])
    fig.text(.09, .88, f'Refinement {"passes" if decision["qualified"] else "fails"}: contact improves at least {factor:.1f}x in every variant.', fontsize=11)
    fig.text(.09, .83, f'New fold/gap prediction errors: {ferror:.4f} / {gerror:.4f} (limit 0.1). EXP-521 remains rejected.', fontsize=10, color='#414956')
    for i, row in enumerate(rows):
        values = row['full_state_distances']
        if values:
            color = ['#65717a', '#a43c50', '#126f75'][i]
            axes[0].vlines(i, min(values), max(values), color=color, linewidth=3)
            axes[0].scatter(i, max(values), marker=['D','X','*'][i], s=[65,85,150][i], color=color,
                edgecolor='black', linewidth=.5, zorder=3)
    axes[0].axhline(1e-4, color='#a43c50', linestyle='--', linewidth=1, label='Contact radius')
    axes[0].set_yscale('log'); axes[0].set_ylabel('Scaled full-state distance')
    axes[0].set_title('A  All 16 contact variants', loc='left', pad=10)
    axes[0].legend(loc='lower left', fontsize=9, frameon=False)
    for j, (color, marker) in enumerate([('#176887','o'),('#b66518','s')]):
        for i, row in enumerate(rows):
            v = row['net_gap_improvement_percent'][j::2]
            if not v: continue
            mean = math.fsum(v)/4
            axes[1].errorbar(i+[-.045,.045][j], mean, yerr=[[mean-min(v)],[max(v)-mean]],
                fmt=marker, color=color, capsize=4, markersize=7,
                label=f'Maximum {j+1} (root {[5,13][j]})' if i == 0 else None)
    axes[1].axhline(0, color='#65717a', linewidth=1)
    axes[1].set_ylabel('Absolute-gap reduction (%)\nfrom original anchor')
    axes[1].set_title('B  Net progress, not trial-to-refinement gain', loc='left', pad=10)
    axes[1].legend(loc='lower right', fontsize=9, frameon=False)
    for ax in axes:
        ax.set_xticks(range(3), ['Original\nanchor','Rejected\ntrial','New\nrefinement'])
        ax.set_xlim(-.35, 2.35); ax.grid(alpha=.15)
    fig.text(.09, .075, 'All variants retained: 16 full-state comparisons; four solver/window contexts for each maximum. Ranges are not confidence intervals.\n'
        'The trial and refinement share c = 7.147; only a changes during refinement. Both gap heights remain negative.\n'
        'These are discrete stages, not a continuously qualified path. No grazing endpoint, exact contact, homoclinic orbit or Jones arrow is established.',
        fontsize=8.5, color='#414956')
    outputs = {}
    for extension in ('svg','pdf','png'):
        path = output/(STEM+'.'+extension)
        metadata = {'Date':None} if extension == 'svg' else ({'CreationDate':None,'ModDate':None} if extension == 'pdf' else {})
        fig.savefig(path, dpi=300, metadata=metadata); outputs[path.name] = dict(bytes=path.stat().st_size, sha256=sha256(path))
    plt.close(fig)
    product = dict(figure_id=STEM, sources=dict(run.INPUTS, **{SOURCE:SOURCE_SHA}),
        source_commit=receipt['source_commit'], generator='scripts/render_exp522_refinement.py',
        generator_sha256=sha256(Path(__file__)), matplotlib=matplotlib.__version__, numpy=np.__version__, outputs=outputs,
        plotted_data=rows, full_state_transform='max absolute normalized component for each of 16 six-vectors',
        gap_transform='100*(1-abs(g)/abs(original g)), all four contexts per root; original signed gap retained times15',
        selection='Original anchor, prescribed rejected trial, sole prescribed new refinement; EXP-521 stencil shown in its separate complete figure.',
        interval_semantics='Complete numerical variant ranges, not confidence intervals',
        minimum_contact_improvement_factor=factor, fold_prediction_maximum=ferror, gap_prediction_maximum=gerror,
        refinement_qualified=decision['qualified'], parent_predictor_qualified=False,
        alt_text='Two panels show the large drop in fold/orbit contact residual after the new correction and retained net grazing-gap progress. Rejected trial is explicitly labeled. The first gap gives back a small amount of trial progress; both gaps remain below the section.',
        claims_excluded=['continuous qualified path','exact contact','grazing endpoint','homoclinic connection','Jones arrow'])
    path = output/(STEM+'.receipt.json'); path.write_text(json.dumps(product,sort_keys=True,indent=2,allow_nan=False)+'\n')
    (output/(STEM+'.index.json')).write_text(json.dumps(dict(figure_id=STEM,receipts={path.name:sha256(path)}),sort_keys=True,indent=2)+'\n')
    return product


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output',type=Path,required=True)
    render(parser.parse_args().output)
