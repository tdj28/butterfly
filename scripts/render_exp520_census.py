#!/usr/bin/env python3
"""Plot the complete audited stationary-point inventory, not inferred word chains."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'docs/experiments/receipts/EXP-520-periodic-stationarity-census-result.json'
SHA = 'cb0c5983e0ec2d6c0dc6e7ebf4f4569c028d84f7f6ce8b8ea67fac5465a00b23'
FREEZE = 'ed4bb3fe2ef905dbe5210e1df21f28afd24fe094'
STEM = 'EXP-520-periodic-stationarity-census'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def data(path):
    if sha(path) != SHA:
        raise ValueError('audited source identity differs')
    result = json.loads(Path(path).read_bytes())
    if (result['experiment_id'] != 'EXP-520' or result['source_commit'] != FREEZE
            or result['passed'] is not True or result['segments'] != 417460
            or result['profiles'] != 10 or result['windows'] != 20
            or not result['all_profiles_qualified'] or not result['all_nearest_consistent']
            or any(result[k] is not False for k in ('exact_flow_completeness', 'symbolic_chains_verified', 'D_identified'))):
        raise ValueError('complete audited census required')
    points = result['points']
    if [p['id'] for p in points] != ['coarse--1', 'coarse-+1', 'fine--1', 'fine-+1', 'correction']:
        raise ValueError('complete point order required')
    if sum(v['segments'] for p in points for v in p['profiles']) != result['segments']:
        raise ValueError('complete segment denominator differs')
    rows = []
    for p in points:
        contexts = []
        if [v['method'] for v in p['profiles']] != ['DOP853', 'Radau']:
            raise ValueError('both solver profiles required')
        for v in p['profiles']:
            if not v['qualified'] or not v['polynomial_census_complete'] or v['unresolved'] or v['join_failures'] or len(v['events']) != 40:
                raise ValueError('unqualified polynomial census')
            if [w['phase'] for w in v['windows']] != [.25, 1.25]:
                raise ValueError('both ordered cycle windows required')
            for w in v['windows']:
                if w['count'] != len(w['events']) or w['count'] != 16 or not w['qualified']:
                    raise ValueError('complete qualified window required')
                contexts.append(dict(method=v['method'], window=w['phase'],
                    phases=[e['cycle_phase'] for e in w['events']],
                    gaps=[e['signed_gap'] for e in w['events']],
                    curvature=[e['curvature_sign'] for e in w['events']]))
        index = p['comparison']['nearest_index']
        if not p['comparison']['consistent_nearest'] or index is None:
            raise ValueError('nearest object ambiguous')
        for context, nearest in zip(contexts, p['comparison']['nearest'], strict=True):
            if context['gaps'][index] != nearest['signed_gap']:
                raise ValueError('nominated gap does not belong to complete census')
        values = [e['signed_gap'] for e in p['comparison']['nearest']]
        rows.append(dict(id=p['id'], a=p['parameters']['a'], contexts=contexts,
            nearest_index=index, nearest_gaps=values, mean_gap=float(np.mean(values)),
            minimum_gap=min(values), maximum_gap=max(values), nearest_states=[e['state'] for e in p['comparison']['nearest']]))
    return rows


def render(output):
    output = Path(output)
    if output.exists(): raise ValueError('fresh figure output required')
    rows = data(ROOT/SOURCE)
    output.mkdir(parents=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'svg.hashsalt': STEM, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.9), gridspec_kw={'width_ratios': [1.3, 1]})
    fig.subplots_adjust(left=.085, right=.98, bottom=.26, top=.81, wspace=.29)
    fig.suptitle('A recovered fold contact is not yet a periodic section grazing', fontsize=16, x=.08, ha='left', y=.98)
    fig.text(.08, .9, 'Complete stationary-point census: 417,460 stored segments, two solvers, two cycle windows', fontsize=10, color='#424957')
    ax = axes[0]; correction = rows[-1]
    styles = [('o', '#176887', 'DOP853 / window 1'), ('o', '#cf7520', 'DOP853 / window 2'),
              ('s', '#176887', 'Radau / window 1'), ('s', '#cf7520', 'Radau / window 2')]
    for context, (marker, color, label) in zip(correction['contexts'], styles, strict=True):
        ax.scatter(context['phases'], context['gaps'], s=44, marker=marker, facecolors='none',
                   edgecolors=color, linewidths=1.1, label=label)
    ax.axhline(0., color='#7c2537', linewidth=1, linestyle='--')
    ax.set_yscale('symlog', linthresh=.5)
    ax.set_yticks([-10, -1, 0, 1, 10], labels=['-10', '-1', '0', '1', '10'])
    all_gaps = [g for c in correction['contexts'] for g in c['gaps']]
    ax.set_ylim(min(all_gaps)*1.35, max(all_gaps)*1.35)
    ax.set_xlim(-.015, 1.015)
    ax.set_xticks(np.linspace(0., 1., 6))
    ax.set_xlabel('Phase on the corrected periodic orbit')
    ax.set_ylabel(r'Section displacement $g=y-y_*$ (symmetric-log scale)')
    ax.set_title('A  All 16 stationary points per cycle', loc='left', fontsize=12, pad=11)
    index = correction['nearest_index']; nearest_phase = correction['contexts'][0]['phases'][index]
    ax.annotate(f'Nearest local maximum\ng = {correction["mean_gap"]:.6f}',
        xy=(nearest_phase, correction['mean_gap']), xytext=(.43, -.64),
        arrowprops=dict(arrowstyle='->', color='#30353e'), fontsize=9, ha='left', va='top')
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower left', bbox_to_anchor=(.078, .112), ncol=4, fontsize=8, frameon=False)
    ax.grid(axis='y', alpha=.15)
    ax = axes[1]
    anchor = next(p['a'] for p in rows if p['id'] == 'coarse--1')+1e-5
    for p in rows:
        marker = 'D' if p['id'] == 'correction' else ('s' if p['id'].startswith('coarse') else 'o')
        color = '#a74429' if p['id'] == 'correction' else '#176887'
        x = (p['a']-anchor)/1e-5
        ax.errorbar(x, p['mean_gap'], yerr=[[p['mean_gap']-p['minimum_gap']], [p['maximum_gap']-p['mean_gap']]],
                    fmt=marker, color=color, markersize=6, capsize=3, linewidth=1)
    ax.set_title('B  Same nominated object at all five points', loc='left', fontsize=12, pad=11)
    ax.set_xlabel(r'Parameter displacement $(a-a_{anchor})/10^{-5}$')
    ax.set_ylabel(r'Nearest section displacement $g$ (zoomed scale)')
    ax.ticklabel_format(axis='y', style='plain', useOffset=False)
    ax.grid(alpha=.15)
    ax.text(.03, .96, 'All five gaps remain negative.\nZero is outside this zoom.', transform=ax.transAxes,
            va='top', fontsize=9, bbox=dict(facecolor='white', edgecolor='none', alpha=.9))
    fig.text(.085, .025, 'Overlapping markers retain all solver/window results. Bars are their range, not confidence intervals.\nB: squares = coarse, circles = fine, diamond = correction.\nThis audits saved polynomials, not exact-flow completeness or a Jones symbolic arrow.', fontsize=9, color='#424957')
    outputs = {}
    for extension in ('svg', 'pdf', 'png'):
        path = output/(STEM+'.'+extension)
        metadata = {'Date': None} if extension == 'svg' else ({'CreationDate': None, 'ModDate': None} if extension == 'pdf' else {})
        fig.savefig(path, dpi=300, metadata=metadata)
        outputs[path.name] = dict(bytes=path.stat().st_size, sha256=sha(path))
    plt.close(fig)
    receipt = dict(figure_id=STEM, title='A recovered fold contact is not yet a periodic section grazing',
        description='All stationary section displacements on the corrected cycle, and nearest displacement across all five tested parameter points.',
        alt_text='Panel A shows sixteen stationary y values per corrected cycle. Four solver/window contexts overlap. The closest maximum is below the zero section by about 0.345. Panel B zooms the nearest negative gap at all five a values; none reaches zero.',
        data_source=dict(path=SOURCE, sha256=SHA, fields='points[].profiles[].windows[].events and comparison.nearest',
            selection='All five points, two solvers and two windows. Panel A shows the prescribed corrected point.',
            aggregation='Panel B arithmetic mean and complete min/max over four contexts; no exclusion or jitter.',
            x_transform='Panel B: (a-anchor)/1e-5; anchor is coarse-minus a plus 1e-5.'),
        provenance=dict(source_commit=FREEZE, generator='scripts/render_exp520_census.py',
            generator_sha256=sha(Path(__file__)), matplotlib=matplotlib.__version__, numpy=np.__version__, outputs=outputs),
        plotted_data=rows, anchor_a=anchor, interval_semantics='Descriptive four-context range, not inferential uncertainty.',
        accessibility='Method uses circle/square shape as well as labels; window uses labeled color. Correction diamond is distinct. Panel A explicitly labels symmetric-log scale; panel B explicitly labels zoom and omitted zero.',
        claims_excluded=['exact-flow root completeness', 'D identification', 'homoclinicity', 'Jones symbolic arrow'])
    path = output/(STEM+'.receipt.json')
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2, allow_nan=False)+'\n')
    (output/(STEM+'.index.json')).write_text(json.dumps(dict(figure_id=STEM, receipts={path.name: sha(path)}), sort_keys=True, indent=2)+'\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); render(args.output)
