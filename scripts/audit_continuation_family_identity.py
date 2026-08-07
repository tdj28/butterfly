#!/usr/bin/env python3
"""Classify every row of the inherited period-5 natural continuation."""

from __future__ import annotations
import argparse, json, platform, time
from pathlib import Path
import numpy as np
import scipy
from butterfly import RosslerParameters, SolverConfig, classify_fundamental_period, collect_crossings, legacy_rossler_section
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--manifest',type=Path,required=True); p.add_argument('--source-continuation',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    mb=a.manifest.read_bytes(); m=json.loads(mb); sb=a.source_continuation.read_bytes()
    if m.get('schema')!='butterfly.continuation-family-identity-manifest.v1': raise SystemExit('unsupported manifest')
    if sha256_bytes(sb)!=m['source_continuation_receipt_sha256']: raise SystemExit('source hash mismatch')
    source={'commit':git_value('rev-parse','HEAD'),'branch':git_value('branch','--show-current'),'dirty':bool(git_value('status','--porcelain'))}
    if source['commit'] is None or source['dirty']: raise SystemExit('audit requires clean source')
    d=json.loads(sb); family=next(x for x in d['families'] if x['id']==m['family_id']); solver=SolverConfig(**m['solver']); cc=m['crossings']; started=time.perf_counter(); rows=[]
    for index,row in enumerate(sorted(family['rows'],key=lambda x:float(x['parameters']['b']))):
        q=row['parameters']; pars=RosslerParameters(a=float(q['a']),b=float(q['b']),c=float(q['c']))
        crossings=collect_crossings(pars,np.asarray(row['initial_state'],float),legacy_rossler_section(pars),transient=0.0,observation_horizon=float(cc['observed_stored_periods'])*float(row['period_time']),max_crossings=int(cc['max_crossings']),config=solver)
        rec=classify_fundamental_period(crossings.states,max_period=int(cc['max_period']),required_repeats=int(cc['required_repeats']),atol=float(cc['atol']),rtol=float(cc['rtol']))
        rows.append({'index':index,'b':float(q['b']),'stored_period':float(row['period_time']),'correction_norm':float(row['correction_norm']),'closure_error':float(row['closure_error']),'crossing_count':len(crossings.times),'label':rec.label.value,'fundamental_period':rec.fundamental_period,'recurrence_error':rec.recurrence_error})
    periods=[r['fundamental_period'] for r in rows]; transitions=[i for i in range(1,len(rows)) if periods[i]!=periods[i-1]]; ac=m['acceptance']
    receipt={'schema':'butterfly.continuation-family-identity-receipt.v1','experiment_id':m['experiment_id'],'manifest_sha256':sha256_bytes(mb),'source_continuation_receipt_sha256':sha256_bytes(sb),'source':source,'environment':{'python':platform.python_version(),'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__},'rows':rows,'period_counts':{str(k):periods.count(k) for k in sorted(set(periods),key=lambda x:(x is None,x))},'transition_indices':transitions,'transition_brackets':[{'left':rows[i-1],'right':rows[i]} for i in transitions],'elapsed_seconds':time.perf_counter()-started}
    receipt['passed']=bool(len(rows)>=int(ac['minimum_classified_rows']) and periods.count(int(ac['initial_period']))>=int(ac['minimum_initial_period_rows']) and periods.count(int(ac['final_period']))>=int(ac['minimum_final_period_rows']) and len(transitions)==int(ac['required_transition_count']) and periods[0]==int(ac['initial_period']) and periods[-1]==int(ac['final_period']))
    receipt['interpretation_limit']='Locates the discrete corrector family jump in the stored natural-continuation rows; it does not represent a dynamical period-5-to-3 bifurcation.'
    atomic_write(a.output,canonical_json(receipt)); print(json.dumps({k:v for k,v in receipt.items() if k!='rows'},sort_keys=True)); return 0 if receipt['passed'] else 1
if __name__=='__main__': raise SystemExit(main())
