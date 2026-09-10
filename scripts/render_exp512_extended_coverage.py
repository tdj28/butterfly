#!/usr/bin/env python3
"""Show new observations and endpoint brackets without drawing a continuous map."""
import argparse
import io
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.verify_exp512_public_extension import verify


def render(receipt,expected_sha,output):
    verify(receipt,expected_sha)
    saved = json.loads(receipt.read_bytes())
    if output.exists():
        raise ValueError('fresh figure directory required')
    output.mkdir(parents=True)
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,
        'svg.fonttype':'none','svg.hashsalt':'EXP-512-extended-coverage'})
    fig,axes = plt.subplots(2,2,figsize=(12,8),layout='constrained')
    extended = {(r['curve'],r['node']) for r in saved['extensions']}
    for i,row in enumerate(saved['result']['rows']):
        for method,color,marker in [('DOP853','#1768AC','o'),('Radau','#C45A19','x')]:
            for j,sample in enumerate(row['samples']):
                profile = next(p for p in sample['profiles'] if p['method']==method)
                if profile['status']!='completed':
                    continue
                o = profile['measurement']['observation']
                if 'image_state' not in o:
                    continue
                axes[i,0].scatter(sample['u'],o['image_state'][0],c=color,marker=marker,s=30,label=method)
                if sample['pair']['regular']:
                    axes[i,1].scatter(sample['u'],o['x_graph_slope'],c=color,marker=marker,s=30,label=method)
                if method=='DOP853' and (i,j) in extended:
                    for col,value in [(0,o['image_state'][0]),(1,o['x_graph_slope'])]:
                        if value is not None:
                            axes[i,col].scatter(sample['u'],value,facecolors='none',edgecolors='#8B6508',marker='D',s=95,label='New extended sample')
                if method=='DOP853' and not sample['pair']['regular']:
                    axes[i,0].scatter(sample['u'],o['image_state'][0],facecolors='none',edgecolors='#B42336',marker='s',s=100,label='Still unqualified')
        for left,right in row['analysis']['matched_candidate_brackets']:
            for ax in axes[i]:
                ax.axvspan(row['samples'][left]['u'],row['samples'][right]['u'],color='#E5B94C',alpha=.18,label='Candidate interval only')
        axes[i,1].axhline(0,color='#444444',lw=.8)
        for col,ax in enumerate(axes[i]):
            left,right = row['candidate']['u_box']
            ax.set_xlim(left-.001,right+.001)
            ax.grid(alpha=.15)
            ax.set_xlabel('Initial curve coordinate u')
            ax.set_ylabel('Input return x' if col==0 else 'Output / input x derivative')
            ax.set_title(f'Direction {i}: '+('all observed input states' if col==0 else 'regular-pair slopes'),loc='left',fontweight='bold')
    unique = {}
    for ax in axes.flat:
        handles,labels = ax.get_legend_handles_labels()
        unique.update(zip(labels,handles,strict=True))
    fig.legend(unique.values(),unique.keys(),loc='outside lower center',ncols=5,frameon=False,fontsize=9)
    par = saved['result']['rows'][0]['candidate']['parameters']
    fig.suptitle('EXP-512 | Longer observation exposes five candidate brackets\n'
        f'a = {par["a"]:.8f}, b = {par["b"]:g}, c = {par["c"]:.3f} | 38/40 pairs now regular\n'
        'Shaded intervals are not verified folds or certified continuous return domains.',fontsize=13,fontweight='bold')
    svg = io.StringIO()
    fig.savefig(svg,format='svg',metadata={'Date':None})
    (output/'exp512-extended-coverage.svg').write_text('\n'.join(v.rstrip() for v in svg.getvalue().splitlines())+'\n')
    fig.savefig(output/'exp512-extended-coverage.png',dpi=160)
    plt.close(fig)


if __name__=='__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result',type=Path,required=True)
    p.add_argument('--expected-sha256',required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    a = p.parse_args()
    render(a.result,a.expected_sha256,a.output_dir)
