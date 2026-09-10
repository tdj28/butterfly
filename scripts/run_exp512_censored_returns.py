#!/usr/bin/env python3
"""One bounded observation-window extension, not a reset of EXP-511."""
import argparse
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from butterfly._paired_startup import inventory,sha256
from butterfly.bounded_json import directory_bytes,write_bounded_json
from scripts import run_exp511_curve_coverage as prior
from scripts import audit_exp511_curve_coverage as previous_audit
from scripts import verify_exp511_public_coverage as public
from scripts import exp512_censored_returns as model

ROOT = prior.ROOT
PLAN = ROOT/'experiments/manifests/EXP-512-censored-return-extension.json'
RECEIPT = 'docs/experiments/receipts/EXP-511-direct-curve-coverage-result.json'
INPUTS = dict(prior.INPUTS,**{RECEIPT:'245610c6116eed25f76bc775cc77be6cce66eacd4193d466a069c23b1892eb85'})
EXPLICIT = ['scripts/run_exp512_censored_returns.py','scripts/audit_exp512_censored_returns.py',
    'scripts/exp512_censored_returns.py','tests/test_exp512_censored_returns.py',
    'scripts/verify_exp511_public_coverage.py','tests/test_exp511_public_coverage.py',
    'docs/experiments/EXP-512-censored-return-extension.md','experiments/manifests/EXP-512-censored-return-extension.json']


def inputs():
    if any(sha256(ROOT/n)!=h for n,h in INPUTS.items()):
        raise ValueError('fixed extension inputs differ')
    public.verify(ROOT/RECEIPT,INPUTS[RECEIPT])
    return json.loads((ROOT/RECEIPT).read_bytes())


def expected():
    return dict(experiment_id='EXP-512',status='prospective-outcome-informed-window-extension',
        inputs=INPUTS,selection=model.selection(inputs()),solvers=['DOP853','Radau'],attempts=1,
        horizon_increment=15.,numerical=prior.load()['numerical'],newton_refinements=0,
        reused_samples=33,extended_samples=7,new_control_ivps=0,paid_review='not-requested-human-approval-policy',
        limits=dict(target_ivps=28,wall_seconds=900,output_bytes=512*1024**2,
            initial_free_bytes=9*1024**3,minimum_free_bytes=8*1024**3,failure_reserve_bytes=1024**2),
        symbolic_chains_verified=False,source_paths=sorted(set(prior.load()['source_paths'])|set(EXPLICIT)))


def load():
    p = json.loads(PLAN.read_bytes())
    if p!=expected():
        raise ValueError('frozen horizon extension plan differs')
    return p


def validate():
    p = load()
    if not prior.base.imported()<=set(p['source_paths']):
        raise ValueError('extension source closure incomplete')
    return dict(valid=True,new_integrations=0,extended_samples=7,profiles=14,reused_samples=33)


def startup(p):
    target = Path(tempfile.mkdtemp(prefix='exp512-startup-')).resolve()
    names = set(p['source_paths'])|set(INPUTS)
    for name in names:
        destination = target/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,destination)
    code = (f'import sys;from pathlib import Path;root=Path({str(target)!r});'
        f'sys.path[:0]={[str(target),str(target/"python")]!r};'
        'from scripts.run_exp512_censored_returns import main;main();'
        'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
        'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    child = subprocess.run([sys.executable,'-I','-B','-c',code],cwd=target,capture_output=True,text=True,check=True,timeout=120)
    hashes = {n:sha256(target/n) for n in sorted(names)}
    if hashes!={n:sha256(ROOT/n) for n in sorted(names)}:
        raise ValueError('isolated extension source changed')
    return dict(passed=True,isolated=True,new_integrations=0,sources=hashes,stdout=child.stdout,stderr=child.stderr)


def controls():
    # Actual capture/dense replay producers are byte-identical to EXP-511.
    return previous_audit.audit_controls(ROOT/'artifacts/EXP-511/preflight-controls-01')


def execute(output,source,remote):
    p = load()
    def git(*args):
        return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    if git('rev-parse','HEAD')!=source or git('status','--porcelain') or git('ls-remote','origin',remote).split()!=[source,remote]:
        raise ValueError('clean exact live-pushed source required')
    validate()
    control_result = controls()
    previous = inputs()
    root = ROOT/'artifacts/EXP-512'
    marker = root/'target-once.json'
    output = output.resolve()
    free = shutil.disk_usage(ROOT).free
    if root not in output.parents or output.exists() or marker.exists():
        raise ValueError('fresh output and unconsumed extension attempt required')
    if free<p['limits']['initial_free_bytes']:
        raise ValueError('initial disk reserve')
    output.mkdir(parents=True)
    binding = dict(source_commit=source,remote_ref=remote,started_utc=prior.base.utc(),plan_sha256=sha256(PLAN),
        inputs=INPUTS,sources={n:sha256(ROOT/n) for n in p['source_paths']},initial_free_bytes=free,
        runtime=dict(python=sys.version,numpy=prior.np.__version__,scipy=prior.base.scipy.__version__),paid_review=p['paid_review'])
    start,calls = time.monotonic(),0
    progress,extensions = [],[]
    def save(name,value,reserve=True):
        prior.write(output,output/name,value,p['limits'],reserve)
    def budget(integrating=False):
        nonlocal calls
        if time.monotonic()-start>p['limits']['wall_seconds'] or shutil.disk_usage(ROOT).free<p['limits']['minimum_free_bytes']:
            raise RuntimeError('EXP-512 time/free-space cap')
        if integrating:
            if calls>=p['limits']['target_ivps']:
                raise RuntimeError('EXP-512 IVP cap')
            calls+=1
    def timeout(*_):
        raise TimeoutError('EXP-512 wall deadline')
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p['limits']['wall_seconds'])
    try:
        save('binding.json',binding)
        save('startup.json',startup(p))
        save('control-replay.json',control_result)
        write_bounded_json(root,marker,binding,limit_bytes=directory_bytes(root)+1024**2,minimum_free_bytes=p['limits']['minimum_free_bytes'])
        with prior.producers(prior.base,output,p['limits']):
            for spec in p['selection']:
                c,u = spec['candidate'],spec['u']
                rhs,jac,section = prior.fields(c)
                profiles = []
                for method in p['solvers']:
                    label = f"curve-{spec['curve']}--node-{spec['node']:02d}--{method}"
                    progress.append(dict(label=label,status='started'))
                    save(label+'-started.json',dict(spec=spec,method=method,started_utc=prior.base.utc()))
                    profile = prior.dense.capture(c,u,method,p['numerical'],rhs,jac,section,
                        lambda name,raw:prior.base.retain_npz(output/(label+'--'+name+'.npz'),raw),budget)
                    save(label+'.json',profile)
                    progress[-1]['status']=profile['status']
                    profiles.append(profile)
                old = previous['rows'][spec['curve']]['samples'][spec['node']]
                prefixes = [model.prefix(a,b,p['numerical']['thresholds']) for a,b in zip(old['profiles'],profiles,strict=True)]
                extensions.append(dict(curve=spec['curve'],node=spec['node'],profiles=profiles,prefixes=prefixes))
                print(json.dumps(dict(curve=spec['curve'],node=spec['node'],target_ivps=calls,
                    prefixes_passed=all(v['passed'] for v in prefixes))),flush=True)
        result = model.assemble(previous,extensions,p['selection'],prior.load()['selection']['targets'],p['numerical'])
        budget()
        save('summary.json',dict(experiment_id='EXP-512',status='completed',binding=binding,extensions=extensions,result=result,
            target_ivps=calls,progress=progress,elapsed_seconds=time.monotonic()-start,completed_utc=prior.base.utc(),
            marker_sha256=sha256(marker),files=inventory(output),symbolic_chains_verified=False))
        print(json.dumps(dict(completed=True,target_ivps=calls,summary_sha256=sha256(output/'summary.json'))),flush=True)
    except BaseException as exc:
        signal.alarm(0)
        save('failure.json',dict(error_type=type(exc).__name__,message=str(exc),utc=prior.base.utc(),
            target_ivps=calls,progress=progress,files=inventory(output)),False)
        raise
    finally:
        signal.alarm(0)


def main():
    from scripts import audit_exp512_censored_returns  # noqa: F401
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    for name in ('prepare','startup','execute'):
        modes.add_argument('--'+name,action='store_true')
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--source-commit')
    parser.add_argument('--remote-ref')
    a = parser.parse_args()
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
