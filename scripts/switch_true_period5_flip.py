#!/usr/bin/env python3
"""Switch from a verified period-5 flip to its doubled-period branch."""
from __future__ import annotations
import argparse,json,platform,time
from pathlib import Path
import numpy as np,scipy
from butterfly import RosslerParameters,SolverConfig,rossler_rhs
from butterfly.scan import atomic_write,canonical_json,git_value,sha256_bytes
from switch_periodic_branch import extended_shooting_jacobian
from pseudo_arclength_periodic_b import correct_arclength,diagnose
from continue_identity_constrained_periodic_b import crossing_count
def vec(row):return np.r_[row['initial_state'],2*row['period_time'],row['parameters']['b']]
def primary_distance(v,rows):
 o=sorted(rows,key=lambda r:r['parameters']['b']);bs=np.array([r['parameters']['b'] for r in o]);q=np.empty(5)
 for i in range(3):q[i]=np.interp(v[4],bs,[r['initial_state'][i] for r in o])
 q[3]=np.interp(v[4],bs,[2*r['period_time'] for r in o]);q[4]=v[4];return float(np.linalg.norm(v-q))
def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--event',type=Path,required=True);p.add_argument('--primary',type=Path,required=True);p.add_argument('--output',type=Path,required=True);z=p.parse_args();mb=z.manifest.read_bytes();m=json.loads(mb);eb=z.event.read_bytes();pb=z.primary.read_bytes()
 if sha256_bytes(eb)!=m['event_receipt_sha256'] or sha256_bytes(pb)!=m['primary_receipt_sha256']:raise SystemExit('hash mismatch')
 src={'commit':git_value('rev-parse','HEAD'),'branch':git_value('branch','--show-current'),'dirty':bool(git_value('status','--porcelain'))}
 if src['dirty']:raise SystemExit('clean source required')
 e=json.loads(eb);primary=json.loads(pb);best=e['best_evaluation'];a=primary['fixed_a'];c=primary['fixed_c'];b=e['b_estimate'];event=np.r_[best['initial_state'],2*best['period_time'],b];solver=SolverConfig(**m['solver']);pars=RosslerParameters(a=a,b=b,c=c);phase=rossler_rhs(0,event[:3],pars);phase/=np.linalg.norm(phase);J=extended_shooting_jacobian(event,a=a,c=c,phase_direction=phase,solver=solver);_,sv,rv=np.linalg.svd(J,full_matrices=True);basis=rv[-2:].T;rows=primary['rows'];below=max((r for r in rows if r['parameters']['b']<b),key=lambda r:r['parameters']['b']);above=min((r for r in rows if r['parameters']['b']>b),key=lambda r:r['parameters']['b']);obs=vec(above)-vec(below);obs/=np.linalg.norm(obs);pt=basis@(basis.T@obs);pt/=np.linalg.norm(pt);st=basis[:,0]-pt*np.dot(pt,basis[:,0]);
 if np.linalg.norm(st)<1e-8:st=basis[:,1]-pt*np.dot(pt,basis[:,1])
 st/=np.linalg.norm(st);started=time.perf_counter();branches=[]
 for sign in (-1,1):
  tangent=sign*st;predictor=event+m['continuation']['step_length']*tangent;x,status=correct_arclength(predictor,tangent,event[:3],b,a=a,c=c,solver=solver,tolerance=m['corrector']['tolerance'],max_evaluations=m['corrector']['max_evaluations']);points=[event];outrows=[];statuses=[status]
  if status['success']:
   points.append(x);row=diagnose(x,a=a,c=c,solver=solver);row['one_traversal_crossing_count'],_=crossing_count(a,row['b'],c,row['initial_state'],row['period_time'],solver);outrows.append(row)
  for i in range(1,m['continuation']['steps_per_direction']):
   if len(points)<2:break
   tangent=points[-1]-points[-2];tangent/=np.linalg.norm(tangent);predictor=points[-1]+m['continuation']['step_length']*tangent;x,status=correct_arclength(predictor,tangent,points[-1][:3],points[-1][4],a=a,c=c,solver=solver,tolerance=m['corrector']['tolerance'],max_evaluations=m['corrector']['max_evaluations']);statuses.append(status)
   if not status['success']:break
   points.append(x);row=diagnose(x,a=a,c=c,solver=solver);row['one_traversal_crossing_count'],_=crossing_count(a,row['b'],c,row['initial_state'],row['period_time'],solver);outrows.append(row)
   if not m['continuation']['b_guard'][0]<=x[4]<=m['continuation']['b_guard'][1]:break
  branches.append({'direction':sign,'rows':outrows,'statuses':statuses,'point_count':len(outrows),'endpoint_distance_from_doubled_primary':primary_distance(points[-1],rows)})
 allrows=[r for q in branches for r in q['rows']];ac=m['acceptance'];out={'schema':'butterfly.true-period5-flip-branch-switch.v1','experiment_id':m['experiment_id'],'manifest_sha256':sha256_bytes(mb),'event_receipt_sha256':sha256_bytes(eb),'primary_receipt_sha256':sha256_bytes(pb),'source':src,'environment':{'python':platform.python_version(),'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__},'event_variables':event.tolist(),'shooting_singular_values':sv.tolist(),'primary_tangent':pt.tolist(),'secondary_tangent':st.tolist(),'absolute_tangent_dot':abs(float(np.dot(pt,st))),'branches':branches,'elapsed_seconds':time.perf_counter()-started};out['passed']=sv[-1]<=ac['max_small_singular_value'] and out['absolute_tangent_dot']<=ac['max_tangent_dot'] and all(q['point_count']>=ac['minimum_points_per_direction'] and q['endpoint_distance_from_doubled_primary']>=ac['minimum_endpoint_distance'] for q in branches) and all(r['closure_error']<=ac['max_closure_error'] and r.get('one_traversal_crossing_count',10)==10 for r in allrows);atomic_write(z.output,canonical_json(out));print(json.dumps({k:v for k,v in out.items() if k!='branches'},sort_keys=True));print(json.dumps([{'direction':q['direction'],'points':q['point_count'],'distance':q['endpoint_distance_from_doubled_primary']} for q in branches]));return 0 if out['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
