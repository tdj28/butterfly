#!/usr/bin/env python3
"""Plot every direction/node/return-pair cell without joining event sheets."""
import argparse
import io
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import Patch, Rectangle
import numpy as np

from scripts import exp516_ordinal_coverage as screen


def plot_data(value):
    rows = value['analysis']['rows']
    if len(rows) != 2 or [r['direction'] for r in rows] != [0, 1]:
        raise ValueError('both directions required')
    panels = []
    for row in rows:
        if len(row['samples']) != 20:
            raise ValueError('complete original grid required')
        cells = []
        for item in row['ordinals']:
            if [n['node'] for n in item['nodes']] != list(range(20)):
                raise ValueError('complete ordinal/node plot matrix required')
            for n in item['nodes']:
                r = n['comparison']
                d = r['joint_distance']
                if d is not None and (not math.isfinite(d) or d < 0):
                    raise ValueError('nonnegative finite distance required')
                cells.append(dict(node=n['node'], ordinal=item['ordinal'], distance=d,
                    regular=r['paired_regular'], sampled_coverage=r['sampled_reference_coverage']))
        if [r['ordinal'] for r in row['ordinals']] != list(range(1, len(row['ordinals'])+1)):
            raise ValueError('no missing ordinal rows permitted')
        panels.append(dict(direction=row['direction'], ordinals=len(row['ordinals']), cells=cells))
    return panels


def render(receipt, expected_sha, output):
    checked = screen.verify(receipt, expected_sha)
    value = json.loads(receipt.read_bytes())
    data = plot_data(value)
    if output.exists():
        raise ValueError('fresh figure directory required')
    output.mkdir(parents=True)
    stem = 'EXP-516-event-ordinal-coverage'
    positives = [c['distance'] for p in data for c in p['cells'] if c['distance'] is not None and c['distance'] > 0]
    low = 10**math.floor(math.log10(min([1e-6, *positives])))
    high = 10**math.ceil(math.log10(max([1., *positives])))
    norm = LogNorm(vmin=low, vmax=high)
    cmap = plt.get_cmap('viridis_r').copy()
    cmap.set_bad('#dedede')
    plt.rcParams.update({'font.size':10, 'svg.fonttype':'none', 'svg.hashsalt':stem})
    fig, axes = plt.subplots(1, 2, figsize=(13, 7), layout='constrained', sharey=True)
    max_ordinal = max(p['ordinals'] for p in data)
    for ax, panel in zip(axes, data, strict=True):
        array = np.full((max_ordinal, 20), np.nan)
        for c in panel['cells']:
            if c['distance'] is not None:
                array[c['ordinal']-1, c['node']] = max(c['distance'], low)
        im = ax.imshow(array, cmap=cmap, norm=norm, interpolation='none', aspect='auto')
        for c in panel['cells']:
            if c['distance'] is not None and not c['regular']:
                ax.plot(c['node'], c['ordinal']-1, 'x', color='#e04b47', ms=5, mew=1.1)
            if c['sampled_coverage']:
                ax.plot(c['node'], c['ordinal']-1, 'o', color='black', mfc='none', ms=9, mew=1.2)
            if c['distance'] == 0:
                ax.text(c['node'], c['ordinal']-1, '0', ha='center', va='center', color='black', fontsize=8)
        if max_ordinal >= 8:
            ax.add_patch(Rectangle((-.5, 6.5), 20, 1, fill=False, lw=1.8, edgecolor='#bd3333'))
        ax.set_xticks(range(20))
        ax.set_yticks(range(max_ordinal), [f'{i} → {i+1}' for i in range(1, max_ordinal+1)])
        ax.tick_params(axis='x', labelsize=8)
        ax.set_xlabel('Original grid node (not a uniform physical coordinate)')
        values = [c['distance'] for c in panel['cells'] if c['regular'] and c['distance'] is not None]
        label = f'Nearest regular sampled pair: {min(values):.3g}' if values else 'No regular sampled pairs'
        ax.set_title(f'Direction {panel["direction"]}\n{label}', fontsize=11)
    axes[0].set_ylabel('Accepted input → output return ordinal')
    bar = fig.colorbar(im, ax=axes, fraction=.035, pad=.02)
    bar.set_label('Worst full-state pair distance to all four references (scaled max norm)')
    fig.legend(handles=[Patch(facecolor='#dedede', label='Missing pair / horizon-limited'),
        plt.Line2D([], [], marker='x', color='#e04b47', ls='none', label='Fails paired regularity'),
        Patch(facecolor='none', edgecolor='#bd3333', label='Previously fixed 8 → 9 screen'),
        plt.Line2D([], [], marker='o', mfc='none', color='black', ls='none', label='Regular sampled distance ≤ 1e-6')],
        loc='outside lower center', ncols=2, frameon=False, fontsize=9)
    fig.suptitle('EXP-516 | Check every retained return, not just the eighth\n'
        'Saved-data coverage screen; no lines across unsampled intervals and no newly qualified folds.',
        fontsize=13, fontweight='bold')
    svg = io.StringIO()
    fig.savefig(svg, format='svg', metadata={'Date':None})
    (output/(stem+'.svg')).write_text('\n'.join(s.rstrip() for s in svg.getvalue().splitlines())+'\n')
    fig.savefig(output/(stem+'.pdf'), metadata={'CreationDate':None, 'ModDate':None})
    fig.savefig(output/(stem+'.png'), dpi=300)
    plt.close(fig)
    metadata = dict(figure_id=stem, title='All retained return-pair coverage',
        description='Both directions and every original grid node at every available consecutive accepted return pair.',
        alt_text='Two heatmaps display full-state reference distances by grid node and return ordinal. Red crosses preserve regularity failures, gray cells mark missing pairs, and a red box marks the previously fixed eighth-to-ninth-return screen.',
        data_source=dict(artifact=str(receipt.resolve().relative_to(screen.ROOT)), sha256=expected_sha,
            fields=['analysis.rows[].ordinals[].nodes[].comparison'],
            selection='All direction/node/ordinal cells, including invalid and missing.', exclusions='None',
            aggregation='Maximum scaled distance over input/output endpoints, both solvers and all four references.',
            transformation='Logarithmic color. Exact zeros, if any, use the low color with an explicit 0 label. Gray padded rows are unavailable, not zeros.'),
        provenance=dict(experiment='EXP-516', source_commit=value['source_commit'],
            generator='scripts/render_exp516_ordinal_coverage.py', generator_sha256=screen.sha(Path(__file__)),
            matplotlib=matplotlib.__version__, outputs={stem+'.'+e:screen.sha(output/(stem+'.'+e)) for e in ('svg','pdf','png')}),
        plotted_data=data, interval_semantics='No statistical intervals or certified continuous event sheets.',
        exclusions=['No exact-flow root census', 'No new fold qualification', 'No verified Jones symbol or chain'],
        accessibility='Crosses, outlines, labels and gray missing cells supplement color.',
        guards=dict(public_replay=checked, cells=sum(len(p['cells']) for p in data),
                    zero_distances=sum(c['distance'] == 0 for p in data for c in p['cells'])))
    (output/(stem+'.receipt.json')).write_bytes(screen.encode(metadata))
    (output/(stem+'.index.json')).write_bytes(screen.encode(dict(receipts={stem+'.receipt.json':screen.sha(output/(stem+'.receipt.json'))})))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result', type=Path, required=True)
    p.add_argument('--expected-sha256', required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    a = p.parse_args()
    render(a.result, a.expected_sha256, a.output_dir)
