#!/usr/bin/env python3
"""Bounded prospective transport of all four recovered fold constructions."""
import argparse
import json
import math
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

from butterfly._paired_startup import inventory,sha256
from butterfly.bounded_json import directory_bytes,write_bounded_json
from scripts import run_exp517_candidate_folds as prior
from scripts import verify_exp517_public_folds as public
from scripts import run_exp510_fold_transport as transport
from scripts import exp518_fold_transport as model

ROOT=prior.ROOT
PLAN=ROOT/'experiments/manifests/EXP-518-recovered-fold-transport.json'
RECEIPT='docs/experiments/receipts/EXP-517-earlier-return-folds-result.json'
INPUTS=dict(prior.INPUTS,**{RECEIPT:'0c1233986f4ac6463d8ded47ce0a92353a98a86a889089a3f2bafe78742adf76'})
EXPLICIT=['scripts/run_exp518_fold_transport.py','scripts/audit_exp518_fold_transport.py',
    'scripts/exp518_fold_transport.py','scripts/verify_exp517_public_folds.py',
    'tests/test_exp518_fold_transport.py','docs/experiments/EXP-518-recovered-fold-transport.md',
    'experiments/manifests/EXP-518-recovered-fold-transport.json']
base=prior.base
coverage=prior.coverage


def inputs():
    if any(sha256(ROOT/n)!=h for n,h in INPUTS.items()):
        raise ValueError('fixed source input differs')
    public.verify(ROOT/RECEIPT,INPUTS[RECEIPT])
    saved=json.loads((ROOT/RECEIPT).read_bytes())
    if not saved['cross_representation']['all_references_restored']:
        raise ValueError('complete restored EXP-517 anchor required')
    return saved['rows']


def expected():
    start=inputs()
    parent=prior.load()
    return dict(experiment_id='EXP-518',status='prospective-outcome-informed-two-stage-transport',
        inputs=INPUTS,specifications=model.specifications(transport.load()['specifications'],model.matrix(start)),
        numerical=parent['numerical'],historical_targets=parent['targets'],solvers=['DOP853','Radau'],attempts=1,
        substeps=2,folds_per_step=4,new_cycles=0,new_boundaries=0,
        controls=parent['controls'],new_control_ivps=0,
        limits=dict(target_ivps=256,wall_seconds=3600,output_bytes=2*1024**3,
            initial_free_bytes=11*1024**3,minimum_free_bytes=8*1024**3,failure_reserve_bytes=1024**2),
        paid_review='not-requested-human-approval-policy',symbolic_chains_verified=False,
        source_paths=sorted(set(parent['source_paths'])|set(EXPLICIT)))


def load():
    saved=json.loads(PLAN.read_bytes())
    if saved!=expected():raise ValueError('frozen two-stage transport plan differs')
    return saved


def validate():
    p=load()
    if not base.imported()<=set(p['source_paths']):
        raise ValueError('complete deployed import closure required: '+str(base.imported()-set(p['source_paths'])))
    start=inputs();spec=p['specifications'][0]
    model.candidates(start,spec,transport.offset(spec['parameters']))
    return dict(valid=True,new_integrations=0,maximum_substeps=2,folds_per_step=4,maximum_target_ivps=256)


def startup(p):
    target=Path(tempfile.mkdtemp(prefix='exp518-startup-')).resolve()
    names=set(p['source_paths'])|set(INPUTS)
    for name in names:
        dest=target/name;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,dest)
    code=(f'import sys;from pathlib import Path;root=Path({str(target)!r});'
          f'sys.path[:0]={[str(target),str(target/"python")]!r};'
          'from scripts.run_exp518_fold_transport import main;main();'
          'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
          'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    child=subprocess.run([sys.executable,'-I','-B','-c',code],cwd=target,capture_output=True,text=True,check=True,timeout=240)
    hashes={n:sha256(target/n) for n in sorted(names)}
    if hashes!={n:sha256(ROOT/n) for n in sorted(names)}:raise ValueError('isolated source changed')
    return dict(passed=True,isolated=True,new_integrations=0,sources=hashes,stdout=child.stdout,stderr=child.stderr)


def assess(c,profiles,p):
    """Same local fold and all-prefix qualification; no old-state restoration gate."""
    rhs,_,section=coverage.fields(c)
    comparison=base.compare(c,profiles,p['numerical'])
    # The inherited routine separately computes a reference-restoration label.
    # Those old fixed-parameter distances do not define transport acceptance;
    # keep them explicitly as historical diagnostics, never relabel as passes.
    old=prior.model.assessment(c,profiles,comparison,p['historical_targets'],p['numerical'],rhs,section)
    return dict(qualified=bool(old['qualified'] and comparison['qualified_in_region']),comparison=comparison,prefix_pairs=old['prefix_pairs'],
                historical_fixed_parameter_reference=dict(restored=old['reference_restored'],distances=old['reference_distances']),
                symbolic_chains_verified=False)


def midpoint_seed(c,profiles,p):
    pair=coverage.model.pair(profiles,p['numerical']['scales'])
    if not pair['regular']:return None,pair
    t=math.fsum(v['measurement']['image']['events'][-1]['time'] for v in profiles)/2
    if not c['time_box'][0]<t<c['time_box'][1]:
        return None,dict(pair,seed_failure='observed-midpoint-outside-fixed-time-box')
    return dict(c,seed_time=t),pair


def endpoint(result):
    if not result['transport_completed']:return None
    rows=result['rows'][-1]['rows']
    old=transport.inputs()
    if (len(result['rows'])!=2 or result['rows'][-1]['spec']['parameters']!=old['spec']['parameters']
            or model.matrix(rows)!=old['spec']['parameters']):
        raise ValueError('new folds and reused cycle must share the exact endpoint parameters')
    folds=[dict(r['assessment']['comparison'],parent_id=r['candidate']['parent_id']) for r in rows]
    contact=base.previous.measure(folds,old['cycle'],base.load())
    return dict(contact=contact,fold_proximity=contact['envelope']['pair_state_distance'][3]<=1e-4,
        reused_point_sha256=transport.prior.POINT_SHA,
        boundary_distance=old['boundary_analysis']['cycle_indices'][1]['maximum_distance'],
        scope='New folds, explicitly reused qualified endpoint cycle and boundary context; no new complete joint point.')


def execute(output,source,remote):
    p=load()
    def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    if git('rev-parse','HEAD')!=source or git('status','--porcelain') or git('ls-remote','origin',remote).split()!=[source,remote]:
        raise ValueError('clean exact live-pushed source required')
    validate();start_rows=inputs();controls=prior.controls(p)
    root=ROOT/'artifacts/EXP-518';marker=root/'target-once.json';output=output.resolve()
    free=shutil.disk_usage(ROOT).free
    if root not in output.parents or output.exists() or marker.exists() or free<p['limits']['initial_free_bytes']:
        raise ValueError('fresh unconsumed output and disk reserve required')
    output.mkdir(parents=True)
    binding=dict(source_commit=source,remote_ref=remote,started_utc=base.utc(),plan_sha256=sha256(PLAN),
        inputs=INPUTS,sources={n:sha256(ROOT/n) for n in p['source_paths']},initial_free_bytes=free,
        runtime=dict(python=sys.version,numpy=base.np.__version__,scipy=base.scipy.__version__),paid_review=p['paid_review'])
    started,calls=time.monotonic(),0;progress=[]
    def save(name,value,reserve=True):coverage.write(output,output/name,value,p['limits'],reserve)
    def budget(integrating=False):
        nonlocal calls
        if time.monotonic()-started>p['limits']['wall_seconds'] or shutil.disk_usage(ROOT).free<p['limits']['minimum_free_bytes']:
            raise RuntimeError('EXP-518 time/free-space cap')
        if integrating:
            if calls>=p['limits']['target_ivps']:raise RuntimeError('EXP-518 IVP cap')
            calls+=1
    def measure(spec,candidates):
        stage=output/spec['id'];stage.mkdir();progress.append(dict(id=spec['id'],status='started'))
        save(spec['id']+'/inputs.json',dict(spec=spec,candidates=candidates))
        def probe(c):
            folder=stage/c['id'];folder.mkdir();profiles=[]
            rhs,jac,section=coverage.fields(c)
            for method in p['solvers']:
                label=spec['id']+'/'+c['id']+'/midpoint--'+method
                save(label+'-started.json',dict(candidate=c,method=method,started_utc=base.utc()))
                profile=coverage.dense.capture(c,c['seed_u'],method,p['numerical'],rhs,jac,section,
                    lambda name,raw:base.retain_npz(output/(label+'--'+name+'.npz'),raw),budget)
                save(label+'.json',profile);profiles.append(profile)
            seeded,pair=midpoint_seed(c,profiles,p)
            save(spec['id']+'/'+c['id']+'/seed.json',dict(candidate=seeded,pair=pair))
            return seeded,profiles,pair
        def shoot(c):
            profiles=[]
            for method in p['solvers']:
                with prior.retain_failed_censuses(stage/c['id'],c,method):
                    profiles.append(base.fold_profile(stage/c['id'],c,method,p['numerical'],budget))
            return profiles
        rows=prior.model.follow(candidates,probe,shoot,lambda c,r:assess(c,r,p))
        for row in rows:save(spec['id']+'/'+row['candidate']['id']+'/result.json',row)
        save(spec['id']+'/rows.json',rows);progress[-1]['status']='completed'
        print(json.dumps(dict(completed_substep=spec['id'],target_ivps=calls,
            qualified=sum(bool(r['assessment'] and r['assessment']['qualified']) for r in rows))),flush=True)
        return rows
    def timeout(*_):raise TimeoutError('EXP-518 wall deadline')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(p['limits']['wall_seconds'])
    try:
        save('binding.json',binding);save('startup.json',startup(p));save('control-replay.json',controls)
        write_bounded_json(root,marker,binding,limit_bytes=directory_bytes(root)+1024**2,minimum_free_bytes=p['limits']['minimum_free_bytes'])
        with coverage.producers(base,output,p['limits']):
            result=model.follow(start_rows,p['specifications'],transport.offset,measure)
        budget()
        save('summary.json',dict(experiment_id='EXP-518',status='completed',binding=binding,result=result,
            endpoint_comparison=endpoint(result),stage_progress=progress,target_ivps=calls,
            elapsed_seconds=time.monotonic()-started,completed_utc=base.utc(),files=inventory(output),
            marker_sha256=sha256(marker),symbolic_chains_verified=False))
        print(json.dumps(dict(completed=True,target_ivps=calls,summary_sha256=sha256(output/'summary.json'))),flush=True)
    except BaseException as exc:
        signal.alarm(0)
        save('failure.json',dict(error_type=type(exc).__name__,message=str(exc),utc=base.utc(),target_ivps=calls,
            stage_progress=progress,files=inventory(output)),False)
        raise
    finally:signal.alarm(0)


def main():
    from scripts import audit_exp518_fold_transport  # noqa: F401
    p=argparse.ArgumentParser(description=__doc__);modes=p.add_mutually_exclusive_group()
    for name in ('prepare','startup','execute'):modes.add_argument('--'+name,action='store_true')
    p.add_argument('--output-dir',type=Path);p.add_argument('--source-commit');p.add_argument('--remote-ref')
    a=p.parse_args()
    if a.prepare:write_bounded_json(PLAN.parent,PLAN,expected(),limit_bytes=directory_bytes(PLAN.parent)+1024**2)
    elif a.execute:
        if not all((a.output_dir,a.source_commit,a.remote_ref)):p.error('output, source and remote required')
        execute(a.output_dir,a.source_commit,a.remote_ref)
    else:print(json.dumps(startup(load()) if a.startup else validate()))


if __name__=='__main__':main()
