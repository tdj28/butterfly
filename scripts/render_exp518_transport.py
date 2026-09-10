#!/usr/bin/env python3
"""Plot measured fold transport and both distinct identity gates."""
import argparse
import io
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from butterfly._paired_startup import sha256, write_json
from scripts import verify_exp518_public_transport as public


def plot_data(saved, start):
    stages = [dict(id='start (EXP-517)', rows=start, parameters=public.run.model.matrix(start), decision=None)]
    for item in saved['result']['rows']:
        stages.append(dict(id=item['spec']['id'], rows=item['rows'], parameters=item['spec']['parameters'], decision=item['decision']))
    result = []
    for stage in stages:
        if public.run.model.matrix(stage['rows']) != stage['parameters']:
            raise ValueError('stage parameters differ')
        points = []
        for row in stage['rows']:
            c = row['candidate']
            qualified = bool(row['assessment'] and row['assessment']['qualified'])
            values = []
            if qualified:
                if [v['method'] for v in row['folds']] != public.run.model.METHODS:
                    raise ValueError('both solver profiles required')
                for profile in row['folds']:
                    obs = profile['qualification']['observations']
                    if len(obs) != 3:
                        raise ValueError('three local observations required')
                    coordinates = {key: obs[1][key][0] for key in ('image_state', 'next_state')}
                    if not all(math.isfinite(v) for v in coordinates.values()):
                        raise ValueError('finite measured coordinates required')
                    values.append(dict(method=profile['method'], **coordinates))
            points.append(dict(history=c['history'], direction=c['direction'], qualified=qualified, values=values))
        decision = stage['decision']
        ratios = None
        if decision is not None and decision['qualified']:
            ratios = dict(spread=decision['cross_history_spread']/1e-6, displacement=decision['adjacent_displacement']/.01)
            if any(not math.isfinite(v) or v < 0 for v in ratios.values()):
                raise ValueError('finite nonnegative gate ratios required')
        result.append(dict(id=stage['id'], c=stage['parameters']['c'], points=points, ratios=ratios,
            transport_qualified=None if decision is None else decision['transport_qualified']))
    return result


def endpoint_data(saved):
    endpoint = saved['endpoint_comparison']
    if endpoint is None:
        return []
    rows = endpoint['contact']['rows']
    cases = saved['result']['rows'][-1]['rows']
    if len(rows) != 4 or len(cases) != 4:
        raise ValueError('complete endpoint comparison required')
    result = []
    for row, case in zip(rows, cases, strict=True):
        c = case['candidate']
        if row['id'] != c['id'] or row['family_id'] != c['family_id']:
            raise ValueError('endpoint family identity differs')
        if [(v['method'], v['phase']) for v in row['variants']] != [
                ('DOP853', .25), ('DOP853', 1.25), ('Radau', .25), ('Radau', 1.25)]:
            raise ValueError('all paired solver/window variants required')
        for v in row['variants']:
            values = dict(x_ratio=v['pair_x_distance'][3]/1e-4, state_ratio=v['pair_state_distance'][3]/1e-4)
            if not all(math.isfinite(x) and x >= 0 for x in values.values()):
                raise ValueError('finite nonnegative endpoint distances required')
            result.append(dict(history=c['history'], direction=c['direction'], method=v['method'], phase=v['phase'], **values))
    return result


def render(receipt, expected_sha, output):
    checked = public.verify(receipt, expected_sha)
    saved = json.loads(receipt.read_bytes())
    data = plot_data(saved, public.run.inputs())
    contact = endpoint_data(saved)
    if output.exists():
        raise ValueError('fresh figure directory required')
    output.mkdir(parents=True)
    stem = 'EXP-518-recovered-fold-transport'
    plt.rcParams.update({'font.size': 13, 'svg.fonttype': 'none', 'svg.hashsalt': stem,
                        'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.7), layout='constrained')
    axes = axes.ravel()
    colors = ['#136b79', '#a74661', '#6955a1', '#ad6719']
    markers = ['o', 's', '^', 'D']
    for ax, key, title in zip(axes[:2], ['image_state', 'next_state'], ['Fold input', 'Next return'], strict=True):
        for case, (h, d) in enumerate(public.run.model.CASES):
            for method in public.run.model.METHODS:
                coords = [(s['c'], v[key]) for s in data for p in s['points']
                          if (p['history'], p['direction']) == (h, d) for v in p['values'] if v['method'] == method]
                if coords:
                    xs, ys = zip(*coords, strict=True)
                    ax.plot(xs, ys, color=colors[case], lw=.8, ls='-' if method == 'DOP853' else '--',
                        marker=markers[case], ms=4 if method == 'DOP853' else 7,
                        mfc=colors[case] if method == 'DOP853' else 'none')
        ax.set_title(title+' · measured x coordinate')
        ax.set_xlabel('c (a varies along the fixed path; b = 0.2)')
        ax.set_ylabel('x'); ax.invert_xaxis(); ax.grid(alpha=.15)
        ax.ticklabel_format(axis='y', style='plain', useOffset=False)
    ax = axes[2]
    ax.set_yscale('log'); ax.axhline(1., color='#a74661', ls='--', label='Acceptance limit')
    for i, stage in enumerate(data[1:]):
        if stage['ratios'] is None:
            ax.text(i, .5, 'Unqualified fold matrix', transform=ax.get_xaxis_transform(), ha='center', rotation=90)
        else:
            for shift, key, marker, color in [(-.08, 'spread', 'o', '#136b79'), (.08, 'displacement', 's', '#ad6719')]:
                value = stage['ratios'][key]
                ax.plot(i+shift, max(value, 1e-14), marker, color=color, label=key if i == 0 else None)
                ax.annotate(f'{value:.3g}', (i+shift, max(value, 1e-14)), xytext=(5, 5), textcoords='offset points', fontsize=11)
    ax.set_xticks(range(len(data)-1), [s['id'] for s in data[1:]])
    ax.set_xlim(-.5, max(.5, len(data)-1.5)); ax.set_ylim(bottom=1e-14, top=max(10., *[10*v for s in data if s['ratios'] for v in s['ratios'].values()]))
    ax.set_title('Two separate transport gates')
    ax.set_ylabel('Measured distance / its own threshold (log)')
    ax.grid(axis='y', alpha=.15); ax.legend(frameon=False, fontsize=12)
    ax = axes[3]
    ax.axhline(1., color='#a74661', ls='--')
    if contact:
        for key, marker, color, label in [('x_ratio', 'o', '#136b79', 'x projection only'),
                                          ('state_ratio', 's', '#a74661', 'Full input + output states')]:
            ax.plot(range(16), [r[key] for r in contact], ls='none', marker=marker, color=color, ms=5, label=label)
        ax.set_xticks([1.5, 5.5, 9.5, 13.5], [f'h{h}/d{d}' for h, d in public.run.model.CASES])
        ax.set_ylim(0, max(1.6, 1.2*max(r[k] for r in contact for k in ('x_ratio', 'state_ratio'))))
        ax.legend(frameon=False, fontsize=12, loc='lower center')
        ax.set_xlabel('Each group: both solvers and both repeat windows')
    else:
        ax.text(.5, .5, 'Endpoint comparison not eligible', transform=ax.transAxes, ha='center')
        ax.set_xticks([])
    ax.set_title('Endpoint cycle comparison · all 16 variants')
    ax.set_ylabel('Pair distance / 1e-4 (acceptance limit = 1)')
    ax.grid(axis='y', alpha=.15)
    handles = [plt.Line2D([], [], color=col, marker=marker, label=f'history {h}, direction {d}')
               for col, marker, (h, d) in zip(colors, markers, public.run.model.CASES, strict=True)]
    handles += [plt.Line2D([], [], color='#444444', marker='o', label='DOP853'),
                plt.Line2D([], [], color='#444444', marker='o', mfc='none', ls='--', label='Radau (open)')]
    fig.legend(handles=handles, loc='outside lower center', ncols=3, frameon=False, fontsize=12)
    status = '; '.join(f'{s["id"]}: {sum(p["qualified"] for p in s["points"])}/4 qualified' for s in data[1:])
    failures = [f'{s["id"]} h{p["history"]}/d{p["direction"]}' for s in data[1:] for p in s['points'] if not p['qualified']]
    unrun = [r['id'] for r in saved['result']['progress'] if r['status'] == 'not-run']
    endpoint_status = 'not evaluated' if not contact else ('passes' if saved['endpoint_comparison']['fold_proximity'] else 'FAILS')
    fig.suptitle('EXP-518 | Recovered fold transport; endpoint full-state contact '+endpoint_status+'\n'+status+(' · not run: '+', '.join(unrun) if unrun else '')+
        ('\nUnqualified: '+', '.join(failures) if failures else '')+
        '\nLines only join measured points; they do not prove continuous or unique continuation.', fontsize=14)
    svg = io.StringIO(); fig.savefig(svg, format='svg', metadata={'Date': None})
    (output/(stem+'.svg')).write_text('\n'.join(s.rstrip() for s in svg.getvalue().splitlines())+'\n')
    fig.savefig(output/(stem+'.pdf'), metadata={'CreationDate': None, 'ModDate': None})
    fig.savefig(output/(stem+'.png'), dpi=300); plt.close(fig)
    meta = dict(figure_id=stem, title='Recovered fold transport and identity gates',
        description='All four constructions and both solvers at every executed stage, both transport criteria, and all endpoint cycle-comparison variants.',
        alt_text='Top panels show measured fold input and next-return x against decreasing c; all four constructions and both solvers overlap closely. Bottom left shows the separate spread and displacement gates, normalized by their own thresholds. Bottom right shows every endpoint variant: the x projection passes, but full-state proximity fails. Failures and unrun stages remain explicit.',
        data_source=dict(artifact=str(receipt.resolve().relative_to(public.run.ROOT)), sha256=expected_sha,
            anchor=public.run.RECEIPT, anchor_sha256=public.run.INPUTS[public.run.RECEIPT],
            fields=['result.rows[].rows[].folds[].qualification.observations', 'result.rows[].decision', 'result.progress', 'endpoint_comparison.contact.rows[].variants'],
            selection='All four cases, both solvers, all executed stages; qualified coordinates only, with failure counts and unrun stages retained.',
            transformation='Measured center x coordinates; lines are visual guides only. Transport distances normalized by their distinct frozen thresholds; an exact zero ratio would be shown at the labeled 1e-14 display floor. Endpoint distances at frozen cycle index 3 normalized by 1e-4, both input/output states included.',
            aggregation='No averaging of solver/case coordinates or endpoint variants. Transport ratios use complete-matrix maxima already defined in the frozen decision.'),
        provenance=dict(experiment='EXP-518', source_commit=saved['source_commit'], generator='scripts/render_exp518_transport.py',
            generator_sha256=sha256(Path(__file__)), public_verifier='scripts/verify_exp518_public_transport.py',
            public_verifier_sha256=sha256(Path(public.__file__)), matplotlib=matplotlib.__version__,
            outputs={stem+'.'+e: sha256(output/(stem+'.'+e)) for e in ('svg', 'pdf', 'png')}),
        plotted_data=data, endpoint_variants=contact, unrun_stages=unrun, interval_semantics='No statistical interval, rigorous error bound or continuous-path guarantee.',
        exclusions=['Not a restored original eighth return', 'Not four independent folds', 'Not a C/D dictionary or verified Jones chain'],
        accessibility='Color, marker shape, line style and explicit text statuses.', guards=checked)
    write_json(output/(stem+'.receipt.json'), meta)
    write_json(output/(stem+'.index.json'), dict(receipts={stem+'.receipt.json': sha256(output/(stem+'.receipt.json'))}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args(); render(args.result, args.expected_sha256, args.output_dir)
