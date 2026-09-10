#!/usr/bin/env python3
"""Bounded one-step predictor/corrector continuation with complete raw retention."""
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
from scripts import run_exp507_fold_restoration as prior
from scripts import verify_exp507_public_restoration as public
from scripts import exp508_constrained_step as model

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT/'experiments/manifests/EXP-508-constrained-contact-step.json'
RECEIPT = 'docs/experiments/receipts/EXP-507-fixed-c-fold-restoration-result.json'
INPUTS = {**prior.INPUTS,RECEIPT:'b6d550882b761fb499a9b6e3f4d415aa05c0dc1d1f98f424bcffc2dacaba386d',
    'experiments/manifests/EXP-507-fixed-c-fold-restoration.json':'ac1ea02269f66d1ac005be552a6c8dbb1f7b0536ef94c02d1bbdce812b990788'}
EXPLICIT = ['scripts/run_exp508_constrained_step.py','scripts/audit_exp508_constrained_step.py',
    'scripts/exp508_constrained_step.py','tests/test_exp508_constrained_step.py',
    'docs/experiments/EXP-508-constrained-contact-step.md',
    'experiments/manifests/EXP-508-constrained-contact-step.json','scripts/verify_exp507_public_restoration.py']
base = prior.prior.base


def inputs():
    if any(sha256(ROOT/n) != h for n,h in INPUTS.items()):
        raise ValueError('historical public inputs changed')
    saved = json.loads((ROOT/RECEIPT).read_bytes())
    if not saved['decision']['fold_restored'] or saved['decision']['joint_proximity']:
        raise ValueError('qualified restored nonjoint starting point required')
    return saved['point']


def expected():
    state = model.initialize(base.load(),prior.prior.inputs(),prior.inputs(),inputs())
    return dict(experiment_id='EXP-508',status='prospective-outcome-informed-predictor-corrector',inputs=INPUTS,
        model_recipe='measured EXP-504/507 a secant plus original fine c column; diagnostics retained at execution',
        maximum_a_column_relative_change=.1,
        predictor=model.proposal(state,inputs(),base.load()['anchor'],'predictor'),
        maximum_points=2,attempts=1,c_step=-.02,a_normalized_bound=.1,correction_scalar_floor=1e-12,
        controls=prior.load()['controls'],primary_radius=1e-4,
        limits=dict(target_ivps=1024,wall_seconds=3600,output_bytes=3*1024**3,
            initial_free_bytes=12*1024**3,minimum_free_bytes=8*1024**3,failure_reserve_bytes=1024**2),
        paid_review='not-requested-human-approval-policy',symbolic_chains_verified=False,
        acceptance='complete prescribed stages; all original/start/adjacent identities; fold proximity; lower worst full-state boundary gap and lower absolute boundary residual in every correlated variant')


def load():
    p = json.loads(PLAN.read_bytes())
    if ({k:v for k,v in p.items() if k != 'source_paths'} != expected()
            or not set(EXPLICIT)|set(prior.load()['source_paths']) <= set(p['source_paths'])):
        raise ValueError('frozen constrained-step plan differs')
    return p


def validate():
    p = load()
    public.verify(ROOT/RECEIPT,INPUTS[RECEIPT])
    if not p['predictor']['qualified'] or not base.imported() <= set(p['source_paths']):
        raise ValueError('initial predictor or source closure differs')
    prior.prior.model.warm_plan(base.load(),inputs())
    return dict(valid=True,target_integrations=0,maximum_points=2,variants=256)


def startup(p):
    target = Path(tempfile.mkdtemp(prefix='exp508-startup-')).resolve()
    names = set(p['source_paths'])|set(INPUTS)
    for name in names:
        destination = target/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,destination)
    code = (f'import sys;from pathlib import Path;root=Path({str(target)!r});'
        f'sys.path[:0]={[str(target),str(target/"python")]!r};'
        'from scripts.run_exp508_constrained_step import main;main();'
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
    root = ROOT/'artifacts/EXP-508'
    marker = root/'target-once.json'
    output = output.resolve()
    if root not in output.parents or output.exists() or marker.exists():
        raise ValueError('fresh output and unconsumed marker required')
    free = shutil.disk_usage(ROOT).free
    if free < p['limits']['initial_free_bytes']:
        raise ValueError('initial disk reserve')
    output.mkdir(parents=True)
    binding = dict(source_commit=source,remote_ref=remote,started_utc=base.utc(),plan_sha256=sha256(PLAN),
        inputs=INPUTS,sources={n:sha256(ROOT/n) for n in p['source_paths']},initial_free_bytes=free,
        runtime=dict(python=sys.version,numpy=base.np.__version__,scipy=base.scipy.__version__),paid_review=p['paid_review'])
    start,calls,checks = time.monotonic(),0,0
    progress = model.ledger()
    def write(name,value,reserve=True):
        return prior.write(output,output/name,value,p,reserve)
    def budget(integrating=False):
        nonlocal calls,checks
        checks += 1
        if integrating or checks % 1024 == 1:
            if (time.monotonic()-start > p['limits']['wall_seconds']
                    or shutil.disk_usage(ROOT).free < p['limits']['minimum_free_bytes']
                    or directory_bytes(output) > p['limits']['output_bytes']-p['limits']['failure_reserve_bytes']):
                raise base.previous.cycles_run.BudgetStop('EXP-508 time/storage cap')
        if integrating:
            if calls >= p['limits']['target_ivps']:
                raise base.previous.cycles_run.BudgetStop('EXP-508 IVP cap')
            calls += 1
    def timeout(*_):
        raise base.previous.cycles_run.BudgetStop('EXP-508 wall deadline')
    def completed(entry):
        name = entry['point']['spec']['id']+'-comparison.json'
        write(name,{k:v for k,v in entry.items() if k != 'point'})
        print(json.dumps(dict(completed_stage=entry['point']['spec']['id'],target_ivps=calls)),flush=True)
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p['limits']['wall_seconds'])
    try:
        write('binding.json',binding)
        write('startup.json',startup(p))
        write('control-replay.json',prior.prior.controls(original,p))
        budget(False)
        write_bounded_json(root,marker,binding,limit_bytes=directory_bytes(root)+1024**2,
            minimum_free_bytes=p['limits']['minimum_free_bytes'])
        with prior.producers(base,output,p['limits']):
            result = model.follow(base.load(),prior.prior.inputs(),prior.inputs(),inputs(),
                lambda numerical,spec:base.evaluate(numerical,spec,output/spec['id'],budget),progress,completed)
        budget(False)
        compact = dict(initialization=result['initialization'],analysis=result['analysis'],
            points=[dict(id=e['point']['spec']['id'],path=e['point']['spec']['id']+'/point.json',
                sha256=sha256(output/e['point']['spec']['id']/'point.json')) for e in result['entries']])
        write('summary.json',dict(experiment_id='EXP-508',status='completed',binding=binding,result=compact,
            progress=progress,ledger=base.load()['ledger'],target_ivps=calls,elapsed_seconds=time.monotonic()-start,
            completed_utc=base.utc(),files=inventory(output),marker_sha256=sha256(marker),symbolic_chains_verified=False))
        print(json.dumps(dict(completed=True,target_ivps=calls,output_bytes=directory_bytes(output),
            summary_sha256=sha256(output/'summary.json'))),flush=True)
    except BaseException as exc:
        signal.alarm(0)
        write('failure.json',dict(error_type=type(exc).__name__,message=str(exc)[:2000],utc=base.utc(),
            target_ivps=calls,progress=progress,files=inventory(output)),reserve=False)
        raise
    finally:
        signal.alarm(0)


def main():
    from scripts import audit_exp508_constrained_step  # noqa: F401
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    for name in ('prepare','startup','execute'):
        mode.add_argument('--'+name,action='store_true')
    parser.add_argument('--original-run',type=Path)
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--source-commit')
    parser.add_argument('--remote-ref')
    a = parser.parse_args()
    if a.prepare:
        p = expected()
        p['source_paths'] = sorted(set(EXPLICIT)|set(prior.load()['source_paths'])|base.imported())
        write_bounded_json(PLAN.parent,PLAN,p,limit_bytes=directory_bytes(PLAN.parent)+1024**2)
    elif a.execute:
        if not all((a.original_run,a.output_dir,a.source_commit,a.remote_ref)):
            parser.error('original controls, output, source and remote ref required')
        execute(a.output_dir,a.original_run,a.source_commit,a.remote_ref)
    else:
        print(json.dumps(startup(load()) if a.startup else validate()))


if __name__ == '__main__':
    main()
