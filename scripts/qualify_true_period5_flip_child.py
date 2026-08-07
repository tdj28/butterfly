#!/usr/bin/env python3
"""Qualify arm identity and stability exchange at the true period-5 flip."""
from __future__ import annotations
import argparse,json,platform,time
from pathlib import Path
import numpy as np,scipy
from butterfly import RosslerParameters,SolverConfig
from butterfly.scan import atomic_write,canonical_json,git_value,sha256_bytes
from qualify_separated_normal_form import correct_fixed_b,interpolate_branch,nontrivial_modulus
from compare_periodic_orbit_identity import dense_orbit,phase_aligned_rms
from continue_identity_constrained_periodic_b import crossing_count
def primary_seed(rows,b):
 o=sorted(rows,key=lambda r:r['parameters']['b']);bs=np.array([r['parameters']['b'] for r in o]);state=np.array([np.interp(b,bs,[r['initial_state'][i] for r in o]) for i in range(3)]);period=float(np.interp(b,bs,[r['period_time'] for r in o]));return state,period
def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--branches',type=Path,required=True);p.add_argument('--primary',type=Path,required=True);p.add_argument('--output',type=Path,required=True);z=p.parse_args();mb=z.manifest.read_bytes();m=json.loads(mb);bb=z.branches.read_bytes();pb=z.primary.read_bytes()
 if sha256_bytes(bb)!=m['branch_receipt_sha256'] or sha256_bytes(pb)!=m['primary_receipt_sha256']:raise SystemExit('hash mismatch')
 src={'commit':git_value('rev-parse','HEAD'),'branch':git_value('branch','--show-current'),'dirty':bool(git_value('status','--porcelain'))}
 if src['dirty']:raise SystemExit('clean source required')
 br=json.loads(bb);pr=json.loads(pb);a=pr['fixed_a'];c=pr['fixed_c'];b=m['target_b'];solver=SolverConfig(**m['solver']);corr=m['corrector'];ps,pt=primary_seed(pr['rows'],b);parent=correct_fixed_b(a=a,b=b,c=c,initial_state=ps,period_time=pt,solver=solver,tolerance=corr['tolerance'],max_evaluations=corr['max_evaluations']);children=[]
 for arm in br['branches']:
  rows=[r for r in arm['rows'] if r['one_traversal_crossing_count']==10];state,period=interpolate_branch(rows,b);children.append(correct_fixed_b(a=a,b=b,c=c,initial_state=state,period_time=period,solver=solver,tolerance=corr['tolerance'],max_evaluations=corr['max_evaluations']))
 pars=RosslerParameters(a=a,b=b,c=c);dense=[dense_orbit(x[0],pars,solver) for x in children];identity=phase_aligned_rms((children[0][0],dense[0]),(children[1][0],dense[1]),phase_samples=m['comparison']['phase_samples'],coarse_shifts=m['comparison']['coarse_shifts'],shift_tolerance=m['comparison']['shift_tolerance']);pdense=dense_orbit(parent[0],pars,solver);separation=phase_aligned_rms((parent[0],pdense),(children[0][0],dense[0]),phase_samples=m['comparison']['phase_samples'],coarse_shifts=m['comparison']['coarse_shifts'],shift_tolerance=m['comparison']['shift_tolerance']);pc,_=crossing_count(a,b,c,parent[0].initial_state,parent[0].period_time,solver);cc=[crossing_count(a,b,c,x[0].initial_state,x[0].period_time,solver)[0] for x in children];pm=nontrivial_modulus(parent[1]);cms=[nontrivial_modulus(x[1]) for x in children];ac=m['acceptance'];out={'schema':'butterfly.true-period5-flip-child-qualification.v1','experiment_id':m['experiment_id'],'manifest_sha256':sha256_bytes(mb),'branch_receipt_sha256':sha256_bytes(bb),'primary_receipt_sha256':sha256_bytes(pb),'source':src,'environment':{'python':platform.python_version(),'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__},'parameters':{'a':a,'b':b,'c':c},'parent':{'period_time':parent[0].period_time,'closure_error':parent[0].closure_error,'crossing_count':pc,'multiplier_modulus':pm},'children':[{'period_time':x[0].period_time,'closure_error':x[0].closure_error,'crossing_count':count,'multiplier_modulus':mod} for x,count,mod in zip(children,cc,cms)],'child_arm_identity':identity,'parent_child_separation':separation};out['passed']=identity['rms']<=ac['max_child_arm_rms'] and separation['rms']>=ac['minimum_parent_child_rms'] and parent[0].closure_error<=ac['max_closure_error'] and all(x[0].closure_error<=ac['max_closure_error'] for x in children) and pc==5 and all(x==10 for x in cc) and pm>1 and all(x<1 for x in cms);atomic_write(z.output,canonical_json(out));print(json.dumps(out,sort_keys=True));return 0 if out['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
