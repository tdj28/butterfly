#!/usr/bin/env python3
"""Single-attempt fixed-c fold restoration, preserving every historical failure."""
import argparse
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

from butterfly._paired_startup import inventory, sha256
from butterfly.bounded_json import directory_bytes, write_bounded_json
from scripts import run_exp504_guarded_contact as prior
from scripts import verify_exp504_public_contact as public
from scripts import exp507_fold_restoration as model
from scripts.exp507_bounded_products import producers

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT/'experiments/manifests/EXP-507-fixed-c-fold-restoration.json'
RECEIPT = 'docs/experiments/receipts/EXP-504-contact-path-result.json'
INPUTS = {**prior.INPUTS, RECEIPT:'83b55c0063779f85370890ff34a04a419c475a3692dc5e3567ad4376a31ec128',
    'experiments/manifests/EXP-504-guarded-contact-continuation.json':
        'a5cc08a114d1c967d6b6b22f8e7307959c7f02d7a5dc7b69af1e846ebce9774c'}
EXPLICIT = ['scripts/run_exp507_fold_restoration.py','scripts/audit_exp507_fold_restoration.py',
    'scripts/exp507_fold_restoration.py','scripts/exp507_bounded_products.py',
    'tests/test_exp507_fold_restoration.py','tests/test_exp507_bounded_products.py',
    'docs/experiments/EXP-507-fixed-c-fold-restoration.md',
    'experiments/manifests/EXP-507-fixed-c-fold-restoration.json']


def inputs():
    if any(sha256(ROOT/n) != h for n,h in INPUTS.items()):
        raise ValueError('historical public inputs changed')
    saved = json.loads((ROOT/RECEIPT).read_bytes())
    if (len(saved['result']['steps']) != 1 or saved['result']['analysis']['accepted_steps'] != 0
            or saved['result']['steps'][0]['decision']['reason'] != 'fold proximity failed'):
        raise ValueError('preserved unique rejected predecessor required')
    return saved['result']['steps'][0]['point']


def expected():
    return dict(experiment_id='EXP-507',status='prospective-outcome-informed-corrective-pilot',
        inputs=INPUTS,proposal=model.propose(prior.base.load(),prior.inputs(),inputs()),
        points=1,attempts=1,primary_radius=1e-4,secondary_signed_fold_reduction=.5,
        controls=prior.load()['controls'],
        limits=dict(target_ivps=512,wall_seconds=3600,output_bytes=3*1024**3,
            initial_free_bytes=12*1024**3,minimum_free_bytes=8*1024**3,failure_reserve_bytes=1024**2),
        paid_review='not-requested-human-approval-policy',symbolic_chains_verified=False,
        warm_seed_rule='EXP-504 qualified but rejected point; original and adjacent cycle identities required')


def load():
    p = json.loads(PLAN.read_bytes())
    required = set(EXPLICIT)|set(prior.load()['source_paths'])
    if {k:v for k,v in p.items() if k != 'source_paths'} != expected() or not required <= set(p['source_paths']):
        raise ValueError('fixed restoration plan differs')
    return p


def validate():
    p = load()
    public.verify(ROOT/RECEIPT,INPUTS[RECEIPT])
    prior.model.warm_plan(prior.base.load(),inputs())
    if not prior.base.imported() <= set(p['source_paths']):
        raise ValueError('consumer source closure differs')
    return dict(valid=True,target_integrations=0,points=1,variants=256)


def startup(p):
    target = Path(tempfile.mkdtemp(prefix='exp507-startup-')).resolve()
    names = set(p['source_paths'])|set(INPUTS)
    for name in names:
        destination = target/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,destination)
    code = (f'import sys;from pathlib import Path;root=Path({str(target)!r});'
        f'sys.path[:0]={[str(target),str(target/"python")]!r};'
        'from scripts.run_exp507_fold_restoration import main;main();'
        'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
        'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    child = subprocess.run([sys.executable,'-I','-B','-c',code],cwd=target,capture_output=True,text=True,check=True,timeout=120)
    if any(sha256(ROOT/n) != sha256(target/n) for n in names):
        raise ValueError('copied source changed')
    return dict(passed=True,isolated=True,target_integrations=0,stdout=child.stdout,stderr=child.stderr,
        sources={n:sha256(target/n) for n in sorted(names)})


def write(root,path,value,p,reserve=True):
    return write_bounded_json(root,path,value,limit_bytes=p['limits']['output_bytes'],
        minimum_free_bytes=p['limits']['minimum_free_bytes'],
        reserve_bytes=p['limits']['failure_reserve_bytes'] if reserve else 0)


def execute(output,original,source,remote):
    p = load()
    def git(*args):
        return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    if (git('rev-parse','HEAD') != source or git('status','--porcelain')
            or git('ls-remote','origin',remote).split() != [source,remote]):
        raise ValueError('clean live-pushed exact source required')
    validate()
    root = ROOT/'artifacts/EXP-507'
    marker = root/'target-once.json'
    output = output.resolve()
    if root not in output.parents or output.exists() or marker.exists():
        raise ValueError('fresh output and unconsumed marker required')
    free = shutil.disk_usage(ROOT).free
    if free < p['limits']['initial_free_bytes']:
        raise ValueError('initial disk reserve')
    output.mkdir(parents=True)
    binding = dict(source_commit=source,remote_ref=remote,started_utc=prior.base.utc(),plan_sha256=sha256(PLAN),
        inputs=INPUTS,sources={n:sha256(ROOT/n) for n in p['source_paths']},initial_free_bytes=free,
        runtime=dict(python=sys.version,numpy=prior.base.np.__version__,scipy=prior.base.scipy.__version__),
        paid_review=p['paid_review'])
    start,calls,checks = time.monotonic(),0,0
    def budget(integrating=False):
        nonlocal calls,checks
        checks += 1
        if integrating or checks % 1024 == 1:
            if (time.monotonic()-start > p['limits']['wall_seconds']
                    or shutil.disk_usage(ROOT).free < p['limits']['minimum_free_bytes']
                    or directory_bytes(output) > p['limits']['output_bytes']-p['limits']['failure_reserve_bytes']):
                raise prior.base.previous.cycles_run.BudgetStop('EXP-507 time/storage cap')
        if integrating:
            if calls >= p['limits']['target_ivps']:
                raise prior.base.previous.cycles_run.BudgetStop('EXP-507 IVP cap')
            calls += 1
    def timeout(*_):
        raise prior.base.previous.cycles_run.BudgetStop('EXP-507 wall deadline')
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p['limits']['wall_seconds'])
    try:
        write(output,output/'binding.json',binding,p)
        write(output,output/'startup.json',startup(p),p)
        write(output,output/'control-replay.json',prior.controls(original,p),p)
        budget(False)
        # Marker is separate from the run quota and independently capped at 1 MiB.
        write_bounded_json(root,marker,binding,limit_bytes=directory_bytes(root)+1024**2,
            minimum_free_bytes=p['limits']['minimum_free_bytes'])
        numerical = prior.model.warm_plan(prior.base.load(),inputs())
        with producers(prior.base,output,p['limits']):
            point = prior.base.evaluate(numerical,p['proposal']['spec'],output/'fold-restoration',budget)
        decision = model.decide(prior.base.load(),inputs(),point,p['proposal'])
        write(output,output/'decision.json',decision,p)
        budget(False)
        # No duplicate point/journal in this final summary.
        write(output,output/'summary.json',dict(experiment_id='EXP-507',status='completed',binding=binding,
            point_path='fold-restoration/point.json',point_sha256=sha256(output/'fold-restoration/point.json'),
            decision=decision,ledger=prior.base.load()['ledger'],target_ivps=calls,
            elapsed_seconds=time.monotonic()-start,completed_utc=prior.base.utc(),files=inventory(output),
            marker_sha256=sha256(marker),symbolic_chains_verified=False),p)
        print(json.dumps(dict(completed=True,target_ivps=calls,output_bytes=directory_bytes(output),
            summary_sha256=sha256(output/'summary.json'))),flush=True)
    except BaseException as exc:
        signal.alarm(0)
        write(output,output/'failure.json',dict(error_type=type(exc).__name__,message=str(exc)[:2000],
            utc=prior.base.utc(),target_ivps=calls,files=inventory(output)),p,reserve=False)
        raise
    finally:
        signal.alarm(0)


def main():
    from scripts import audit_exp507_fold_restoration  # noqa: F401
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
        p['source_paths'] = sorted(set(EXPLICIT)|set(prior.load()['source_paths'])|prior.base.imported())
        write_bounded_json(PLAN.parent,PLAN,p,limit_bytes=directory_bytes(PLAN.parent)+1024**2)
    elif a.execute:
        if not all((a.original_run,a.output_dir,a.source_commit,a.remote_ref)):
            parser.error('original controls, output, source and remote ref required')
        execute(a.output_dir,a.original_run,a.source_commit,a.remote_ref)
    else:
        print(json.dumps(startup(load()) if a.startup else validate()))


if __name__ == '__main__':
    main()
