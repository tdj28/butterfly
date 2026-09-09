#!/usr/bin/env python3
"""Show every measured continuation point and both full-state contact gaps."""
import argparse
import json
from pathlib import Path
import sys

from butterfly._paired_startup import sha256,write_json
from scripts import verify_exp504_public_contact as public

ROOT = public.run.ROOT
FIGURE = 'EXP-504-contact-path'


def derive(saved):
    start = public.run.inputs()['proposal']
    pairs = [(start,True,'EXP-503 start')]+[(r['point'],r['decision']['accepted'],r['decision']['reason'])
        for r in saved['result']['steps']]
    rows = []
    for number,(point,accepted,reason) in enumerate(pairs):
        contact = point['contact']
        boundaries = point['boundary_analysis'].get('cycle_indices',[])
        boundary = next((r for r in boundaries if r['index'] == 1),None)
        rows.append(dict(number=number,id=point['spec']['id'],parameters=point['spec']['parameters'],
            qualified=point['qualified'],accepted=accepted,reason=reason,
            fold_distance=None if contact is None else contact['envelope']['pair_state_distance'][3],
            boundary_distance=None if boundary is None or boundary['cells'] != 64 else float(boundary['maximum_distance']),
            joint_proximity=point['joint_proximity']))
    return rows


def draw(rows,analysis):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({'svg.hashsalt':FIGURE,'font.size':10,'axes.formatter.useoffset':False})
    fig,axes = plt.subplots(1,2,figsize=(11,6.2))
    fig.subplots_adjust(left=.09,right=.98,top=.79,bottom=.28,wspace=.35)
    left,right = axes
    c = [r['parameters']['c'] for r in rows]
    a = [r['parameters']['a'] for r in rows]
    left.plot(c,a,color='#aaaaaa',lw=1,zorder=1)
    for r in rows:
        color = '#0072b2' if r['accepted'] else '#b53a27'
        marker = '*' if r['number'] == 0 else ('o' if r['accepted'] else 'X')
        left.scatter(r['parameters']['c'],r['parameters']['a'],marker=marker,color=color,
            s=100 if r['number'] == 0 else 55,zorder=3)
        left.annotate(str(r['number']),(r['parameters']['c'],r['parameters']['a']),
            xytext=(5,5),textcoords='offset points',fontsize=9)
    left.margins(x=.17,y=.2)
    left.set_title('Measured path in parameter space',pad=12)
    left.set_xlabel('c  (continuation moves toward lower values)',labelpad=10)
    left.set_ylabel('a',labelpad=8)
    left.ticklabel_format(style='plain',axis='both',useOffset=False)
    for key,color,marker,label in [('fold_distance','#0072b2','o','Right-fold input + successor'),
            ('boundary_distance','#d55e00','s','Limiting-boundary predecessor')]:
        x = [r['number'] for r in rows if r[key] is not None]
        y = [r[key] for r in rows if r[key] is not None]
        right.plot(x,y,color=color,marker=marker,lw=1.2,label=label)
        for r in rows:
            if not r['accepted'] and r[key] is not None:
                right.scatter(r['number'],r[key],color='black',marker='x',s=75,zorder=4)
    right.axhline(1e-4,color='#555555',ls='--',lw=1,label='Required proximity: 0.0001')
    right.set_yscale('log')
    right.set_xticks([r['number'] for r in rows])
    right.set_title('Do both full-state gaps close?',pad=12)
    right.set_xlabel('Step number (0 is the EXP-503 starting point)',labelpad=10)
    right.set_ylabel('Worst distance over all representations',labelpad=8)
    right.legend(loc='best',fontsize=8,frameon=False)
    for ax in axes:
        ax.grid(alpha=.18)
        for side in ('top','right'):
            ax.spines[side].set_visible(False)
    fig.suptitle('Following the contact direction',fontsize=19,y=.98)
    subtitle = ('Both numerical proximity tests passed; symbolic chains remain unverified' if analysis['joint_proximity']
        else 'The complete bounded path has not established simultaneous contact')
    fig.text(.5,.90,subtitle,ha='center',fontsize=11)
    handles = [Line2D([],[],marker='*',color='#0072b2',ls='none',markersize=10,label='Starting point'),
        Line2D([],[],marker='o',color='#0072b2',ls='none',markersize=6,label='Accepted continuation step')]
    if any(not r['accepted'] for r in rows):
        handles.append(Line2D([],[],marker='X',color='#b53a27',ls='none',markersize=7,label='Rejected step (retained)'))
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,.14),ncol=3,frameon=False,fontsize=9)
    fig.text(.09,.098,'All measured points are shown. Connecting lines indicate step order, not computed intervening trajectories.',fontsize=9)
    fig.text(.09,.066,'Distances use the frozen state scaling and indices; they are numerical proximity tests, not exact-flow proofs.',fontsize=9)
    missing = [r['id'] for r in rows if r['fold_distance'] is None or r['boundary_distance'] is None]
    fig.text(.09,.034,'Warm numerical seeds; correlated representations are not independent replications.' if not missing
        else 'Incomplete distance summaries (not plotted): '+', '.join(missing),fontsize=9)
    return fig


def plot(source,expected_sha,output):
    checked = public.verify(source,expected_sha)
    saved = json.loads(source.read_bytes())
    rows = derive(saved)
    figure = draw(rows,saved['result']['analysis'])
    output.mkdir(parents=True,exist_ok=False)
    outputs = {}
    for suffix in ('svg','pdf','png'):
        path = output/(FIGURE+'.'+suffix)
        metadata = {'Date':None} if suffix == 'svg' else ({'CreationDate':None,'ModDate':None} if suffix == 'pdf' else None)
        figure.savefig(path,dpi=300,metadata=metadata)
        outputs[path.name] = dict(bytes=path.stat().st_size,sha256=sha256(path))
    import matplotlib
    from matplotlib import pyplot as plt
    plt.close(figure)
    bindings = {n:sha256(ROOT/n) for n in ['scripts/verify_exp504_public_contact.py',
        'scripts/exp504_continuation_model.py','scripts/run_exp504_guarded_contact.py',
        'experiments/manifests/EXP-504-guarded-contact-continuation.json']}
    receipt = dict(figure_id=FIGURE,title='Following the contact direction',
        description='All measured parameter points and both complete full-state proximity summaries.',
        alt_text='The left panel shows the parameter path, with a star at the starting point, numbered circles for accepted steps and crosses for rejected steps. The right panel shows worst fold and boundary distances on a logarithmic scale against the common proximity threshold.',
        data_source=dict(path=source.resolve().relative_to(ROOT).as_posix(),sha256=expected_sha,
            fields=['result.steps.point','result.steps.decision','EXP-503.proposal'],
            selection='Starting point and every completed measured step, including rejected points.',
            exclusions='Only missing complete distance summaries are unplotted, explicitly listed; no favorable point selection.',
            aggregation='Worst full-state distance over the complete correlated representation set.',
            transformation='Logarithmic distance axis; connecting lines show order only, without interpolation claims.'),
        provenance=dict(experiment_id='EXP-504',source_commit=saved['source_commit'],audit_receipt_sha256=expected_sha,
            generator_path=Path(__file__).resolve().relative_to(ROOT).as_posix(),generator_sha256=sha256(Path(__file__)),
            python=sys.version,matplotlib=matplotlib.__version__,outputs=outputs),bindings=bindings,
        derived_values=rows,hard_guards=checked,
        interval_semantics='Worst values over fixed correlated representations, not statistical uncertainty or absolute error bounds.',
        claim_exclusions=['No exact-flow proof','No C/D identification','No verified Jones arrow','Not a parameter-plane atlas'],
        accessibility=dict(non_color_channels='Numbers, stars, circles, squares and rejected-point crosses',png_dpi=300))
    path = output/(FIGURE+'.receipt.json')
    write_json(path,receipt)
    write_json(output/(FIGURE+'.index.json'),dict(figures=[dict(path=path.name,sha256=sha256(path))]))
    return receipt


def verify(output):
    path = output/(FIGURE+'.receipt.json')
    receipt = json.loads(path.read_bytes())
    index = json.loads((output/(FIGURE+'.index.json')).read_bytes())
    source = ROOT/receipt['data_source']['path']
    if (index != dict(figures=[dict(path=path.name,sha256=sha256(path))])
            or receipt['provenance']['generator_sha256'] != sha256(Path(__file__))
            or any(sha256(ROOT/n) != h for n,h in receipt['bindings'].items())
            or public.verify(source,receipt['data_source']['sha256']) != receipt['hard_guards']
            or derive(json.loads(source.read_bytes())) != receipt['derived_values']
            or any(sha256(output/n) != r['sha256'] or (output/n).stat().st_size != r['bytes']
                for n,r in receipt['provenance']['outputs'].items())):
        raise ValueError('figure source, derived data or output drift')
    return dict(passed=True,figure_id=FIGURE,source_sha256=receipt['data_source']['sha256'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt',type=Path)
    parser.add_argument('--expected-sha256')
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--verify-only',action='store_true')
    a = parser.parse_args()
    if not a.verify_only:
        if not a.receipt or not a.expected_sha256:
            parser.error('audited receipt and hash required')
        plot(a.receipt,a.expected_sha256,a.output_dir)
    print(json.dumps(verify(a.output_dir)))


if __name__ == '__main__':
    main()
