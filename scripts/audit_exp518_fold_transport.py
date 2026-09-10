#!/usr/bin/env python3
"""Full local raw replay and separately coded transport arithmetic."""
import argparse
import json
import math
from pathlib import Path

from butterfly._paired_startup import inventory,sha256
from butterfly.bounded_json import directory_bytes,write_bounded_json
from scripts import run_exp518_fold_transport as run
from scripts import audit_exp502_joint_contact as fold_audit


def read(path):return json.loads(path.read_bytes())


def scalar_decision(previous,current,decision):
    if not decision['qualified']:return
    # Vectorized implementation is separate from the controller's scalar loops.
    np=run.base.np;scales=np.asarray(run.model.SCALES)
    old,new=[run.model.states(rows) for rows in (previous,current)]
    spread=max(float(np.max(np.ptp(np.asarray([v[k] for v in new]),axis=0)/scales))
               for k in ('image_state','next_state'))
    displacement=max(float(np.max(np.abs(np.asarray([v[k] for v in new])-np.asarray([v[k] for v in old]))/scales))
                     for k in ('image_state','next_state'))
    if (not math.isclose(spread,decision['cross_history_spread'],rel_tol=1e-12,abs_tol=1e-15)
            or not math.isclose(displacement,decision['adjacent_displacement'],rel_tol=1e-12,abs_tol=1e-15)
            or decision['transport_qualified']!=(spread<=1e-6 and displacement<=.01)):
        raise ValueError('separately coded transport arithmetic differs')


def audit(output,expected_sha):
    p=run.load()
    if sha256(output/'summary.json')!=expected_sha:raise ValueError('summary byte identity differs')
    saved,b=read(output/'summary.json'),read(output/'binding.json')
    if (saved['experiment_id']!='EXP-518' or saved['status']!='completed' or saved['binding']!=b
            or b['sources']!={n:sha256(run.ROOT/n) for n in p['source_paths']}
            or b['inputs']!=run.INPUTS or b['plan_sha256']!=sha256(run.PLAN)
            or b['paid_review']!=p['paid_review'] or saved['symbolic_chains_verified'] is not False
            or b['initial_free_bytes']<p['limits']['initial_free_bytes']
            or saved['files']!=inventory(output,omit=('summary.json',))
            or not b['started_utc']<=saved['completed_utc']
            or not 0<=saved['elapsed_seconds']<=p['limits']['wall_seconds']):
        raise ValueError('source/input/inventory/resource binding differs')
    marker=run.ROOT/'artifacts/EXP-518/target-once.json'
    if sha256(marker)!=saved['marker_sha256'] or read(marker)!=b:raise ValueError('consumed marker differs')
    startup=read(output/'startup.json')
    if (startup['passed'] is not True or startup['isolated'] is not True or startup['new_integrations']!=0
            or startup['sources']!={n:sha256(run.ROOT/n) for n in set(p['source_paths'])|set(run.INPUTS)}
            or json.loads(startup['stdout'])!=dict(valid=True,new_integrations=0,maximum_substeps=2,folds_per_step=4,maximum_target_ivps=256)):
        raise ValueError('isolated startup differs')
    controls=run.prior.controls(p)
    if controls!=read(output/'control-replay.json'):raise ValueError('analytic controls differ')
    names={'binding.json','startup.json','control-replay.json'};calls=0;previous=run.inputs()
    def measure(spec,candidates):
        nonlocal calls,previous
        stage=output/spec['id']
        if read(stage/'inputs.json')!=dict(spec=spec,candidates=candidates):raise ValueError('warm-start inputs differ')
        names.update({spec['id']+'/inputs.json',spec['id']+'/rows.json'})
        def probe(c):
            nonlocal calls
            folder=stage/c['id'];profiles=[];rhs,_,section=run.coverage.fields(c)
            for method in p['solvers']:
                label='midpoint--'+method
                profile=read(folder/(label+'.json'));start=read(folder/(label+'-started.json'))
                if (start['candidate']!=c or start['method']!=method or profile['method']!=method
                        or not b['started_utc']<=start['started_utc']<=saved['completed_utc']):
                    raise ValueError('midpoint source/configuration differs')
                rebuilt,paths=run.prior.previous.previous_audit.check_profile(folder,label,profile,c,c['seed_u'],p['numerical'],rhs,section)
                calls+=len(paths);names.update(spec['id']+'/'+c['id']+'/'+n for n in paths|{label+'.json',label+'-started.json'})
                profiles.append(rebuilt)
            seeded,pair=run.midpoint_seed(c,profiles,p)
            if read(folder/'seed.json')!=dict(candidate=seeded,pair=pair):raise ValueError('midpoint seed differs')
            names.add(spec['id']+'/'+c['id']+'/seed.json')
            return seeded,profiles,pair
        def shoot(c):
            nonlocal calls
            folder=stage/c['id'];rows=[]
            comparison,paths,count=fold_audit.old.check_fold(folder,c,p['numerical'],b,saved['completed_utc'])
            calls+=count
            for method in p['solvers']:
                label=c['id']+'--'+method;profile=read(folder/(label+'.json'))
                for i,entry in enumerate(profile['censuses']):
                    name=label+f'--guard-{i}.npz'
                    fold_audit.check_guard(fold_audit.old.load_raw(folder/name),
                        fold_audit.old.load_raw(folder/(label+f'--census-{i}.npz')),entry['report'],p['numerical']['guard'])
                    paths.add(name);calls+=1
                rows.append(profile)
            if comparison!=dict(run.base.compare(c,rows,p['numerical']),parent_id=c['parent_id']):
                raise ValueError('fold comparison differs')
            names.update(spec['id']+'/'+c['id']+'/'+n for n in paths)
            return rows
        rows=run.prior.model.follow(candidates,probe,shoot,lambda c,r:run.assess(c,r,p))
        for row in rows:
            name=spec['id']+'/'+row['candidate']['id']+'/result.json'
            if not run.coverage.public.equal(row,read(output/name)):raise ValueError('complete candidate replay differs')
            names.add(name)
        if not run.coverage.public.equal(rows,read(stage/'rows.json')):raise ValueError('stage result differs')
        scalar_decision(previous,rows,run.model.decision(previous,rows));previous=rows
        print(json.dumps(dict(audited_substep=spec['id'],target_ivps=calls)),flush=True)
        return rows
    result=run.model.follow(run.inputs(),p['specifications'],run.transport.offset,measure)
    endpoint=run.endpoint(result);size=directory_bytes(output)
    if (not run.coverage.public.equal(result,saved['result']) or not run.coverage.public.equal(endpoint,saved['endpoint_comparison'])
            or names!=set(saved['files'])
            or saved['stage_progress']!=[dict(id=r['spec']['id'],status='completed') for r in result['rows']]
            or calls!=saved['target_ivps'] or calls>p['limits']['target_ivps'] or size>p['limits']['output_bytes']):
        raise ValueError('complete transport/IVP/output accounting differs')
    if endpoint is not None:
        folds=[dict(r['assessment']['comparison'],parent_id=r['candidate']['parent_id']) for r in result['rows'][-1]['rows']]
        scalar=fold_audit.old.scalar_contact(folds,run.transport.inputs()['cycle'])
        if not fold_audit.old.periodic_audit.numeric_equal(scalar,endpoint['contact']):raise ValueError('separate endpoint arithmetic differs')
    return dict(experiment_id='EXP-518',passed=True,protocol_compliant=True,source_commit=b['source_commit'],
        plan_sha256=sha256(run.PLAN),summary_sha256=expected_sha,inputs=run.INPUTS,result=result,
        endpoint_comparison=endpoint,controls=controls,target_ivps=calls,output_bytes_including_summary=size,
        output_limit_bytes=p['limits']['output_bytes'],new_integrations=0,symbolic_chains_verified=False,
        paid_review=p['paid_review'],scope='Full local raw midpoint/fold/guard/census replay; separately coded transport and endpoint arithmetic. Not an independent-team or rigorous exact-flow proof.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',type=Path,required=True);p.add_argument('--expected-sha256',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();result=audit(a.run,a.expected_sha256)
    write_bounded_json(a.output.parent,a.output,result,limit_bytes=directory_bytes(a.output.parent)+32*1024**2)
    print(json.dumps(dict(passed=True,target_ivps=result['target_ivps'],audit_sha256=sha256(a.output))))
