#!/usr/bin/env python3
"""Render all audited c-stencil points and the prescribed correction, if any."""
import argparse
import hashlib
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scripts import exp521_critical_response as model

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'docs/experiments/receipts/EXP-521-critical-periodic-response-result.json'
FREEZE = '7260931511c2fc4583dbb89e7716b2d54c082005'
STEM = 'EXP-521-critical-periodic-response'
PARENTS = {
    'docs/experiments/receipts/EXP-519-fixed-c-fold-response-result.json': '92ff9159ca3de7794a481e9d682d02626b945495f3ad87e6c7d095137f0117ec',
    'docs/experiments/receipts/EXP-520-periodic-stationarity-census-result.json': 'cb0c5983e0ec2d6c0dc6e7ebf4f4569c028d84f7f6ce8b8ea67fac5465a00b23'}


def sha(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()


def table(receipt, parent519, parent520):
    if (receipt['experiment_id'] != 'EXP-521' or receipt['source_commit'] != FREEZE
            or receipt['passed'] is not True or any(receipt[k] is not False
            for k in ('symbolic_chains_verified', 'D_identified', 'exact_critical_locus_proved'))):
        raise ValueError('complete audited identity and bounded claim required')
    result = receipt['result']; anchor = parent519['result']['correction']
    parameters = anchor['spec']['parameters']
    if [p['spec'] for p in result['points']] != model.stencil(parameters):
        raise ValueError('complete prescribed c stencil required')
    corrected = result['correction']
    if (corrected is None) != (result['proposal'] is None): raise ValueError('correction presence differs')
    if corrected is not None and corrected['spec'] != result['proposal']['spec']:
        raise ValueError('prescribed correction identity differs')
    census = parent520['points'][-1]
    if census['id'] != 'correction' or census['parameters'] != parameters: raise ValueError('anchor census identity differs')
    match = model.match(census, census)
    points = [dict(spec=dict(id='anchor', parameters=parameters), qualified=True,
        vectors=anchor['vectors'], gaps=match['gaps'])]+result['points']+([] if corrected is None else [corrected])
    rows = []
    for p in points:
        vectors = None if p['vectors'] is None else model.fold.values(p['vectors'])
        gaps = None if p['gaps'] is None else model.gvalues(p['gaps'])*15
        distances = [] if vectors is None else np.max(np.abs(vectors), axis=1).tolist()
        values = [] if gaps is None else [gaps[i::2].tolist() for i in range(2)]
        rows.append(dict(id=p['spec']['id'], parameters=p['spec']['parameters'], qualified=p['qualified'],
            normalized_c=(p['spec']['parameters']['c']-parameters['c'])/.005,
            normalized_a=(p['spec']['parameters']['a']-parameters['a'])/1e-5,
            gaps=values, full_state_distances=distances,
            gap_ranges=[dict(mean=math.fsum(v)/4, minimum=min(v), maximum=max(v)) for v in values],
            distance_range=None if not distances else dict(minimum=min(distances), maximum=max(distances))))
    return rows


def load(expected_sha):
    if len(expected_sha) != 64 or sha(ROOT/SOURCE) != expected_sha: raise ValueError('audited receipt hash differs')
    parents = []
    for name, digest in PARENTS.items():
        if sha(ROOT/name) != digest: raise ValueError('fixed parent bytes differ')
        parents.append(json.loads((ROOT/name).read_bytes()))
    receipt = json.loads((ROOT/SOURCE).read_bytes())
    return receipt, table(receipt, *parents)


def render(output, expected_sha):
    source, rows = load(expected_sha); output = Path(output)
    if output.exists(): raise ValueError('fresh figure output required')
    output.mkdir(parents=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'svg.hashsalt': STEM,
        'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.6))
    fig.subplots_adjust(left=.085, right=.98, top=.79, bottom=.34, wspace=.3)
    fig.suptitle('Testing a contact-preserving step toward periodic grazing', x=.085, ha='left', y=.98, fontsize=15)
    correction = source['result']['correction']
    verdict = ('No correction authorized' if correction is None else
        ('Measured correction passes the local gates' if source['result']['decision']['qualified'] else 'Measured correction fails the local gates'))
    fig.text(.085, .89, verdict+' | all prescribed stencil points retained', fontsize=10, color='#414956')
    checks = None
    decision = source['result']['decision']
    if decision is not None and decision['folds'] and decision['gaps']:
        checks = dict(full_state_maximum=max(v['distance'] for v in decision['folds']),
            fold_prediction_maximum=max(v['prediction_error'] for v in decision['folds']),
            gap_prediction_maximum=max(v['prediction_error'] for v in decision['gaps']),
            overall_qualified=decision['qualified'], full_state_limit=1e-4, prediction_limit=.1)
        contact = 'passes' if checks['full_state_maximum'] <= 1e-4 else 'fails'
        fig.text(.085, .842, f'Correction: contact {contact}; fold prediction error {checks["fold_prediction_maximum"]:.4g}; '
            f'gap prediction error {checks["gap_prediction_maximum"]:.4g} (prediction limit: 0.1).', fontsize=9, color='#414956')
    colors = ['#176887', '#b66518']; shapes = ['o', 's']
    fixed = sorted(rows[:5], key=lambda r: r['normalized_c'])
    for j, (color, marker) in enumerate(zip(colors, shapes, strict=True)):
        valid = [r for r in fixed if r['gap_ranges']]
        # Missing identity breaks the line; it never becomes a zero gap.
        axes[0].plot([r['normalized_c'] for r in fixed],
            [r['gap_ranges'][j]['mean'] if r['gap_ranges'] and r['qualified'] else np.nan for r in fixed],
            color=color, alpha=.35, linewidth=1)
        for i, row in enumerate(valid):
            v = row['gap_ranges'][j]
            axes[0].errorbar(row['normalized_c'], v['mean'],
                yerr=[[v['mean']-v['minimum']], [v['maximum']-v['mean']]],
                fmt=marker, color=color, markersize=6, capsize=3,
                markerfacecolor=color if row['qualified'] else 'white', markeredgecolor=color,
                label=f'Inner maximum {j+1} (source root {[5,13][j]})' if i == 0 else None)
    if correction is not None and rows[-1]['gap_ranges']:
        for j, color in enumerate(colors):
            v = rows[-1]['gap_ranges'][j]
            axes[0].errorbar(rows[-1]['normalized_c'], v['mean'],
                yerr=[[v['mean']-v['minimum']], [v['maximum']-v['mean']]],
                fmt=['*', 'P'][j], markersize=[12, 9][j], capsize=4, color=color,
                markerfacecolor=color if rows[-1]['qualified'] else 'white', markeredgecolor='black',
                markeredgewidth=.6, zorder=5)
    axes[0].axhline(0, color='#923347', linestyle='--', linewidth=1)
    axes[0].set_title('A  Both identified periodic maxima', loc='left', fontsize=12, pad=12)
    axes[0].set_ylabel(r'Section displacement $g=y-y_*$')
    axes[0].ticklabel_format(axis='y', style='plain', useOffset=False)
    for row in rows:
        if not row['distance_range']: continue
        value = row['distance_range']; x = row['normalized_c']
        marker = '*' if row['id'] == 'critical-step' else ('D' if row['id'] == 'anchor' else 'o')
        color = '#176887' if row['qualified'] else '#767676'
        axes[1].vlines(x, value['minimum'], value['maximum'], color=color, linewidth=2)
        axes[1].scatter(x, value['maximum'], marker=marker, s=120 if marker == '*' else 40,
            color=color, edgecolors='black', linewidths=.4, zorder=4)
    axes[1].axhline(1e-4, color='#923347', linestyle='--', linewidth=1, label='Full-state acceptance limit')
    axes[1].set_yscale('symlog', linthresh=1e-8)
    axes[1].set_title('B  Full fold/orbit contact, all 16 variants', loc='left', fontsize=12, pad=12)
    axes[1].set_ylabel('Scaled full-state distance\n(symmetric-log scale)')
    handles, labels = [], []
    for ax in axes:
        h, names = ax.get_legend_handles_labels(); handles.extend(h); labels.extend(names)
    fig.legend(handles, labels, loc='lower left', bbox_to_anchor=(.08, .185), ncol=3, fontsize=8, frameon=False)
    for ax in axes:
        ax.set_xlabel(r'Parameter displacement $(c-c_0)/0.005$')
        ax.grid(alpha=.15); ax.set_xlim(-1.12, 1.12)
    missing = [r['id'] for r in rows if not r['gaps'] or not r['full_state_distances']]
    unqualified = [r['id'] for r in rows if not r['qualified']]
    foot = ('Circles/squares: fixed-a data. Correction: star (maximum 1), plus (maximum 2); a also changes.\n'
        'A: means and ranges of four solver/window contexts. B: complete range and worst of 16 variants.\n'
        'Open/gray: unqualified geometry. Overall correction verdict also includes prediction. Ranges are not confidence intervals.\n'
        'Zero in A is a section-grazing height, not a homoclinic criterion. This is not a verified Jones arrow.')
    if unqualified: foot += '\nUnqualified: '+', '.join(unqualified)
    if missing: foot += '\nUnavailable geometry: '+', '.join(missing)
    fig.text(.085, .035, foot, fontsize=8.5, color='#414956')
    outputs = {}
    for extension in ('svg', 'pdf', 'png'):
        path = output/(STEM+'.'+extension)
        metadata = {'Date': None} if extension == 'svg' else ({'CreationDate': None, 'ModDate': None} if extension == 'pdf' else {})
        fig.savefig(path, dpi=300, metadata=metadata)
        outputs[path.name] = dict(bytes=path.stat().st_size, sha256=sha(path))
    plt.close(fig)
    receipt = dict(figure_id=STEM, title='Testing a contact-preserving step toward periodic grazing',
        description='Both inner periodic maxima and full-state contact across every c-stencil point and the prescribed correction, if authorized.',
        alt_text='Two panels compare the signed section gaps of both identified periodic maxima and the full-state fold/orbit distances. Every fixed-a stencil point is retained; star/plus shapes distinguish the two maxima on the step that changes a as well as c. Unqualified points have open/gray markers and are explicitly listed. '+verdict+'.',
        data_source=dict(path=SOURCE, sha256=expected_sha, parent_inputs=PARENTS,
            fields='result.points/correction: gaps, vectors, spec, qualified; EXP-519 correction and EXP-520 corrected census for anchor.',
            selection='All four prescribed stencil points, audited parent anchor, and prescribed correction if present; none excluded.',
            transformations='c displacement divided by .005; g residual multiplied by 15; per-variant full-state distance is max absolute normalized component.',
            aggregation='g: mean/min/max of four solver/window contexts per root; contact: min/max of all 16 variants.'),
        provenance=dict(source_commit=FREEZE, generator='scripts/render_exp521_response.py', generator_sha256=sha(Path(__file__)),
            matplotlib=matplotlib.__version__, numpy=np.__version__, outputs=outputs), plotted_data=rows,
        interval_semantics='Descriptive complete numerical-variant ranges, not confidence intervals.',
        accessibility='Root uses circle/square and explicit legend, correction roots use star/plus, anchor diamond in panel B; unqualified points use open/gray markers and an explicit list. All axes/scales labeled.',
        unqualified_points=unqualified, unavailable_geometry=missing, correction_checks=checks,
        guards=['fixed source hash and freeze', 'complete stencil order/parameters', 'prescribed correction only', 'finite complete keyed vectors', 'both tracked roots'],
        claims_excluded=['exact-flow completeness', 'exact critical locus', 'C/D dictionary', 'homoclinic orbit', 'Jones symbolic arrow'])
    path = output/(STEM+'.receipt.json'); path.write_text(json.dumps(receipt, sort_keys=True, indent=2, allow_nan=False)+'\n')
    (output/(STEM+'.index.json')).write_text(json.dumps(dict(figure_id=STEM, receipts={path.name:sha(path)}), sort_keys=True, indent=2)+'\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True); args = parser.parse_args(); render(args.output, args.expected_sha256)
