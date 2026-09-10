#!/usr/bin/env python3
"""Render audited finite samples; guide lines are not continuum enclosures."""
import argparse
import io
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scripts.verify_exp511_public_coverage import verify


def render(receipt,expected_sha,output):
    verify(receipt,expected_sha)
    saved = json.loads(receipt.read_bytes())
    if output.exists():
        raise ValueError('fresh figure directory required')
    output.mkdir(parents=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,
        'svg.fonttype':'none','svg.hashsalt':'EXP-511-curve-coverage'})
    fig,axes = plt.subplots(2,3,figsize=(14,8),layout='constrained')
    target = json.loads((Path(__file__).resolve().parents[1]/'experiments/manifests/EXP-511-direct-curve-coverage.json').read_bytes())['selection']['targets']
    for i,row in enumerate(saved['rows']):
        for method,color,marker in [('DOP853','#1768AC','o'),('Radau','#C45A19','x')]:
            values = []
            for sample in row['samples']:
                profile = next(p for p in sample['profiles'] if p['method']==method)
                if profile['status']=='completed' and 'image_state' in profile['measurement']['observation']:
                    o = profile['measurement']['observation']
                    values.append((sample['u'],o['image_state'][0],o['gain'],o['x_graph_slope'],sample['pair']['regular']))
            for col in (0,1):
                axes[i,col].scatter([v[0] for v in values],[v[col+1] for v in values],
                    c=color,marker=marker,s=28,label=method,alpha=.8)
            regular = [v for v in values if v[4]]
            axes[i,2].scatter([v[1] for v in regular],[v[3] for v in regular],c=color,marker=marker,s=28,label=method,alpha=.8)
            if method=='DOP853':
                irregular = [v for v in values if not v[4]]
                missing = [s['u'] for s in row['samples'] if s['u'] not in [v[0] for v in values]]
                for col in (0,1):
                    axes[i,col].scatter([v[0] for v in irregular],[v[col+1] for v in irregular],
                        facecolors='none',edgecolors='#B42336',marker='s',s=100,label='Unqualified pair')
                    axes[i,col].scatter(missing,[.025]*len(missing),transform=axes[i,col].get_xaxis_transform(),
                        color='#B42336',marker='|',s=100,label='Missing return prefix')
        for t in target:
            axes[i,0].axhline(t['image_state'][0],color='#2A8058',alpha=.25,lw=1)
            axes[i,2].axvline(t['image_state'][0],color='#2A8058',alpha=.25,lw=1)
        axes[i,0].plot([],[],color='#2A8058',label='Depth-4 fold x')
        axes[i,1].axhline(1e-4,color='#B42336',ls='--',lw=1,label='Minimum gain')
        axes[i,1].set_yscale('log')
        axes[i,2].axhline(0,color='#444444',lw=.8)
        axes[i,2].set_yscale('symlog',linthresh=.1)
        for col,ax in enumerate(axes[i]):
            ax.grid(alpha=.15)
            if col<2:
                left,right = row['candidate']['u_box']
                padding = .025*(right-left)
                ax.set_xlim(left-padding,right+padding)
            ax.set_xlabel('Initial curve coordinate u' if col<2 else 'Input return x')
            ax.set_ylabel(['Input return x','Scaled input tangent gain','Output / input x derivative'][col])
            ax.set_title(f'Direction {i}: '+['sampled coverage','input regularity','regular-pair slopes'][col],loc='left',fontweight='bold')
    labels = {}
    for ax in axes.flat:
        handles,names = ax.get_legend_handles_labels()
        labels.update(zip(names,handles,strict=True))
    fig.legend(labels.values(),labels.keys(),loc='outside lower center',ncols=6,fontsize=9,frameon=False)
    fig.suptitle('EXP-511 | Where do the long-history curves actually go?\n'
        'a = 0.21559488260076548, b = 0.2, c = 7.162\n'
        'Finite samples only; unsampled intervals remain uncertified.',fontsize=13,fontweight='bold')
    svg = io.StringIO()
    fig.savefig(svg,format='svg',metadata={'Date':None})
    (output/'exp511-curve-coverage.svg').write_text('\n'.join(line.rstrip() for line in svg.getvalue().splitlines())+'\n')
    fig.savefig(output/'exp511-curve-coverage.png',dpi=160)
    plt.close(fig)


if __name__=='__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result',type=Path,required=True)
    p.add_argument('--expected-sha256',required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    a = p.parse_args()
    render(a.result,a.expected_sha256,a.output_dir)
