#!/usr/bin/env python3
"""Plot every saved/new tangent norm at the three prescribed return ordinals."""
import argparse
from decimal import localcontext
import io
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from butterfly._paired_startup import sha256, write_json
from scripts.verify_exp515_public_precision import verify
from scripts import run_exp515_third_return_precision as run


def plot_data(saved, plan):
    result = []
    with localcontext() as ctx:
        ctx.prec = 70
        for row, case in zip(saved['rows'], plan['cases'], strict=True):
            curves = [dict(method=p['configuration'], norms=[m['scaled_norm'] for m in p['measures']]) for p in row['profiles']]
            curves += [dict(method=h['method'], norms=[str(run.model.norm(e['tangent'])) for e in h['events']]) for h in case['historical']]
            if len(curves) != 4 or any(len(c['norms']) != 3 for c in curves):
                raise ValueError('complete four-method/three-return plot matrix required')
            if any(not 0 < float(v) < float('inf') for c in curves for v in c['norms']):
                raise ValueError('nonpositive/nonfinite norms require a separately labeled figure design')
            result.append(dict(id=case['id'], direction=case['direction'], node=case['node'], curves=curves))
    return result


def render(receipt, expected_sha, output):
    check = verify(receipt, expected_sha)
    if (check['resolved_return_comparisons'], check['distinct_failed_historical_vectors'],
            check['failed_historical_comparisons']) != (18, 4, 8):
        raise ValueError('this result-specific headline requires the complete audited outcome')
    saved = json.loads(receipt.read_bytes())
    data = plot_data(saved, run.load())
    if output.exists():
        raise ValueError('fresh figure output required')
    output.mkdir(parents=True)
    stem = 'EXP-515-third-return-precision'
    plt.rcParams.update({'font.size':10, 'svg.fonttype':'none', 'svg.hashsalt':stem,
                         'axes.spines.top':False, 'axes.spines.right':False})
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), layout='constrained', sharex=True, sharey=True)
    styles = {'decimal-40':dict(color='#146B82', marker='o', ms=5, lw=1.4),
              'decimal-50':dict(color='#123844', marker='s', ms=8, mfc='none', lw=.8, ls='--'),
              'DOP853':dict(color='#C56A16', marker='^', ms=5, lw=1, ls=':'),
              'Radau':dict(color='#A33C50', marker='x', ms=6, lw=1, ls='-.')}
    titles = {8:'left neighbor', 9:'center', 10:'right neighbor'}
    for ax, row in zip(axes.flat, data, strict=True):
        for curve in row['curves']:
            ax.plot([1, 2, 3], list(map(float, curve['norms'])), label=curve['method'], **styles[curve['method']])
        ax.set_yscale('log')
        ax.set_ylim(3e-14, 3e4)
        ax.set_xticks([1, 2, 3])
        ax.set_xlim(.85, 3.15)
        ax.set_title(f'Direction {row["direction"]} · {titles[row["node"]]}')
        ax.grid(axis='y', alpha=.17)
        if row['node'] == 9:
            ax.annotate('Binary64 estimates\nmiss this small tangent',
                xy=(3, float(row['curves'][2]['norms'][2])), xytext=(1.08, 1e-6),
                fontsize=9, arrowprops=dict(arrowstyle='->', color='#555555'), color='#444444')
    for ax in axes[:, 0]:
        ax.set_ylabel('Scaled transverse sensitivity (log scale)')
    for ax in axes[1]:
        ax.set_xlabel('Accepted return number')
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='outside lower center', ncols=4, frameon=False)
    fig.suptitle('EXP-515 | Extremely weak sensitivity survives higher precision\n'
        '40- and 50-digit profiles agree; the center values are not resolved by the old binary64 estimates.',
        fontsize=13, fontweight='bold')
    svg = io.StringIO()
    fig.savefig(svg, format='svg', metadata={'Date':None})
    (output/(stem+'.svg')).write_text('\n'.join(s.rstrip() for s in svg.getvalue().splitlines())+'\n')
    fig.savefig(output/(stem+'.pdf'), metadata={'CreationDate':None, 'ModDate':None})
    fig.savefig(output/(stem+'.png'), dpi=300)
    plt.close(fig)
    metadata = dict(figure_id=stem, title='Sensitivity through the first three returns',
        description='All six inputs and all four numerical profiles, retaining the neighboring controls and both centers.',
        alt_text='Six panels show the transverse tangent norm at returns one, two and three. All methods agree at the first two returns and at neighboring inputs. At both centers, the higher-precision third-return norm is near 1e-13, while the old binary64 values are near 1e-12. The two higher-precision profiles overlap.',
        data_source=dict(artifact=str(receipt.resolve().relative_to(run.ROOT)), sha256=expected_sha,
            additional_inputs=run.INPUTS, fields=['rows[].profiles[].measures[].scaled_norm', 'plan.cases[].historical[].events[].tangent'],
            selection='Every six-input/four-profile/three-return cell: 72 norm observations.', exclusions='None',
            aggregation='None; both higher-precision profiles remain plotted even when they overlap.',
            transformation='Euclidean norm of tangent divided componentwise by [15,15,.01]; logarithmic y axis. Connecting lines guide the eye, not samples between return events.'),
        provenance=dict(experiment='EXP-515', source_commit=saved['source_commit'], audit_receipt_sha256=expected_sha,
            generator='scripts/render_exp515_precision_comparison.py', generator_sha256=sha256(Path(__file__)),
            matplotlib=matplotlib.__version__, outputs={stem+'.'+e:sha256(output/(stem+'.'+e)) for e in ('svg','pdf','png')}),
        plotted_data=data, interval_semantics='No inferential error bars; fixed deterministic numerical observations. Root-box diagnostics are in the audit receipt, not global ODE error bounds.',
        exclusions=['Not an exact-flow proof', 'Not a newly qualified depth-eight fold', 'Not a verified Jones symbol or arrow', 'No independence claim for repeated numerical comparisons'],
        accessibility='Distinct marker shapes and line styles supplement color; panels label direction and center/neighbor identity.',
        guards=dict(public_replay=check, observations=72, all_values_finite_positive=True, no_exclusions=True))
    write_json(output/(stem+'.receipt.json'), metadata)
    write_json(output/(stem+'.index.json'), dict(receipts={stem+'.receipt.json':sha256(output/(stem+'.receipt.json'))}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result', type=Path, required=True)
    p.add_argument('--expected-sha256', required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    a = p.parse_args()
    render(a.result, a.expected_sha256, a.output_dir)
