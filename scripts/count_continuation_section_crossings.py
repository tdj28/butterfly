#!/usr/bin/env python3
"""Count accepted section crossings in exactly one stored closed traversal."""
from __future__ import annotations
import argparse,json,platform,time
from pathlib import Path
import numpy as np, scipy
from butterfly import RosslerParameters,SolverConfig,collect_crossings,legacy_rossler_section
from butterfly.scan import atomic_write,canonical_json,git_value,sha256_bytes
def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--source-continuation',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();mb=a.manifest.read_bytes();m=json.loads(mb);sb=a.source_continuation.read_bytes()
 if sha256_bytes(sb)!=m['source_continuation_receipt_sha256']:raise SystemExit('hash mismatch')
 src={'commit':git_value('rev-parse','HEAD'),'branch':git_value('branch','--show-current'),'dirty':bool(git_value('status','--porcelain'))}
 if src['dirty']:raise SystemExit('clean source required')
 d=json.loads(sb);f=next(x for x in d['families'] if x['id']==m['family_id']);solver=SolverConfig(**m['solver']);rows=[];t=time.perf_counter()
 for i,r in enumerate(sorted(f['rows'],key=lambda x:x['parameters']['b'])):
  q=r['parameters'];pars=RosslerParameters(**q);x=collect_crossings(pars,r['initial_state'],legacy_rossler_section(pars),transient=0,observation_horizon=r['period_time']*(1-1e-10),max_crossings=20,config=solver);rows.append({'index':i,'b':q['b'],'stored_period':r['period_time'],'crossing_count':len(x.times),'integration_success':x.integration_success,'correction_norm':r['correction_norm']})
 counts=[r['crossing_count'] for r in rows];trans=[i for i in range(1,len(rows)) if counts[i]!=counts[i-1]];ac=m['acceptance'];out={'schema':'butterfly.one-traversal-crossing-audit.v1','experiment_id':m['experiment_id'],'manifest_sha256':sha256_bytes(mb),'source_continuation_receipt_sha256':sha256_bytes(sb),'source':src,'environment':{'python':platform.python_version(),'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__},'rows':rows,'count_histogram':{str(k):counts.count(k) for k in sorted(set(counts))},'transition_indices':trans,'transition_brackets':[{'left':rows[i-1],'right':rows[i]} for i in trans],'elapsed_seconds':time.perf_counter()-t}
 out['passed']=all(r['integration_success'] for r in rows) and counts[0]==ac['initial_count'] and counts[-1]==ac['final_count'] and counts.count(ac['initial_count'])>=ac['minimum_each'] and counts.count(ac['final_count'])>=ac['minimum_each'];atomic_write(a.output,canonical_json(out));print(json.dumps({k:v for k,v in out.items() if k!='rows'},sort_keys=True));return 0 if out['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
