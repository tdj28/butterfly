#!/usr/bin/env python3
"""Refine a signed Floquet flip while enforcing periodic-orbit identity."""
from __future__ import annotations
import argparse,json,platform,time
from pathlib import Path
import numpy as np,scipy
from butterfly import RosslerParameters,SolverConfig,correct_periodic_orbit,flow_monodromy
from butterfly.scan import atomic_write,canonical_json,git_value,sha256_bytes
from continue_identity_constrained_periodic_b import crossing_count
def multiplier(a,b,c,state,period,solver,corrector):
 x=correct_periodic_orbit(RosslerParameters(a=a,b=b,c=c),state,period,config=solver,max_evaluations=corrector['max_evaluations'],tolerance=corrector['tolerance']);m=flow_monodromy(RosslerParameters(a=a,b=b,c=c),x.initial_state,x.period_time,config=solver);n=int(np.argmin(abs(m.multipliers-1)));v=max(np.delete(m.multipliers,n),key=abs);count,ok=crossing_count(a,b,c,x.initial_state,x.period_time,solver);return x,complex(v),count,ok
def row_value(r):return max((complex(v['real'],v['imag']) for v in r['nontrivial_multipliers']),key=abs)
def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--source-continuation',type=Path,required=True);p.add_argument('--output',type=Path,required=True);z=p.parse_args();mb=z.manifest.read_bytes();m=json.loads(mb);sb=z.source_continuation.read_bytes()
 if sha256_bytes(sb)!=m['source_continuation_sha256']:raise SystemExit('hash mismatch')
 src={'commit':git_value('rev-parse','HEAD'),'branch':git_value('branch','--show-current'),'dirty':bool(git_value('status','--porcelain'))}
 if src['dirty']:raise SystemExit('clean source required')
 d=json.loads(sb);a=d['fixed_a'];c=d['fixed_c'];left_b,right_b=m['b_bracket'];left=min(d['rows'],key=lambda r:abs(r['parameters']['b']-left_b));right=min(d['rows'],key=lambda r:abs(r['parameters']['b']-right_b));lr=row_value(left).real+1;rr=row_value(right).real+1;solver=SolverConfig(**m['solver']);evaluations=[];started=time.perf_counter()
 for _ in range(m['refinement']['maximum_iterations']):
  if right_b-left_b<=m['refinement']['b_tolerance']:break
  b=(left_b+right_b)/2;seed=left if b-left_b<=right_b-b else right;x,v,count,ok=multiplier(a,b,c,seed['initial_state'],seed['period_time'],solver,m['corrector']);res=v.real+1;e={'b':b,'initial_state':x.initial_state.tolist(),'period_time':x.period_time,'closure_error':x.closure_error,'multiplier':{'real':v.real,'imag':v.imag},'residual':res,'crossing_count':count};evaluations.append(e)
  if not ok or count!=m['expected_crossing_count'] or abs(v.imag)>1e-8:raise RuntimeError(f'identity/multiplier failure at b={b}')
  if lr*res<=0:right_b=b;rr=res;right=e
  else:left_b=b;lr=res;left=e
 best=min(evaluations,key=lambda e:abs(e['residual']));ac=m['acceptance'];out={'schema':'butterfly.identity-constrained-flip-refinement.v1','experiment_id':m['experiment_id'],'manifest_sha256':sha256_bytes(mb),'source_continuation_sha256':sha256_bytes(sb),'source':src,'environment':{'python':platform.python_version(),'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__},'b_bracket':[left_b,right_b],'b_estimate':(left_b+right_b)/2,'bracket_width':right_b-left_b,'best_evaluation':best,'evaluations':evaluations,'elapsed_seconds':time.perf_counter()-started};out['passed']=out['bracket_width']<=ac['max_b_bracket_width'] and abs(best['residual'])<=ac['max_multiplier_residual'] and best['closure_error']<=ac['max_closure_error'] and best['crossing_count']==m['expected_crossing_count'];atomic_write(z.output,canonical_json(out));print(json.dumps({k:v for k,v in out.items() if k!='evaluations'},sort_keys=True));return 0 if out['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
