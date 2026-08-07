#!/usr/bin/env python3
"""Refine where a stable periodic orbit crosses the legacy half-plane gate."""
from __future__ import annotations
import argparse,json,platform,time
from pathlib import Path
import numpy as np,scipy
from scipy.integrate import solve_ivp
from butterfly import RosslerParameters,SolverConfig,legacy_rossler_section,rossler_rhs
from butterfly.scan import atomic_write,canonical_json,git_value,sha256_bytes
from qualify_separated_normal_form import correct_fixed_b,interpolate_branch,nontrivial_modulus
def gate_data(pars,state,period,solver,rank):
 sec=legacy_rossler_section(pars)
 def event(t,x):return sec.value(x)
 event.direction=0;event.terminal=False
 r=solve_ivp(lambda t,x:rossler_rhs(t,x,pars),(0,period*(1+1e-8)),state,method=solver.method,rtol=solver.rtol,atol=solver.atol,max_step=solver.max_step,events=event)
 times=np.asarray(r.t_events[0]);states=np.asarray(r.y_events[0]);keep=times>period*1e-7;times=times[keep];states=states[keep];margins=float(sec.gate_upper)-states[:,sec.gate_axis];ordered=np.sort(margins)[::-1];return {'raw_crossing_count':len(margins),'accepted_crossing_count':int(np.sum(margins>0)),'ranked_gate_margin':float(ordered[rank-1]),'minimum_absolute_gate_margin':float(np.min(abs(margins))),'margins':margins.tolist(),'integration_success':r.success}
def evaluate(b,rows,a,c,solver,corrector,rank):
 s,t=interpolate_branch(rows,b);x,m=correct_fixed_b(a=a,b=b,c=c,initial_state=s,period_time=t,solver=solver,tolerance=corrector['tolerance'],max_evaluations=corrector['max_evaluations']);g=gate_data(RosslerParameters(a=a,b=b,c=c),x.initial_state,x.period_time,solver,rank);return {'b':b,'initial_state':x.initial_state.tolist(),'period_time':x.period_time,'closure_error':x.closure_error,'multiplier_modulus':nontrivial_modulus(m),**g}
def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--branches',type=Path,required=True);p.add_argument('--output',type=Path,required=True);z=p.parse_args();mb=z.manifest.read_bytes();m=json.loads(mb);bb=z.branches.read_bytes()
 if sha256_bytes(bb)!=m['branch_receipt_sha256']:raise SystemExit('hash mismatch')
 src={'commit':git_value('rev-parse','HEAD'),'branch':git_value('branch','--show-current'),'dirty':bool(git_value('status','--porcelain'))}
 if src['dirty']:raise SystemExit('clean source required')
 d=json.loads(bb);a=m['fixed_a'];c=m['fixed_c'];rows=next(q['rows'] for q in d['branches'] if q['direction']==m['branch_direction']);solver=SolverConfig(**m['solver']);left_b,right_b=m['b_bracket'];started=time.perf_counter();left=evaluate(left_b,rows,a,c,solver,m['corrector'],m['accepted_rank']);right=evaluate(right_b,rows,a,c,solver,m['corrector'],m['accepted_rank'])
 if left['ranked_gate_margin']*right['ranked_gate_margin']>0:raise RuntimeError('gate margin is not bracketed')
 evals=[]
 for _ in range(m['refinement']['maximum_iterations']):
  if right_b-left_b<=m['refinement']['b_tolerance']:break
  b=(left_b+right_b)/2;x=evaluate(b,rows,a,c,solver,m['corrector'],m['accepted_rank']);evals.append(x)
  if left['ranked_gate_margin']*x['ranked_gate_margin']<=0:right_b=b;right=x
  else:left_b=b;left=x
 best=min(evals,key=lambda x:abs(x['ranked_gate_margin']));ac=m['acceptance'];out={'schema':'butterfly.legacy-gate-transition-refinement.v1','experiment_id':m['experiment_id'],'manifest_sha256':sha256_bytes(mb),'branch_receipt_sha256':sha256_bytes(bb),'source':src,'environment':{'python':platform.python_version(),'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__},'b_bracket':[left_b,right_b],'b_estimate':(left_b+right_b)/2,'bracket_width':right_b-left_b,'left_endpoint':left,'right_endpoint':right,'best_evaluation':best,'evaluations':evals,'elapsed_seconds':time.perf_counter()-started};out['passed']=out['bracket_width']<=ac['max_b_bracket_width'] and abs(best['ranked_gate_margin'])<=ac['max_gate_margin'] and best['closure_error']<=ac['max_closure_error'] and best['multiplier_modulus']<1 and {left['accepted_crossing_count'],right['accepted_crossing_count']}==set(m['expected_endpoint_counts']);atomic_write(z.output,canonical_json(out));print(json.dumps({k:v for k,v in out.items() if k!='evaluations'},sort_keys=True));return 0 if out['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
