#!/usr/bin/env python3
"""Replay every direct-curve dense polynomial, event and sampling decision."""
import argparse
import json
import math
from pathlib import Path
import numpy as np
from butterfly._paired_startup import inventory,sha256
from butterfly.bounded_json import directory_bytes,write_bounded_json
from scripts import run_exp511_curve_coverage as run


def read(path):
    return json.loads(path.read_bytes())


def raw(path):
    with np.load(path,allow_pickle=False) as saved:
        return {n:saved[n] for n in saved.files}


def check_profile(folder,label,profile,c,u,settings,rhs,section):
    raws = {name:raw(folder/(label+'--'+name+'.npz')) for name in profile['products']}
    rebuilt = run.dense.replay(profile,c,u,settings,rhs,section,raws)
    if not run.public.equal(rebuilt,profile):
        raise ValueError('dense census/measurement replay differs')
    return rebuilt,{label+'--'+n+'.npz' for n in raws}


def audit_controls(output):
    p = run.load()
    saved = read(output/'summary.json')
    if (saved['passed'] is not True or saved['control_ivps']!=12 or len(saved['rows'])!=6
            or saved['source_hashes']!={n:sha256(run.ROOT/n) for n in p['source_paths']}
            or saved['files']!=inventory(output,omit=('summary.json',))
            or directory_bytes(output)>p['controls']['output_bytes']
            or not 0<=saved['elapsed_seconds']<=p['controls']['wall_seconds']):
        raise ValueError('analytic control binding/matrix/resource differs')
    rows,names = [],set()
    for kind in p['controls']['kinds']:
        c,u,settings,(rhs,_,section),k = run.control_case(kind)
        for method in p['solvers']:
            label = kind+'--'+method
            row = read(output/(label+'.json'))
            if row['kind']!=kind or row['profile']['method']!=method:
                raise ValueError('control identity differs')
            rebuilt,paths = check_profile(output,label,row['profile'],c,u,settings,rhs,section)
            verdict = run.control_verdict(rebuilt,c,u,k)
            if not run.public.equal(verdict,row['verdict']):
                raise ValueError('analytic control verdict differs')
            names.update(paths|{label+'.json'})
            rows.append(row)
    if rows!=saved['rows'] or names!=set(saved['files']):
        raise ValueError('complete control inventory differs')
    return dict(passed=True,control_ivps=12,new_integrations=0,summary_sha256=sha256(output/'summary.json'),
        source_hashes=saved['source_hashes'],rows=[dict(kind=r['kind'],method=r['profile']['method'],verdict=r['verdict']) for r in rows],
        full_dense_replay=True)


def scalar_check(c,samples,targets,analysis):
    """Separate scalar state distances and endpoint-sign bracket comparisons."""
    for item in analysis['per_method']:
        obs = []
        for sample in samples:
            profile = next(p for p in sample['profiles'] if p['method']==item['method'])
            obs.append(profile['measurement']['observation'] if profile['status']=='completed' else dict(valid=False))
        brackets = []
        def connected(indices):
            if not all(samples[i]['pair']['regular'] and obs[i]['valid'] for i in indices):
                return False
            return len({obs[i]['input_x_tangent']>0 for i in indices})==1
        for i in range(len(samples)-1):
            if connected([i,i+1]) and obs[i]['x_graph_slope']*obs[i+1]['x_graph_slope']<0:
                brackets.append([i,i+1])
        for i in range(1,len(samples)-1):
            if connected([i-1,i,i+1]) and obs[i]['x_graph_slope']==0 and obs[i-1]['x_graph_slope']*obs[i+1]['x_graph_slope']<0:
                brackets.append([i-1,i+1])
        if sorted(brackets)!=item['candidate_brackets']:
            raise ValueError('separate scalar bracket analysis differs')
        for row in item['distances']:
            o = obs[row['index']]
            for key,field in [('image_state','input_distances'),('next_state','output_distances')]:
                distances = [max(abs(o[key][i]-t[key][i])/scale for i,scale in enumerate([15.,15.,.01])) for t in targets]
                if any(not math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-13) for a,b in zip(distances,row[field],strict=True)):
                    raise ValueError('separate scalar state distances differ')


def audit(output,expected_sha,control_output):
    p = run.load()
    if sha256(output/'summary.json')!=expected_sha:
        raise ValueError('target summary byte identity differs')
    saved,binding = read(output/'summary.json'),read(output/'binding.json')
    if (saved['experiment_id']!='EXP-511' or saved['status']!='completed' or saved['binding']!=binding
            or binding['sources']!={n:sha256(run.ROOT/n) for n in p['source_paths']}
            or binding['inputs']!=run.INPUTS or binding['plan_sha256']!=sha256(run.PLAN)
            or binding['paid_review']!=p['paid_review'] or saved['symbolic_chains_verified'] is not False
            or binding['initial_free_bytes']<p['limits']['initial_free_bytes']
            or saved['files']!=inventory(output,omit=('summary.json',))
            or not binding['started_utc']<=saved['completed_utc']
            or not 0<=saved['elapsed_seconds']<=p['limits']['wall_seconds']):
        raise ValueError('source/input/raw/resource/claim binding differs')
    marker = run.ROOT/'artifacts/EXP-511/target-once.json'
    if sha256(marker)!=saved['marker_sha256'] or read(marker)!=binding:
        raise ValueError('consumed marker differs')
    startup = read(output/'startup.json')
    expected_start = dict(valid=True,new_integrations=0,curves=2,profiles=sum(len(c['grid'])*2 for c in p['selection']['curves']))
    if (startup['passed'] is not True or startup['isolated'] is not True or startup['new_integrations']!=0
            or json.loads(startup['stdout'])!=expected_start
            or startup['sources']!={n:sha256(run.ROOT/n) for n in set(p['source_paths'])|set(run.INPUTS)}):
        raise ValueError('isolated startup differs')
    control = audit_controls(control_output)
    if control!=read(output/'control-replay.json'):
        raise ValueError('control replay differs')
    names,rows,progress,calls = {'binding.json','startup.json','control-replay.json'},[],[],0
    for i,c in enumerate(p['selection']['curves']):
        folder = output/f'curve-{i}'
        rhs,_,section = run.fields(c)
        samples = []
        for j,u in enumerate(c['grid']):
            profiles = []
            for method in p['solvers']:
                label = f'node-{j:02d}--'+method
                profile = read(folder/(label+'.json'))
                start = read(folder/(label+'-started.json'))
                if (profile['method']!=method or {k:start[k] for k in ('u','method')}!=dict(u=u,method=method)
                        or not binding['started_utc']<=start['started_utc']<=saved['completed_utc']):
                    raise ValueError('profile identity/start differs')
                rebuilt,paths = check_profile(folder,label,profile,c,u,p['numerical'],rhs,section)
                names.update(f'curve-{i}/'+n for n in paths|{label+'.json',label+'-started.json'})
                calls+=len(paths)
                progress.append(dict(curve=i,node=j,method=method,status=profile['status']))
                profiles.append(rebuilt)
            samples.append(dict(u=u,profiles=profiles,pair=run.model.pair(profiles,p['numerical']['scales'])))
        analysis = run.model.analyze(c,samples,p['selection']['targets'])
        scalar_check(c,samples,p['selection']['targets'],analysis)
        row = dict(candidate=c,samples=samples,analysis=analysis)
        if not run.public.equal(row,read(folder/'result.json')):
            raise ValueError('complete curve replay differs')
        names.add(f'curve-{i}/result.json')
        rows.append(row)
        print(json.dumps(dict(audited_curve=i,target_ivps=calls)),flush=True)
    size = directory_bytes(output)
    if (not run.public.equal(rows,saved['rows']) or names!=set(saved['files']) or progress!=saved['progress']
            or calls!=saved['target_ivps'] or calls>p['limits']['target_ivps'] or size>p['limits']['output_bytes']):
        raise ValueError('complete decision/count/output quota differs')
    return dict(experiment_id='EXP-511',passed=True,protocol_compliant=True,source_commit=binding['source_commit'],
        summary_sha256=expected_sha,plan_sha256=sha256(run.PLAN),inputs=run.INPUTS,rows=rows,controls=control,
        target_ivps=calls,output_bytes_including_summary=size,output_limit_bytes=p['limits']['output_bytes'],
        new_integrations=0,symbolic_chains_verified=False,paid_review=p['paid_review'],
        scope='Full local dense-polynomial, event, tangent and grid replay plus scalar comparisons. Same-code local audit, not independent-team replication or an exact-flow/global root-absence proof.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--expected-sha256',required=True)
    parser.add_argument('--control-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    a = parser.parse_args()
    result = audit(a.run,a.expected_sha256,a.control_dir)
    write_bounded_json(a.output.parent,a.output,result,limit_bytes=directory_bytes(a.output.parent)+16*1024**2)
    print(json.dumps(dict(passed=True,target_ivps=result['target_ivps'],audit_sha256=sha256(a.output))))


if __name__=='__main__':
    main()
