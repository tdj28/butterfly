#!/usr/bin/env python3
"""One bounded all-four fold search, seeded by an observed midpoint return."""
import argparse
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from unittest.mock import patch
from butterfly._paired_startup import inventory,sha256
from butterfly.bounded_json import directory_bytes,write_bounded_json
from scripts import run_exp512_censored_returns as previous
from scripts import verify_exp512_public_extension as public
from scripts import run_exp504_guarded_contact as control_owner
from scripts import exp517_candidate_folds as model
from scripts import exp516_ordinal_coverage as screen

ROOT=previous.ROOT
PLAN=ROOT/'experiments/manifests/EXP-517-earlier-return-folds.json'
RECEIPT='docs/experiments/receipts/EXP-512-censored-return-extension-result.json'
SCREEN='docs/experiments/receipts/EXP-516-event-ordinal-coverage-result.json'
GRAZING='docs/experiments/receipts/EXP-514-candidate-grazing-boundaries-result.json'
INPUTS=dict(previous.INPUTS,**screen.INPUTS,**{SCREEN:'45b8dd88ee0cab27d4eba7ec4c4891afdd6948ddaa83c110017ed26ac012a445',
    GRAZING:'825b6298900cf644b5b1e6e6b433c1e42bf3e791af8f0d89d90fd2ebc977d4bc'})
EXPLICIT=['scripts/run_exp517_candidate_folds.py','scripts/audit_exp517_candidate_folds.py',
    'scripts/exp517_candidate_folds.py','scripts/verify_exp512_public_extension.py',
    'tests/test_exp517_candidate_folds.py','docs/experiments/EXP-517-earlier-return-folds.md',
    'experiments/manifests/EXP-517-earlier-return-folds.json','scripts/exp513_candidate_folds.py']
coverage=previous.prior
base=coverage.base


def inputs():
    if any(sha256(ROOT/n)!=h for n,h in INPUTS.items()):
        raise ValueError('fixed public input differs')
    public.verify(ROOT/RECEIPT,INPUTS[RECEIPT])
    screen.verify(ROOT/SCREEN,INPUTS[SCREEN])
    return dict(coverage=json.loads((ROOT/RECEIPT).read_bytes()),
        screen=json.loads((ROOT/SCREEN).read_bytes()),grazing=json.loads((ROOT/GRAZING).read_bytes()))


def expected():
    return dict(experiment_id='EXP-517',status='prospective-outcome-informed-four-candidate-search',
        inputs=INPUTS,**model.selection(inputs()),targets=coverage.load()['selection']['targets'],
        numerical=base.load()['fold'],solvers=['DOP853','Radau'],attempts=1,
        seed_rule='u midpoint; regular paired census; mean observed (history+1) return time',
        controls=coverage.prior.load()['controls'],new_control_ivps=0,new_cycles=0,new_boundaries=0,
        limits=dict(target_ivps=128,wall_seconds=3600,output_bytes=2*1024**3,
            initial_free_bytes=11*1024**3,minimum_free_bytes=8*1024**3,failure_reserve_bytes=1024**2),
        paid_review='not-requested-human-approval-policy',symbolic_chains_verified=False,
        source_paths=sorted(set(previous.load()['source_paths'])|set(EXPLICIT)|set(screen.SOURCES)))


def load():
    p=json.loads(PLAN.read_bytes())
    if p!=expected():
        raise ValueError('frozen all-four plan differs')
    return p


def validate():
    p=load()
    if not base.imported()<=set(p['source_paths']):
        raise ValueError('source closure incomplete: '+str(base.imported()-set(p['source_paths'])))
    for c in p['candidates']:
        rhs,_,section=coverage.fields(c)
        for u in [*c['u_box'],c['seed_u']-c['epsilon'],c['seed_u']+c['epsilon']]:
            q=base.np.asarray(c['initial_state'])+u*base.np.asarray(c['initial_tangent'])
            f=rhs(0.,q)
            if abs(section.value(q))>1e-10 or not section.accepts(q) or f[1]>=0 or abs(f[1])/base.np.linalg.norm(f)<p['numerical']['thresholds']['angle']:
                raise ValueError('mapped initial curve is not on the valid oriented section')
    return dict(valid=True,new_integrations=0,candidates=4,maximum_target_ivps=128)


def startup(p):
    target=Path(tempfile.mkdtemp(prefix='exp517-startup-')).resolve()
    names=set(p['source_paths'])|set(INPUTS)
    for name in names:
        dest=target/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,dest)
    code=(f'import sys;from pathlib import Path;root=Path({str(target)!r});'
        f'sys.path[:0]={[str(target),str(target/"python")]!r};'
        'from scripts.run_exp517_candidate_folds import main;main();'
        'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
        'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    child=subprocess.run([sys.executable,'-I','-B','-c',code],cwd=target,capture_output=True,text=True,check=True,timeout=180)
    hashes={n:sha256(target/n) for n in sorted(names)}
    if hashes!={n:sha256(ROOT/n) for n in sorted(names)}:
        raise ValueError('isolated source changed')
    return dict(passed=True,isolated=True,new_integrations=0,sources=hashes,stdout=child.stdout,stderr=child.stderr)


def controls(p):
    return dict(dense=previous.controls(),fold_bundle=control_owner.controls(ROOT/'artifacts/EXP-502/target-69efcd3',p))


def assess(c,rows,p):
    rhs,_,section=coverage.fields(c)
    comparison=base.compare(c,rows,p['numerical'])
    return dict(comparison=comparison,**model.assessment(c,rows,comparison,p['targets'],p['numerical'],rhs,section))


@contextmanager
def retain_failed_censuses(folder,c,method):
    """Keep failed solver meshes before the inherited collector can raise."""
    original=base.section_census.solve_ivp
    ordinal=0
    def solve(*args,**kwargs):
        nonlocal ordinal
        sol=original(*args,**kwargs)
        if not sol.success or not base.np.isfinite(sol.y).all():
            base.retain_npz(folder/(c['id']+'--'+method+f'--failed-census-{ordinal}.npz'),
                dict(times=sol.t,augmented_states=sol.y.T,success=base.np.array(sol.success),nfev=base.np.array(sol.nfev)))
        ordinal+=1
        return sol
    with patch.object(base.section_census,'solve_ivp',solve):
        yield


def execute(output,source,remote):
    p=load()
    def git(*args):
        return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    if git('rev-parse','HEAD')!=source or git('status','--porcelain') or git('ls-remote','origin',remote).split()!=[source,remote]:
        raise ValueError('clean exact live-pushed source required')
    validate()
    control_result=controls(p)
    root=ROOT/'artifacts/EXP-517'
    marker=root/'target-once.json'
    output=output.resolve()
    free=shutil.disk_usage(ROOT).free
    if root not in output.parents or output.exists() or marker.exists() or free<p['limits']['initial_free_bytes']:
        raise ValueError('fresh unconsumed output and disk reserve required')
    output.mkdir(parents=True)
    binding=dict(source_commit=source,remote_ref=remote,started_utc=base.utc(),plan_sha256=sha256(PLAN),
        inputs=INPUTS,sources={n:sha256(ROOT/n) for n in p['source_paths']},initial_free_bytes=free,
        runtime=dict(python=sys.version,numpy=base.np.__version__,scipy=base.scipy.__version__),paid_review=p['paid_review'])
    start,calls=time.monotonic(),0
    progress=[]
    def save(name,value,reserve=True):
        coverage.write(output,output/name,value,p['limits'],reserve)
    def budget(integrating=False):
        nonlocal calls
        if time.monotonic()-start>p['limits']['wall_seconds'] or shutil.disk_usage(ROOT).free<p['limits']['minimum_free_bytes']:
            raise RuntimeError('EXP-517 time/free-space cap')
        if integrating:
            if calls>=p['limits']['target_ivps']:
                raise RuntimeError('EXP-517 IVP cap')
            calls+=1
    def probe(c):
        folder=output/c['id']
        folder.mkdir()
        progress.append(dict(id=c['id'],status='started'))
        rhs,jac,section=coverage.fields(c)
        profiles=[]
        for method in p['solvers']:
            label=c['id']+'/midpoint--'+method
            save(label+'-started.json',dict(candidate=c,method=method,started_utc=base.utc()))
            profile=coverage.dense.capture(c,c['seed_u'],method,p['numerical'],rhs,jac,section,
                lambda name,raw:base.retain_npz(output/(label+'--'+name+'.npz'),raw),budget)
            save(label+'.json',profile)
            profiles.append(profile)
        seeded,pair=model.seed(c,profiles,p['numerical'])
        save(c['id']+'/seed.json',dict(candidate=seeded,pair=pair))
        if seeded is None:
            progress[-1]['status']='midpoint-unqualified'
        return seeded,profiles,pair
    def shoot(c):
        rows=[]
        for method in p['solvers']:
            with retain_failed_censuses(output/c['id'],c,method):
                rows.append(base.fold_profile(output/c['id'],c,method,p['numerical'],budget))
        progress[-1]['status']='searched'
        print(json.dumps(dict(completed_candidate=c['id'],target_ivps=calls)),flush=True)
        return rows
    def timeout(*_):
        raise TimeoutError('EXP-517 wall deadline')
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p['limits']['wall_seconds'])
    try:
        save('binding.json',binding)
        save('startup.json',startup(p))
        save('control-replay.json',control_result)
        write_bounded_json(root,marker,binding,limit_bytes=directory_bytes(root)+1024**2,minimum_free_bytes=p['limits']['minimum_free_bytes'])
        with coverage.producers(base,output,p['limits']):
            rows=model.follow(p['candidates'],probe,shoot,lambda c,r:assess(c,r,p))
            for row in rows:
                save(row['candidate']['id']+'/result.json',row)
        budget()
        save('summary.json',dict(experiment_id='EXP-517',status='completed',binding=binding,rows=rows,
            target_ivps=calls,progress=progress,cross_representation=model.cross_representation(rows,p['numerical']['scales']),elapsed_seconds=time.monotonic()-start,completed_utc=base.utc(),
            marker_sha256=sha256(marker),files=inventory(output),symbolic_chains_verified=False))
        print(json.dumps(dict(completed=True,target_ivps=calls,summary_sha256=sha256(output/'summary.json'))),flush=True)
    except BaseException as exc:
        signal.alarm(0)
        save('failure.json',dict(error_type=type(exc).__name__,message=str(exc),utc=base.utc(),target_ivps=calls,
            progress=progress,files=inventory(output)),False)
        raise
    finally:
        signal.alarm(0)


def main():
    from scripts import audit_exp517_candidate_folds  # noqa: F401
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group()
    for name in ('prepare','startup','execute'):
        modes.add_argument('--'+name,action='store_true')
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--source-commit')
    parser.add_argument('--remote-ref')
    a=parser.parse_args()
    if a.prepare:
        write_bounded_json(PLAN.parent,PLAN,expected(),limit_bytes=directory_bytes(PLAN.parent)+1024**2)
    elif a.execute:
        if not all((a.output_dir,a.source_commit,a.remote_ref)):
            parser.error('output, source and remote required')
        execute(a.output_dir,a.source_commit,a.remote_ref)
    else:
        print(json.dumps(startup(load()) if a.startup else validate()))


if __name__=='__main__':
    main()
