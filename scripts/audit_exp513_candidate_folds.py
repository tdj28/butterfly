#!/usr/bin/env python3
"""Replay every new product and all five decisions, without new integrations."""
import argparse
import json
from pathlib import Path
from butterfly._paired_startup import inventory,sha256
from butterfly.bounded_json import directory_bytes,write_bounded_json
from scripts import run_exp513_candidate_folds as run
from scripts import audit_exp502_joint_contact as fold_audit


def read(path):
    return json.loads(path.read_bytes())


def scalar_distances(row,targets,scales):
    if not row['assessment']['qualified']:
        return
    expected=[]
    for profile in row['folds']:
        o=profile['qualification']['observations'][1]
        for target in targets:
            values={key:max(abs(a-b)/s for a,b,s in zip(o[key],target[key],scales,strict=True))
                for key in ('image_state','next_state')}
            expected.append(dict(method=profile['method'],target_id=target['id'],target_method=target['method'],**values))
    if (not run.coverage.public.equal(expected,row['assessment']['reference_distances'])
            or all(max(v['image_state'],v['next_state'])<=1e-6 for v in expected)!=row['assessment']['reference_restored']):
        raise ValueError('separately coded reference distances differ')


def audit(output,expected_sha):
    p=run.load()
    if sha256(output/'summary.json')!=expected_sha:
        raise ValueError('summary byte identity differs')
    saved,b=read(output/'summary.json'),read(output/'binding.json')
    if (saved['experiment_id']!='EXP-513' or saved['status']!='completed' or saved['binding']!=b
            or b['sources']!={n:sha256(run.ROOT/n) for n in p['source_paths']}
            or b['inputs']!=run.INPUTS or b['plan_sha256']!=sha256(run.PLAN)
            or b['paid_review']!=p['paid_review'] or saved['symbolic_chains_verified'] is not False
            or b['initial_free_bytes']<p['limits']['initial_free_bytes']
            or saved['files']!=inventory(output,omit=('summary.json',))
            or not b['started_utc']<=saved['completed_utc']
            or not 0<=saved['elapsed_seconds']<=p['limits']['wall_seconds']):
        raise ValueError('source/input/inventory/resource binding differs')
    marker=run.ROOT/'artifacts/EXP-513/target-once.json'
    if sha256(marker)!=saved['marker_sha256'] or read(marker)!=b:
        raise ValueError('consumed marker differs')
    startup=read(output/'startup.json')
    if (startup['passed'] is not True or startup['isolated'] is not True or startup['new_integrations']!=0
            or startup['sources']!={n:sha256(run.ROOT/n) for n in set(p['source_paths'])|set(run.INPUTS)}
            or json.loads(startup['stdout'])!=dict(valid=True,new_integrations=0,candidates=5,maximum_target_ivps=160)):
        raise ValueError('isolated startup differs')
    control_result=run.controls(p)
    if control_result!=read(output/'control-replay.json'):
        raise ValueError('analytic control replay differs')
    names={'binding.json','startup.json','control-replay.json'}
    calls=0
    def probe(c):
        nonlocal calls
        folder=output/c['id']
        rhs,_,section=run.coverage.fields(c)
        profiles=[]
        for method in p['solvers']:
            label='midpoint--'+method
            profile=read(folder/(label+'.json'))
            start=read(folder/(label+'-started.json'))
            if (start['candidate']!=c or start['method']!=method or profile['method']!=method
                    or not b['started_utc']<=start['started_utc']<=saved['completed_utc']):
                raise ValueError('midpoint start/configuration differs')
            rebuilt,paths=run.previous.previous_audit.check_profile(folder,label,profile,c,c['seed_u'],p['numerical'],rhs,section)
            calls+=len(paths)
            names.update(c['id']+'/'+n for n in paths|{label+'.json',label+'-started.json'})
            profiles.append(rebuilt)
        seeded,pair=run.model.seed(c,profiles,p['numerical'])
        if read(folder/'seed.json')!=dict(candidate=seeded,pair=pair):
            raise ValueError('midpoint seed differs')
        names.add(c['id']+'/seed.json')
        return seeded,profiles,pair
    def shoot(c):
        nonlocal calls
        folder=output/c['id']
        comparison,paths,count=fold_audit.old.check_fold(folder,c,p['numerical'],b,saved['completed_utc'])
        calls+=count
        rows=[]
        for method in p['solvers']:
            label=c['id']+'--'+method
            profile=read(folder/(label+'.json'))
            for i,entry in enumerate(profile['censuses']):
                name=label+f'--guard-{i}.npz'
                fold_audit.check_guard(fold_audit.old.load_raw(folder/name),
                    fold_audit.old.load_raw(folder/(label+f'--census-{i}.npz')),entry['report'],p['numerical']['guard'])
                paths.add(name)
                calls+=1
            rows.append(profile)
        if comparison!=dict(run.base.compare(c,rows,p['numerical']),parent_id=c['parent_id']):
            raise ValueError('fold comparison differs')
        names.update(c['id']+'/'+n for n in paths)
        return rows
    rows=run.model.follow(p['candidates'],probe,shoot,lambda c,r:run.assess(c,r,p))
    for row in rows:
        name=row['candidate']['id']+'/result.json'
        if not run.coverage.public.equal(row,read(output/name)):
            raise ValueError('complete candidate result differs')
        names.add(name)
        if row['assessment'] is not None:
            scalar_distances(row,p['targets'],p['numerical']['scales'])
    size=directory_bytes(output)
    if (not run.coverage.public.equal(rows,saved['rows']) or names!=set(saved['files'])
            or saved['progress']!=[dict(id=r['candidate']['id'],status=r['status']) for r in rows]
            or calls!=saved['target_ivps'] or calls>p['limits']['target_ivps'] or size>p['limits']['output_bytes']):
        raise ValueError('complete matrix/decision/resource accounting differs')
    return dict(experiment_id='EXP-513',passed=True,protocol_compliant=True,source_commit=b['source_commit'],
        plan_sha256=sha256(run.PLAN),summary_sha256=expected_sha,inputs=run.INPUTS,rows=rows,
        controls=control_result,target_ivps=calls,output_bytes_including_summary=size,
        output_limit_bytes=p['limits']['output_bytes'],new_integrations=0,
        symbolic_chains_verified=False,paid_review=p['paid_review'],
        scope='Full local new midpoint dense/mesh and fold mesh/algebra/census replay; old controls and compact targets reused. Not independent-team replication or exact-flow proof.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--expected-sha256',required=True)
    parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args()
    result=audit(a.run,a.expected_sha256)
    write_bounded_json(a.output.parent,a.output,result,limit_bytes=directory_bytes(a.output.parent)+32*1024**2)
    print(json.dumps(dict(passed=True,target_ivps=result['target_ivps'],audit_sha256=sha256(a.output))))


if __name__=='__main__':
    main()
