#!/usr/bin/env python3
"""Eight-step, single-attempt warm continuation with full raw retention."""
import argparse
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

from butterfly._paired_startup import inventory,sha256,write_json
from scripts import run_exp502_joint_contact as base
from scripts import run_exp503_joint_continuation as previous
from scripts import verify_exp503_public_contact as public
from scripts import exp504_continuation_model as model

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT/'experiments/manifests/EXP-504-guarded-contact-continuation.json'
RECEIPT = 'docs/experiments/receipts/EXP-503-joint-contact-result.json'
INPUTS = {**base.INPUTS,RECEIPT:'56cf4e0d13d2f082c3272494f0ef6a4719dfd92d7d9686a74c67026c995437a7',
    'experiments/manifests/EXP-502-joint-contact-search.json':previous.BASE_SHA,
    'experiments/manifests/EXP-503-joint-contact-continuation.json':'ac90cbfa8168abd8a21e49066bc294c2102bb1542811caef9d74354eb6d515e9'}
EXPLICIT = ['scripts/run_exp504_guarded_contact.py','scripts/exp504_continuation_model.py',
    'scripts/audit_exp504_guarded_contact.py','tests/test_exp504_guarded_contact.py',
    'docs/experiments/EXP-504-guarded-contact-continuation.md','docs/experiments/EXP-504-local-design-audit.md',
    'experiments/manifests/EXP-504-guarded-contact-continuation.json','scripts/verify_exp503_public_contact.py']


def inputs():
    if any(sha256(ROOT/n) != h for n,h in INPUTS.items()):
        raise ValueError('exact public input hash differs')
    return json.loads((ROOT/RECEIPT).read_bytes())


def expected():
    inputs()
    prior = json.loads(previous.PLAN.read_bytes())
    controls = {n:v for n,v in prior['original']['files'].items() if '/' not in n or n.startswith('decimal-controls/')}
    return dict(experiment_id='EXP-504',status='prospective-outcome-informed-warm-continuation',inputs=INPUTS,
        steps=8,normalized_step_cap=10,maximum_directional_error=.1,secondary_reduction=.2,
        controls=controls,limits=dict(target_ivps=3072,wall_seconds=7200,output_bytes=10*1024**3,
            initial_free_bytes=19*1024**3,minimum_free_bytes=8*1024**3,write_margin_bytes=64*1024**2),
        paid_review='not-requested-human-approval-policy',symbolic_chains_verified=False,
        warm_seed_rule='immediately-previous-accepted-point',attempts=1)


def load():
    p = json.loads(PLAN.read_bytes())
    required = set(EXPLICIT)|set(json.loads(previous.PLAN.read_bytes())['source_paths'])
    if {k:v for k,v in p.items() if k != 'source_paths'} != expected() or not required <= set(p['source_paths']):
        raise ValueError('frozen continuation plan differs')
    return p


def controls(original,p):
    for n,record in p['controls'].items():
        path = original/n
        if path.is_symlink() or path.stat().st_size != record['bytes'] or sha256(path) != record['sha256']:
            raise ValueError('original analytic-control inventory differs')
    return previous.replay_controls(original,base.load())


def validate():
    p = load()
    public.verify(ROOT/RECEIPT,INPUTS[RECEIPT])
    state = model.initialize(base.load(),inputs())
    model.warm_plan(base.load(),inputs()['proposal'])
    if not state['check']['passed'] or not base.imported() <= set(p['source_paths']):
        raise ValueError('initial model or consumer source closure differs')
    return dict(valid=True,target_integrations=0,steps=8,variants=256)


def startup(p):
    target = Path(tempfile.mkdtemp(prefix='exp504-startup-')).resolve()
    names = set(p['source_paths'])|set(INPUTS)
    for name in names:
        destination = target/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,destination)
    code = (f'import sys;from pathlib import Path;root=Path({str(target)!r});sys.path[:0]={[str(target),str(target/"python")]!r};'
        'from scripts.run_exp504_guarded_contact import main;main();'
        'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
        'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    child = subprocess.run([sys.executable,'-I','-B','-c',code],cwd=target,capture_output=True,text=True,check=True,timeout=120)
    if any(sha256(ROOT/n) != sha256(target/n) for n in names):
        raise ValueError('copied source changed')
    return dict(passed=True,isolated=True,target_integrations=0,stdout=child.stdout,stderr=child.stderr,
        sources={n:sha256(target/n) for n in sorted(names)})


def execute(output,original,source,remote):
    p = load()
    def git(*args):
        return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    if (git('rev-parse','HEAD') != source or git('status','--porcelain')
            or git('ls-remote','origin',remote).split() != [source,remote]):
        raise ValueError('clean live-pushed exact source required')
    validate()
    output = output.resolve()
    marker = ROOT/'artifacts/EXP-504/target-once.json'
    if ROOT/'artifacts/EXP-504' not in output.parents or output.exists() or marker.exists():
        raise ValueError('fresh output and unconsumed marker required')
    free = shutil.disk_usage(ROOT).free
    if free < p['limits']['initial_free_bytes']:
        raise ValueError('initial free space reserve')
    output.mkdir(parents=True)
    binding = dict(source_commit=source,remote_ref=remote,started_utc=base.utc(),plan_sha256=sha256(PLAN),inputs=INPUTS,
        sources={n:sha256(ROOT/n) for n in p['source_paths']},initial_free_bytes=free,
        runtime=dict(python=sys.version,numpy=base.np.__version__,scipy=base.scipy.__version__),paid_review=p['paid_review'])
    write_json(output/'binding.json',binding)
    start,calls,checks = time.monotonic(),0,0
    progress = model.ledger()
    def budget(integrating=False):
        nonlocal calls,checks
        checks += 1
        if integrating or checks % 1024 == 1:
            if (time.monotonic()-start > p['limits']['wall_seconds']
                    or shutil.disk_usage(ROOT).free < p['limits']['minimum_free_bytes']
                    or sum(f.stat().st_size for f in output.rglob('*') if f.is_file()) >
                        p['limits']['output_bytes']-p['limits']['write_margin_bytes']):
                raise base.previous.cycles_run.BudgetStop('EXP-504 time/storage cap')
        if integrating:
            if calls >= p['limits']['target_ivps']:
                raise base.previous.cycles_run.BudgetStop('EXP-504 target IVP cap')
            calls += 1
    def timeout(*_):
        raise base.previous.cycles_run.BudgetStop('EXP-504 wall deadline')
    def completed(entry):
        write_json(output/(entry['point']['spec']['id']+'-decision.json'),entry['decision'])
        print(json.dumps(dict(completed_point=entry['point']['spec']['id'],target_ivps=calls,
            accepted=entry['decision']['accepted'])),flush=True)
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p['limits']['wall_seconds'])
    try:
        write_json(output/'startup.json',startup(p))
        write_json(output/'control-replay.json',controls(original,p))
        budget(False)
        write_json(marker,binding)
        result = model.follow(base.load(),inputs(),lambda numerical,spec:base.evaluate(numerical,spec,output/spec['id'],budget),
            progress,completed)
        budget(False)
        write_json(output/'summary.json',dict(experiment_id='EXP-504',status='completed',binding=binding,
            result=result,progress=progress,ledger=base.load()['ledger'],target_ivps=calls,
            elapsed_seconds=time.monotonic()-start,completed_utc=base.utc(),files=inventory(output),
            marker_sha256=sha256(marker),symbolic_chains_verified=False))
        print(json.dumps(dict(completed=True,target_ivps=calls,summary_sha256=sha256(output/'summary.json'))),flush=True)
    except BaseException as exc:
        signal.alarm(0)
        for slot in progress:
            if slot['status'] == 'not-run' and slot['reason'] is None:
                slot['reason'] = 'attempt interrupted: '+type(exc).__name__
        write_json(output/'failure.json',dict(error_type=type(exc).__name__,message=str(exc),utc=base.utc(),
            target_ivps=calls,progress=progress,files=inventory(output)))
        raise
    finally:
        signal.alarm(0)


def main():
    from scripts import audit_exp504_guarded_contact  # noqa: F401
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--prepare',action='store_true')
    mode.add_argument('--startup',action='store_true')
    mode.add_argument('--execute',action='store_true')
    parser.add_argument('--original-run',type=Path)
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--source-commit')
    parser.add_argument('--remote-ref')
    a = parser.parse_args()
    if a.prepare:
        p = expected()
        p['source_paths'] = sorted(set(EXPLICIT)|set(json.loads(previous.PLAN.read_bytes())['source_paths'])|base.imported())
        write_json(PLAN,p)
    elif a.execute:
        if not all((a.original_run,a.output_dir,a.source_commit,a.remote_ref)):
            parser.error('original controls, output, source and remote ref required')
        execute(a.output_dir,a.original_run,a.source_commit,a.remote_ref)
    else:
        print(json.dumps(startup(load()) if a.startup else validate()))


if __name__ == '__main__':
    main()
