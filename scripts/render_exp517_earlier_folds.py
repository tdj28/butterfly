#!/usr/bin/env python3
"""Local return samples and fold approximations; retain failures."""
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
from scripts import verify_exp517_public_folds as public


def plot_data(saved):
    rows=saved['rows']
    if [(r['candidate']['history'],r['candidate']['direction']) for r in rows]!=[(4,0),(4,1),(7,0),(7,1)]:
        raise ValueError('complete four-representation figure required')
    result=[]
    for row in rows:
        assessment=row['assessment']
        qualified=bool(assessment and assessment['qualified'])
        restored=bool(assessment and assessment['reference_restored'])
        if restored and not qualified:
            raise ValueError('an unqualified fold cannot restore its reference')
        curves=[]
        failure=[]
        worst=None
        if qualified:
            if [p['method'] for p in row['folds']]!=['DOP853','Radau']:
                raise ValueError('both solver profiles required')
            for p in row['folds']:
                q=p['qualification']
                observations=q['observations']
                if len(observations)!=3 or [v['offset'] for v in p['censuses']]!=[-1e-6,0.,1e-6]:
                    raise ValueError('complete three-offset local samples required')
                x0,y0=[observations[1][k][0] for k in ('image_state','next_state')]
                xs=[(o['image_state'][0]-x0)/15*1e5 for o in observations]
                ys=[(o['next_state'][0]-y0)/15*1e9 for o in observations]
                k=q['scaled_curvature']
                slope=observations[1]['x_graph_slope']
                if not all(math.isfinite(v) for v in [*xs,*ys,k,slope]) or not min(xs)<0<max(xs) or k==0:
                    raise ValueError('finite nondegenerate local prediction required')
                curves.append(dict(method=p['method'],input_center=x0,output_center=y0,
                    x_plot=xs,y_plot=ys,scaled_curvature=k,center_slope=slope,offsets=[-1e-6,0.,1e-6]))
            distances=assessment['reference_distances']
            if len(distances)!=8:
                raise ValueError('both solvers and every reference required')
            values=[r[k] for r in distances for k in ('image_state','next_state')]
            if any(not math.isfinite(v) or v<0 for v in values):
                raise ValueError('finite nonnegative reference distance required')
            worst=max(values)
        elif row['folds'] is not None:
            failure=[dict(method=p['method'],shooting=p['shooting']['reason'],
                          qualification=p['qualification'].get('reason','failed complete comparison')) for p in row['folds']]
        else:
            failure=[dict(status=row['status'])]
        result.append(dict(id=row['candidate']['id'],history=row['candidate']['history'],
            direction=row['candidate']['direction'],qualified=qualified,restored=restored,
            curves=curves,worst_reference_distance=worst,failure=failure))
    return result


def render(receipt,expected_sha,output):
    checked=public.verify(receipt,expected_sha)
    saved=json.loads(receipt.read_bytes())
    data=plot_data(saved)
    if output.exists():raise ValueError('fresh figure output required')
    output.mkdir(parents=True)
    stem='EXP-517-earlier-return-folds'
    plt.rcParams.update({'font.size':10,'svg.fonttype':'none','svg.hashsalt':stem,
        'axes.spines.top':False,'axes.spines.right':False})
    fig=plt.figure(figsize=(13,7.4),layout='constrained')
    grid=fig.add_gridspec(2,3,width_ratios=[1,1,.95])
    styles={'DOP853':dict(color='#136b79',marker='o',ls='-'),
            'Radau':dict(color='#a74661',marker='s',ls='--')}
    for index,row in enumerate(data):
        ax=fig.add_subplot(grid[index//2,index%2])
        ax.set_title(f'History {row["history"]} · direction {row["direction"]}\n'
            +('Local fold qualified' if row['qualified'] else 'Unqualified — retained'),fontsize=11)
        if row['qualified']:
            for curve in row['curves']:
                style=styles[curve['method']]
                x=np.linspace(min(curve['x_plot']),max(curve['x_plot']),201)
                y=(curve['center_slope']*(x/1e5)+.5*curve['scaled_curvature']*(x/1e5)**2)*1e9
                ax.plot(x,y,color=style['color'],ls=style['ls'],lw=1.1)
                ax.plot(curve['x_plot'],curve['y_plot'],ls='none',marker=style['marker'],
                    ms=7 if curve['method']=='Radau' else 4.5,mfc='none' if curve['method']=='Radau' else style['color'],
                    color=style['color'])
            ax.axhline(0,color='#999999',lw=.5)
            ax.axvline(0,color='#999999',lw=.5)
            ax.grid(alpha=.15)
            ax.set_xlabel('Input Δx / 15 × 10⁵ (centered per solver)')
            ax.set_ylabel('Output Δx / 15 × 10⁹')
        else:
            ax.text(.5,.5,'\n'.join(str(f.get('shooting',f.get('status','unresolved'))) for f in row['failure']),
                    transform=ax.transAxes,ha='center',va='center',wrap=True)
            ax.set_xticks([]);ax.set_yticks([])
    comparison=fig.add_subplot(grid[:,2])
    distances=[r['worst_reference_distance'] for r in data if r['worst_reference_distance'] is not None]
    positives=[v for v in distances if v>0]
    low=min([1e-7,*[v/3 for v in positives]])
    high=max([1e-5,*[v*3 for v in positives]])
    comparison.set_xscale('log');comparison.set_xlim(low,high)
    comparison.axvline(1e-6,color='#ab3848',ls='--',lw=1.2)
    comparison.set_yticks(range(4),[f'h{r["history"]} / d{r["direction"]}' for r in data])
    comparison.set_ylim(3.7,-.7)
    for i,row in enumerate(data):
        d=row['worst_reference_distance']
        if d is None:
            comparison.text(.05,i,'unqualified',transform=comparison.get_yaxis_transform(),color='#a33c50')
        else:
            color='#136b79' if row['restored'] else '#a33c50'
            comparison.plot(d if d else low,i,'o',color=color)
            comparison.annotate(f'{d:.3g}' if d else '0 (margin)',(d if d else low,i),
                xytext=(0,12),textcoords='offset points',ha='center',fontsize=9,color=color)
    comparison.grid(axis='x',alpha=.17)
    comparison.set_title('Full-state calibration check\nWorst of all solver/reference pairs',fontsize=11)
    comparison.set_xlabel('Scaled max distance (log)\nDashed line: unchanged 1e-6 threshold')
    handles=[plt.Line2D([],[],color=st['color'],marker=st['marker'],ls=st['ls'],
                       mfc='none' if method=='Radau' else st['color'],label=method) for method,st in styles.items()]
    fig.legend(handles=handles,loc='outside lower center',ncols=2,frameon=False)
    fig.suptitle(f'EXP-517 | {sum(r["qualified"] for r in data)}/4 local folds qualify; '
        f'{sum(r["restored"] for r in data)}/4 match every reference\n'
        'Dots: computed return samples. Curves: local fold approximations, not extra trajectories.',
        fontsize=13,fontweight='bold')
    svg=io.StringIO();fig.savefig(svg,format='svg',metadata={'Date':None})
    (output/(stem+'.svg')).write_text('\n'.join(s.rstrip() for s in svg.getvalue().splitlines())+'\n')
    fig.savefig(output/(stem+'.pdf'),metadata={'CreationDate':None,'ModDate':None})
    fig.savefig(output/(stem+'.png'),dpi=300);plt.close(fig)
    metadata=dict(figure_id=stem,title='Earlier-return fold recovery and full-state calibration',
        description='Every history/direction case, both solvers, local computed samples and all-reference errors.',
        alt_text='Four local panels compare three return samples with a local fold approximation. A right-hand panel compares worst full-state reference errors with the unchanged threshold. Failed cases, if any, are explicitly labeled.',
        data_source=dict(artifact=str(receipt.resolve().relative_to(public.run.ROOT)),sha256=expected_sha,
            fields=['rows[].folds[].qualification.observations','rows[].folds[].qualification.scaled_curvature','rows[].assessment.reference_distances'],
            selection='All four representations; every qualified profile uses all three prescribed offset samples; failures retained as text.',
            exclusions='No candidate excluded. Midpoint and Newton trace details remain in the receipt rather than the local-shape panels.',
            aggregation='Reference panel takes the maximum across both state endpoints, both solvers and all four reference states.',
            transformation='Per-solver centering of x coordinates; dimensionless local input scaled by 1e5 and output by 1e9. Lines use the measured center slope (not forced to zero) and variational fold-limit curvature only over the sampled span. At a finite root residual this is a fold approximation, not an exact Taylor coefficient of the x graph or a rigorous remainder bound. Center agreement is checked separately in full state.'),
        provenance=dict(experiment='EXP-517',source_commit=saved['source_commit'],
            generator='scripts/render_exp517_earlier_folds.py',generator_sha256=sha256(Path(__file__)),
            public_verifier='scripts/verify_exp517_public_folds.py',public_verifier_sha256=sha256(Path(public.__file__)),
            matplotlib=matplotlib.__version__,outputs={stem+'.'+e:sha256(output/(stem+'.'+e)) for e in ('svg','pdf','png')}),
        plotted_data=data,interval_semantics='Deterministic numerical comparisons, no statistical error bars or rigorous flow enclosure.',
        exclusions=['Not a restored original eighth-return representation','Not an independent generating partition','Not a verified Jones symbolic chain'],
        accessibility='Distinct markers/line styles and textual failures supplement color.',
        guards=dict(public_replay=checked,representations=4,computed_local_points=sum(3*len(r['curves']) for r in data)))
    write_json(output/(stem+'.receipt.json'),metadata)
    write_json(output/(stem+'.index.json'),dict(receipts={stem+'.receipt.json':sha256(output/(stem+'.receipt.json'))}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result',type=Path,required=True)
    p.add_argument('--expected-sha256',required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args();render(a.result,a.expected_sha256,a.output_dir)
