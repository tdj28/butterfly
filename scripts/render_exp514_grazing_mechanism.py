#!/usr/bin/env python3
"""Render audited local crossing birth/death with explicit normal-form scaling."""
import argparse
import io
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from butterfly._paired_startup import sha256, write_json
from scripts.verify_exp514_public_grazing import verify


def render(receipt, expected_sha, output):
    receipt = receipt.resolve()
    result = verify(receipt, expected_sha)
    saved = json.loads(receipt.read_bytes())
    if output.exists():
        raise ValueError('fresh figure output required')
    output.mkdir(parents=True)
    plt.rcParams.update({'font.size':10, 'axes.spines.top':False, 'axes.spines.right':False,
        'svg.fonttype':'none', 'svg.hashsalt':'EXP-514-grazing-mechanism'})
    fig, axes = plt.subplots(1, 5, figsize=(15, 4.5), layout='constrained', sharey=True)
    plotted = []
    for ax, row in zip(axes, saved['rows'], strict=True):
        c = row['candidate']
        ax.set_title(f'Direction {c["direction"]}, nodes {c["indices"]}\n'
                     f'{c["accepted_prefix"]} earlier return'+('' if c['accepted_prefix']==1 else 's'), fontsize=10)
        decision = row['decision']
        if decision['analysis'] is None or not decision['analysis']['solvers']:
            ax.text(.5, .5, 'No qualified\nroot/side analysis', ha='center', va='center', transform=ax.transAxes)
            plotted.append(dict(id=c['id'], qualified=False, points=[]))
            continue
        points = []
        for j, analysis in enumerate(decision['analysis']['solvers']):
            root = analysis['root']
            scale_u = max(map(abs, c['doses']))
            scale_t = np.sqrt(abs(2*root['jacobian'][0][0]*scale_u/root['jacobian'][1][1]))
            if not np.isfinite([scale_u, scale_t]).all() or min(scale_u, scale_t) <= 0:
                raise ValueError('finite nonzero normal-form scales required')
            if j == 0:
                sign = -np.sign(root['jacobian'][0][0]*root['jacobian'][1][1])
                x = sign*np.linspace(0, 1.05, 151)
                for branch in (-1, 1):
                    ax.plot(x, branch*np.sqrt(abs(x)), '--', color='#737373', lw=1,
                            label='Quadratic tangency guide' if branch==1 else None)
                ax.axvspan(min(-sign*1.12, 0), max(-sign*1.12, 0), color='#EEEEEE', alpha=.65)
                ax.text(-sign*.55, 0, 'No crossings\npredicted here', ha='center', va='center', fontsize=9, color='#555555')
            for side in analysis['sides']:
                for event in side['local_roots']:
                    x = (side['u']-root['u'])/scale_u
                    y = (event['time']-root['time'])/scale_t
                    points.append(dict(method=analysis['method'], nominal_dose=side['nominal_dose'],
                        accepted=event['accepted'], x=x, y=y, scale_u=scale_u, scale_t=float(scale_t)))
                    if j==0:
                        ax.scatter(x, y, s=62, marker='v' if event['accepted'] else '^',
                            color='#126B89' if event['accepted'] else '#B25E17', zorder=3,
                            label='Accepted crossing' if event['accepted'] else 'Opposite-direction crossing')
                    else:
                        ax.scatter(x, y, s=110, facecolors='none', edgecolors='#303030', marker='s', lw=.8,
                            label='Radau cross-check', zorder=4)
        plotted.append(dict(id=c['id'], qualified=decision['qualified'], points=points))
        if not decision['qualified']:
            ax.text(.5, .96, 'NOT QUALIFIED', color='#A51E2C', ha='center', va='top', transform=ax.transAxes)
        ax.axhline(0, lw=.6, color='#AAAAAA')
        ax.axvline(0, lw=.6, color='#AAAAAA')
        ax.set_xlim(-1.15, 1.15)
        ax.set_ylim(-1.25, 1.25)
        ax.set_xlabel('Scaled initial-curve offset')
        ax.grid(alpha=.12)
    axes[0].set_ylabel('Scaled crossing time relative to tangency')
    unique = {}
    for ax in axes:
        handles, labels = ax.get_legend_handles_labels()
        unique.update(zip(labels, handles, strict=True))
    fig.legend(unique.values(), unique.keys(), loc='outside lower center', ncols=4, frameon=False, fontsize=9)
    fig.suptitle(f'EXP-514 | A section tangency creates or removes a pair of crossings\n'
        f'{result["qualified"]}/5 intervals pass the full numerical grazing test; this is not a verified Jones symbolic arrow.',
        fontsize=13, fontweight='bold')
    stem = 'EXP-514-grazing-mechanism'
    svg = io.StringIO()
    fig.savefig(svg, format='svg', metadata={'Date':None})
    (output/(stem+'.svg')).write_text('\n'.join(s.rstrip() for s in svg.getvalue().splitlines())+'\n')
    fig.savefig(output/(stem+'.pdf'), metadata={'CreationDate':None, 'ModDate':None})
    fig.savefig(output/(stem+'.png'), dpi=300)
    plt.close(fig)
    metadata = dict(figure_id=stem, title='Section-grazing birth and death of crossings',
        description='All five candidate intervals, two solvers and four signed offsets. Measured crossing times compared with the local quadratic tangency guide.',
        alt_text='Five panels show a pair of section crossings on one side of each tangency and none on the other. Triangles distinguish accepted and opposite-direction crossings; open squares show Radau checks. Dashed curves are local quadratic guides, not additional trajectory observations.',
        data_source=dict(artifact=str(receipt.relative_to(Path(__file__).resolve().parents[1])), sha256=expected_sha,
            fields=['rows[].candidate', 'rows[].decision.analysis.solvers[].root', 'rows[].decision.analysis.solvers[].sides[].local_roots'],
            selection='All five candidates and every reported local root at all four prescribed offsets under both solvers.',
            exclusions='No candidate excluded; unqualified cases are explicitly labeled.', aggregation='None',
            transformation='x=(side_u-root_u)/max_abs_dose; y=(event_t-root_t)/sqrt(abs(2*h_u*max_abs_dose/h_tt)). Dashed guide y=+/-sqrt(abs(x)) on the predicted pair side.'),
        provenance=dict(experiment='EXP-514', audit_receipt_sha256=expected_sha,
            generator='scripts/render_exp514_grazing_mechanism.py', generator_sha256=sha256(Path(__file__)),
            matplotlib=matplotlib.__version__, source_commit=saved['source_commit'],
            outputs={stem+'.'+extension:sha256(output/(stem+'.'+extension)) for extension in ('svg','pdf','png')}),
        plotted_data=plotted, interval_semantics='No inferential intervals; points are fixed deterministic census observations.',
        exclusions=['Not an exact-flow proof', 'Not a global fold-absence proof', 'Not verification of Jones symbols or arrows', 'Dashed lines are a local normal-form guide, not integrated data'],
        accessibility='Triangle orientation distinguishes crossing direction; open squares distinguish Radau; panel titles identify every interval.',
        guards=dict(public_verifier=result, expected_candidates=5, all_candidates_present=len(plotted)==5, finite_scaling=True))
    write_json(output/(stem+'.receipt.json'), metadata)
    write_json(output/(stem+'.index.json'), dict(receipts={stem+'.receipt.json':sha256(output/(stem+'.receipt.json'))}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result', type=Path, required=True)
    p.add_argument('--expected-sha256', required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    a = p.parse_args()
    render(a.result, a.expected_sha256, a.output_dir)
