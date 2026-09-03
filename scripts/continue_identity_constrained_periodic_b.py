#!/usr/bin/env python3
"""Continue a periodic orbit in b while enforcing Poincare family identity."""

from __future__ import annotations
import argparse, json, platform, time
from pathlib import Path
import numpy as np, scipy
from butterfly import RosslerParameters,SolverConfig,collect_crossings,correct_periodic_orbit,legacy_rossler_section
from butterfly.scan import atomic_write,canonical_json,git_value,sha256_bytes
from continue_periodic_orbits_in_b import orbit_row,candidate_crossings

def crossing_count(a,b,c,state,period,solver):
    p=RosslerParameters(a=a,b=b,c=c); eps=1e-8
    x=collect_crossings(p,state,legacy_rossler_section(p),transient=0.0,observation_horizon=period*(1+eps),max_crossings=32,config=solver)
    keep=(x.times>period*1e-7)&(x.times<=period*(1+eps))
    return int(np.sum(keep)),x.integration_success

def direction(seed,*,a,c,direction,limit,expected,solver,continuation,corrector):
    accepted=[seed]; rows=[]; rejected=[]; step=float(continuation['nominal_step']); minimum=float(continuation['minimum_step'])
    while direction*(limit-accepted[-1]['parameters']['b'])>1e-14:
        current=accepted[-1]; db=min(step,abs(limit-current['parameters']['b'])); target=current['parameters']['b']+direction*db
        if len(accepted)>=2:
            previous=accepted[-2]; scale=(target-current['parameters']['b'])/(current['parameters']['b']-previous['parameters']['b']); state=np.asarray(current['initial_state'])+scale*(np.asarray(current['initial_state'])-np.asarray(previous['initial_state'])); period=current['period_time']+scale*(current['period_time']-previous['period_time'])
        else: state=np.asarray(current['initial_state']); period=current['period_time']
        try: correction=correct_periodic_orbit(RosslerParameters(a=a,b=target,c=c),state,period,config=solver,max_evaluations=int(corrector['max_evaluations']),tolerance=float(corrector['tolerance']))
        except Exception as error: correction=None; message=f'{type(error).__name__}: {error}'
        else: message=correction.message
        count=None; integration=False
        if correction is not None and correction.success: count,integration=crossing_count(a,target,c,correction.initial_state,correction.period_time,solver)
        if correction is None or not correction.success or not integration or count!=expected:
            rejected.append({'from_b':current['parameters']['b'],'target_b':target,'trial_step':db,'corrector_success':bool(correction and correction.success),'crossing_count':count,'message':message});step=db/2
            if step<minimum: break
            continue
        row=orbit_row(RosslerParameters(a=a,b=target,c=c),correction,solver);row['accepted_step']=db;row['one_traversal_crossing_count']=count;rows.append(row);accepted.append(row);step=min(float(continuation['nominal_step']),db*1.5)
    return rows,{'direction':direction,'limit':limit,'last_b':accepted[-1]['parameters']['b'],'reached_limit':abs(accepted[-1]['parameters']['b']-limit)<=1e-12,'rejected_trials':rejected,'terminal_step':step}

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--source-orbits',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();mb=args.manifest.read_bytes();m=json.loads(mb);sb=args.source_orbits.read_bytes()
    if sha256_bytes(sb)!=m['source_orbit_receipt_sha256']:raise SystemExit('source hash mismatch')
    src={'commit':git_value('rev-parse','HEAD'),'branch':git_value('branch','--show-current'),'dirty':bool(git_value('status','--porcelain'))}
    if src['dirty']:raise SystemExit('clean source required')
    d=json.loads(sb);family=next(x for x in d['families'] if x['id']==m['source_family_id']);point=next(x for x in family['points'] if all(abs(x['parameters'][k]-m['seed'][k])<1e-12 for k in ('a','b','c')));q=point['parameters'];cor=point['correction'];solver=SolverConfig(**m['solver']);seed_correction=type('C',(),{'initial_state':np.asarray(cor['initial_state']),'period_time':cor['period_time'],'closure_error':cor['closure_error'],'phase_residual':cor['phase_residual'],'correction_norm':cor['correction_norm'],'evaluations':cor['evaluations']})();seed=orbit_row(RosslerParameters(**q),seed_correction,solver);seed['one_traversal_crossing_count'],_=crossing_count(q['a'],q['b'],q['c'],seed['initial_state'],seed['period_time'],solver)
    started=time.perf_counter();down,ds=direction(seed,a=q['a'],c=q['c'],direction=-1,limit=m['continuation']['b_min'],expected=m['expected_crossing_count'],solver=solver,continuation=m['continuation'],corrector=m['corrector']);up,us=direction(seed,a=q['a'],c=q['c'],direction=1,limit=m['continuation']['b_max'],expected=m['expected_crossing_count'],solver=solver,continuation=m['continuation'],corrector=m['corrector']);rows=list(reversed(down))+[seed]+up;ac=m['acceptance'];out={'schema':'butterfly.identity-constrained-b-continuation.v1','experiment_id':m['experiment_id'],'manifest_sha256':sha256_bytes(mb),'source_orbit_receipt_sha256':sha256_bytes(sb),'source':src,'environment':{'python':platform.python_version(),'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__},'fixed_a':q['a'],'fixed_c':q['c'],'expected_crossing_count':m['expected_crossing_count'],'rows':rows,'downward_status':ds,'upward_status':us,'candidate_crossings':candidate_crossings(rows),'elapsed_seconds':time.perf_counter()-started}
    out['passed']=seed['one_traversal_crossing_count']==m['expected_crossing_count'] and len(rows)>=ac['minimum_accepted_points'] and len(down)>=ac['minimum_points_each_direction'] and len(up)>=ac['minimum_points_each_direction'] and all(r['one_traversal_crossing_count']==m['expected_crossing_count'] and r['closure_error']<=ac['max_closure_error'] for r in rows) and len(ds['rejected_trials'])+len(us['rejected_trials'])>=ac['minimum_rejected_identity_trials'];atomic_write(args.output,canonical_json(out));print(json.dumps({k:v for k,v in out.items() if k!='rows'},sort_keys=True));return 0 if out['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
