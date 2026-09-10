#!/usr/bin/env python3
"""Data-bound fresh-response and full-state-contact figure; no target solves."""
import argparse
import io
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from butterfly._paired_startup import sha256, write_json
from scripts import verify_exp519_public_response as public

STEM = 'EXP-519-fixed-c-fold-response'
RADIUS = 1e-4


def point_data(saved, source):
    points = [dict(spec=dict(id='anchor', parameters=source['anchor']), qualified=True, vectors=source['anchor_vectors'])]
    points += saved['result']['points']
    if saved['result']['correction'] is not None:
        points += [saved['result']['correction']]
    result = []
    for point in points:
        par = point['spec']['parameters']
        if any(par[k] != source['anchor'][k] for k in ('b', 'c')):
            raise ValueError('fixed b/c figure required')
        row = dict(id=point['spec']['id'], parameters=par, normalized_a=(par['a']-source['anchor']['a'])/1e-5,
                   qualified=point['qualified'], vectors=point['vectors'], signed_x=None, x_distance=None,
                   full_distance=None, component_maximum=None)
        if point['qualified']:
            values = public.run.model.values(point['vectors'])
            row.update(signed_x=values[:, 0].tolist(),
                x_distance=np.max(np.abs(values[:, [0, 3]]), axis=1).tolist(),
                full_distance=np.max(np.abs(values), axis=1).tolist(),
                component_maximum=np.max(np.abs(values), axis=0).tolist())
        elif point['vectors'] is not None:
            raise ValueError('unqualified point cannot supply qualified residuals')
        result.append(row)
    return result


def response_data(saved):
    rows = saved['result']['response']['variants']
    if not rows:
        return []
    if [r['key'] for r in rows] != public.run.model.KEYS:
        raise ValueError('complete response figure keys required')
    return [dict(history=h, direction=d,
                 variants=[r for r in rows if r['key'][:2] == [h, d]],
                 maximum_x_error=max(r['x_relative_error'] for r in rows if r['key'][:2] == [h, d]),
                 maximum_full_error=max(r['full_relative_error'] for r in rows if r['key'][:2] == [h, d]))
            for h, d in public.run.model.folds.CASES]


def render(receipt, expected_sha, output):
    checked = public.verify(receipt, expected_sha)
    saved = json.loads(receipt.read_bytes()); source = public.run.inputs()
    points, response = point_data(saved, source), response_data(saved)
    if output.exists():
        raise ValueError('fresh figure output required')
    output.mkdir(parents=True)
    plt.rcParams.update({'font.size': 12, 'svg.fonttype': 'none', 'svg.hashsalt': STEM,
                        'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5), layout='constrained')
    ax1, ax2, ax3, ax4 = axes.ravel()
    colors = dict(anchor='#626b73', stencil='#137b88', correction='#bd631c')
    used = set()
    for row in points:
        kind = row['id'] if row['id'] in ('anchor', 'correction') else 'stencil'
        label = dict(anchor='Reused EXP-518 anchor', stencil='Fresh stencil', correction='Single correction')[kind]
        marker = dict(anchor='s', stencil='o', correction='D')[kind]; x = row['normalized_a']
        if not row['qualified']:
            for ax in (ax1, ax2):
                ax.plot(x, .04, marker='x', color='#9e3547', transform=ax.get_xaxis_transform())
                ax.text(x, .08, 'unqualified', transform=ax.get_xaxis_transform(), ha='center', fontsize=8, rotation=90)
            continue
        for ax, key in ((ax1, 'signed_x'), (ax2, 'full_distance')):
            values = [v/RADIUS for v in row[key]]
            center = math.fsum(values)/16; lower, upper = min(values), max(values)
            if ax is ax2:
                center, lower, upper = [max(v, 1e-12) for v in (center, lower, upper)]
            ax.errorbar(x, center, yerr=[[max(0., center-lower)], [max(0., upper-center)]],
                fmt=marker, color=colors[kind], capsize=4, markersize=7, markeredgecolor='white',
                label=label if kind not in used else None, zorder=4)
        used.add(kind)
    linear = None
    if saved['result']['response']['qualified']:
        f = math.fsum(points[0]['signed_x'])/16
        j = math.fsum(r['fine'][0] for r in saved['result']['response']['variants'])/16
        linear = dict(normalized_a=[-1., 1.], signed_x=[f-j, f+j])
        ax1.plot(linear['normalized_a'], np.asarray(linear['signed_x'])/RADIUS, '--', color='#809a9c', lw=1.2,
                 label='Fine-stencil linear model')
    ax1.axhline(0., color='#899096', lw=.8)
    ax1.set_title('A  Signed x residual')
    ax1.set_ylabel('Signed input x residual / tolerance')
    ax1.legend(fontsize=9, loc='best')
    ax2.set_title('B  Full-state fold/orbit separation')
    ax2.set_yscale('log'); ax2.axhline(1., color='#9e3547', ls='--', lw=1.1, label='Acceptance limit')
    ax2.set_ylabel('Full-state distance / tolerance')
    ax2.legend(fontsize=9, loc='best')
    for ax in (ax1, ax2):
        ax.set_xlabel(r'Change in a from anchor / $10^{-5}$'); ax.grid(alpha=.15)
    ax3.set_title('C  Fresh derivative consistency')
    if response:
        for i, row in enumerate(response):
            for offset, key, label, color in [(-.16, 'maximum_x_error', 'x response', '#137b88'),
                                              (.16, 'maximum_full_error', 'Full six-component response', '#786097')]:
                ax3.bar(i+offset, max(row[key]/.05, 1e-12), width=.28, color=color,
                        hatch='///' if key == 'maximum_full_error' else None,
                        edgecolor='white', label=label if i == 0 else None)
        ax3.set_xticks(range(4), [f'h{r["history"]}, d{r["direction"]}' for r in response])
        ax3.set_xlabel('Fold construction (maximum over both solvers/windows)')
        ax3.legend(fontsize=9)
    else:
        ax3.text(.5, .45, 'No qualified stencil matrix', transform=ax3.transAxes, ha='center')
    ax3.axhline(1., color='#9e3547', ls='--', lw=1.1)
    ax3.set_ylabel('Coarse/fine relative error / 5% limit')
    ax3.text(.02, .90, 'Response '+('qualified' if saved['result']['response']['qualified'] else 'NOT qualified'),
             transform=ax3.transAxes, va='top', fontsize=10)
    ax4.set_title('D  Which full-state coordinates matter?')
    before = points[0]['component_maximum']; after = next((p for p in points if p['id'] == 'correction'), None)
    valid_after = after is not None and after['qualified']
    xs = np.arange(6)
    ax4.bar(xs-.16 if valid_after else xs, np.asarray(before)/RADIUS, width=.30 if valid_after else .5,
            color=colors['anchor'], label='Reused anchor')
    if valid_after:
        ax4.bar(xs+.16, np.asarray(after['component_maximum'])/RADIUS, width=.30,
                color=colors['correction'], hatch='///', edgecolor='white', label='Single correction')
    else:
        ax4.text(.02, .97, 'Correction '+('not run' if after is None else 'unqualified'),
                 transform=ax4.transAxes, va='top', fontsize=10)
    ax4.axhline(1., color='#9e3547', ls='--', lw=1.1)
    ax4.set_xticks(xs, ['input x', 'input y', 'input z', 'next x', 'next y', 'next z'], rotation=25, ha='right')
    ax4.set_ylabel('Maximum component distance / tolerance'); ax4.legend(fontsize=9)
    for ax in (ax3, ax4):
        ax.set_ylim(0., max(1.25, ax.get_ylim()[1]*1.15)); ax.grid(axis='y', alpha=.15)
    if response:
        smallest = min(max(r[key]/.05, 1e-12) for r in response
                       for key in ('maximum_x_error', 'maximum_full_error'))
        ax3.set_yscale('log')
        ax3.set_ylim(min(1., smallest)/3, max(1.25, ax3.get_ylim()[1]))
    fig.suptitle('A fresh response test of fold/orbit contact', fontsize=17)
    files = {}
    for extension in ('svg', 'pdf', 'png'):
        buffer = io.BytesIO()
        metadata = {'Date': None} if extension == 'svg' else ({'CreationDate': None, 'ModDate': None} if extension == 'pdf' else {})
        fig.savefig(buffer, format=extension, dpi=300, metadata=metadata)
        path = output/(STEM+'.'+extension); path.write_bytes(buffer.getvalue())
        files[path.name] = dict(sha256=sha256(path), bytes=path.stat().st_size)
    plt.close(fig)
    record = dict(figure_id='EXP-519-response', title='Fresh fixed-c fold response and full-state contact',
        description='Four fixed a perturbations test fresh derivatives; at most one prescribed correction is compared with the reused anchor that failed full-state contact.',
        alt_text='Four panels show signed x residual, full-state separation, coarse-versus-fine derivative agreement, and input/next-return component distances. Every qualified point includes all sixteen construction/solver/window variants; missing qualification is marked rather than plotted as zero.',
        data_source=dict(path=receipt.resolve().relative_to(public.run.ROOT).as_posix(), sha256=expected_sha,
            fields=['result.points', 'result.response', 'result.correction', 'result.decision'],
            anchor_receipt=public.run.RECEIPT, anchor_sha256=public.run.INPUTS[public.run.RECEIPT],
            selection='Complete frozen points and all sixteen variants; anchor reused explicitly; no favorable-point selection.',
            transformation='Parameter shift divided by 1e-5; distances divided by 1e-4; response errors divided by .05. Log-panel distances and response errors below 1e-12 after normalization are displayed at 1e-12, without changing stored values.'),
        provenance=dict(experiment_id='EXP-519', source_commit=saved['source_commit'],
            generator='scripts/render_exp519_response.py', generator_sha256=sha256(Path(__file__)),
            verifier='scripts/verify_exp519_public_response.py', verifier_sha256=sha256(Path(public.__file__)),
            matplotlib=matplotlib.__version__, audit=checked, outputs=files),
        plotted_data=dict(points=points, response=response, linear_prediction=linear),
        interval_semantics='Means with complete min/max variant ranges; not confidence intervals or independent replications. Construction bars use worst-case solver/window errors.',
        accessibility='Panels and axes labelled; anchor square, stencil circles, correction diamond; paired bar categories use hatching as well as color and position; categories have legends; acceptance limits are dashed. Coincident variants are explicitly represented by ranges.',
        claim_scope='Numerical local contact/response only. No second critical point, C/D dictionary, symbolic arrow, continuous-flow proof or boundary contact.',
        guards=dict(complete_variant_keys=True, fixed_b_c=True, audited_receipt=True, missing_points_not_zero=True))
    receipt_path = output/(STEM+'.receipt.json'); write_json(receipt_path, record)
    write_json(output/(STEM+'.index.json'), dict(figure_id=record['figure_id'], receipts={receipt_path.name: sha256(receipt_path)}))
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result', type=Path, required=True); parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    a = parser.parse_args(); render(a.result, a.expected_sha256, a.output_dir)
