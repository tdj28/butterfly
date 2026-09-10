#!/usr/bin/env python3
"""Audit all new dense products and explicit reuse of the unchanged EXP-511 grid."""
import argparse
import json
from pathlib import Path
from butterfly._paired_startup import inventory,sha256
from butterfly.bounded_json import directory_bytes,write_bounded_json
from scripts import run_exp512_censored_returns as run

read = run.previous_audit.read


def audit(output,expected_sha):
    p = run.load()
    if sha256(output/'summary.json')!=expected_sha:
        raise ValueError('extension summary identity differs')
    saved,binding = read(output/'summary.json'),read(output/'binding.json')
    if (saved['experiment_id']!='EXP-512' or saved['status']!='completed' or saved['binding']!=binding
            or binding['sources']!={n:sha256(run.ROOT/n) for n in p['source_paths']}
            or binding['inputs']!=run.INPUTS or binding['plan_sha256']!=sha256(run.PLAN)
            or binding['paid_review']!=p['paid_review'] or saved['symbolic_chains_verified'] is not False
            or binding['initial_free_bytes']<p['limits']['initial_free_bytes']
            or saved['files']!=inventory(output,omit=('summary.json',))
            or not binding['started_utc']<=saved['completed_utc']
            or not 0<=saved['elapsed_seconds']<=p['limits']['wall_seconds']):
        raise ValueError('extension source/input/raw/resource/claim binding differs')
    marker = run.ROOT/'artifacts/EXP-512/target-once.json'
    if sha256(marker)!=saved['marker_sha256'] or read(marker)!=binding:
        raise ValueError('extension consumed marker differs')
    startup = read(output/'startup.json')
    if (startup['passed'] is not True or startup['isolated'] is not True or startup['new_integrations']!=0
            or json.loads(startup['stdout'])!=dict(valid=True,new_integrations=0,extended_samples=7,profiles=14,reused_samples=33)
            or startup['sources']!={n:sha256(run.ROOT/n) for n in set(p['source_paths'])|set(run.INPUTS)}):
        raise ValueError('isolated extension startup differs')
    controls = run.controls()
    if controls!=read(output/'control-replay.json'):
        raise ValueError('unchanged producer controls differ')
    previous = run.inputs()
    names,extensions,progress,calls = {'binding.json','startup.json','control-replay.json'},[],[],0
    for spec in p['selection']:
        c,u = spec['candidate'],spec['u']
        rhs,_,section = run.prior.fields(c)
        profiles = []
        for method in p['solvers']:
            label = f"curve-{spec['curve']}--node-{spec['node']:02d}--{method}"
            profile = read(output/(label+'.json'))
            start = read(output/(label+'-started.json'))
            if (profile['method']!=method or start['spec']!=spec or start['method']!=method
                    or not binding['started_utc']<=start['started_utc']<=saved['completed_utc']):
                raise ValueError('extension profile start/identity differs')
            rebuilt,paths = run.previous_audit.check_profile(output,label,profile,c,u,p['numerical'],rhs,section)
            names.update(paths|{label+'.json',label+'-started.json'})
            calls+=len(paths)
            progress.append(dict(label=label,status=profile['status']))
            profiles.append(rebuilt)
        old = previous['rows'][spec['curve']]['samples'][spec['node']]
        prefixes = [run.model.prefix(a,b,p['numerical']['thresholds']) for a,b in zip(old['profiles'],profiles,strict=True)]
        extensions.append(dict(curve=spec['curve'],node=spec['node'],profiles=profiles,prefixes=prefixes))
        print(json.dumps(dict(audited_curve=spec['curve'],node=spec['node'],target_ivps=calls)),flush=True)
    result = run.model.assemble(previous,extensions,p['selection'],run.prior.load()['selection']['targets'],p['numerical'])
    for row in result['rows']:
        run.previous_audit.scalar_check(row['candidate'],row['samples'],run.prior.load()['selection']['targets'],row['analysis'])
    size = directory_bytes(output)
    if (not run.prior.public.equal(extensions,saved['extensions']) or not run.prior.public.equal(result,saved['result'])
            or names!=set(saved['files']) or progress!=saved['progress'] or calls!=saved['target_ivps']
            or calls>p['limits']['target_ivps'] or size>p['limits']['output_bytes']):
        raise ValueError('complete extension matrix/decision/accounting differs')
    return dict(experiment_id='EXP-512',passed=True,protocol_compliant=True,source_commit=binding['source_commit'],
        summary_sha256=expected_sha,plan_sha256=sha256(run.PLAN),inputs=run.INPUTS,extensions=extensions,result=result,
        target_ivps=calls,reused_target_ivps=160,output_bytes_including_summary=size,output_limit_bytes=p['limits']['output_bytes'],
        controls=controls,new_integrations=0,symbolic_chains_verified=False,paid_review=p['paid_review'],
        scope='New dense products fully replayed locally; old EXP-511 compact inputs explicitly reused, not a second raw audit of those 160 IVPs. No exact-flow or symbolic proof.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--expected-sha256',required=True)
    parser.add_argument('--output',type=Path,required=True)
    a = parser.parse_args()
    result = audit(a.run,a.expected_sha256)
    write_bounded_json(a.output.parent,a.output,result,limit_bytes=directory_bytes(a.output.parent)+16*1024**2)
    print(json.dumps(dict(passed=True,target_ivps=result['target_ivps'],audit_sha256=sha256(a.output))))


if __name__=='__main__':
    main()
