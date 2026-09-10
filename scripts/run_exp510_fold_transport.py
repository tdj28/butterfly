#!/usr/bin/env python3
"""Bounded local fold-only transport; no boundary or cycle integrations."""
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
from butterfly.models import RosslerParameters
from butterfly.poincare import legacy_rossler_section
from scripts import replay_exp509_failed_predictor as prior
from scripts import verify_exp509_public_replay as public
from scripts import exp510_fold_transport as model

ROOT = prior.ROOT
PLAN = ROOT/'experiments/manifests/EXP-510-four-substep-fold-transport.json'
RECEIPT = 'docs/experiments/receipts/EXP-509-failed-predictor-replay-result.json'
INPUTS = dict(prior.old.INPUTS,**{RECEIPT:'6857228fe1c4b09692982e5d6481595398552c2e055b6f1620b22c499bcff4e5'})
EXPLICIT = ['scripts/run_exp510_fold_transport.py','scripts/audit_exp510_fold_transport.py',
    'scripts/exp510_fold_transport.py','scripts/verify_exp509_public_replay.py',
    'tests/test_exp509_public_replay.py','tests/test_exp510_fold_transport.py',
    'docs/experiments/EXP-510-four-substep-fold-transport.md',
    'experiments/manifests/EXP-510-four-substep-fold-transport.json']
base = prior.old.base


def inputs():
    if any(sha256(ROOT/n) != h for n,h in INPUTS.items()):
        raise ValueError('fixed historical input identity differs')
    return json.loads((ROOT/RECEIPT).read_bytes())['reconstructed_result']['entries'][0]['point']


def expected():
    return dict(experiment_id='EXP-510',status='prospective-outcome-informed-fold-transport',
        inputs=INPUTS,specifications=model.specifications(prior.old.inputs()['spec']['parameters'],inputs()['spec']['parameters']),
        substeps=4,folds_per_step=4,solvers=['DOP853','Radau'],attempts=1,
        new_cycles=0,new_boundaries=0,cross_history_radius=1e-6,maximum_adjacent_displacement=.01,
        seed_rule='mean of both qualified predecessor solver roots; unchanged u +/- .02, time +/- 1; no failed-root reuse',
        controls=prior.old.load()['controls'],
        limits=dict(target_ivps=512,wall_seconds=1800,output_bytes=2*1024**3,
            initial_free_bytes=12*1024**3,minimum_free_bytes=8*1024**3,failure_reserve_bytes=1024**2),
        paid_review='not-requested-human-approval-policy',symbolic_chains_verified=False,
        source_paths=sorted(set(prior.load()['source_paths'])|set(EXPLICIT)))


def load():
    p = json.loads(PLAN.read_bytes())
    if p != expected():
        raise ValueError('four-substep fold plan differs')
    return p


def offset(parameters):
    return legacy_rossler_section(RosslerParameters(**parameters)).offset


def validate():
    p = load()
    public.verify(ROOT/RECEIPT,INPUTS[RECEIPT])
    if not base.imported() <= set(p['source_paths']):
        raise ValueError('successor source closure incomplete')
    first = p['specifications'][0]
    model.candidates(base.load(),prior.old.inputs()['folds'],first,offset(first['parameters']))
    return dict(valid=True,new_integrations=0,maximum_substeps=4,folds_per_step=4)


def startup(p):
    target = Path(tempfile.mkdtemp(prefix='exp510-startup-')).resolve()
    names = set(p['source_paths'])|set(INPUTS)
    for name in names:
        destination = target/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,destination)
    code = (f'import sys;from pathlib import Path;root=Path({str(target)!r});'
        f'sys.path[:0]={[str(target),str(target/"python")]!r};'
        'from scripts.run_exp510_fold_transport import main;main();'
        'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
        'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    child = subprocess.run([sys.executable,'-I','-B','-c',code],cwd=target,capture_output=True,text=True,check=True,timeout=120)
    if any(sha256(ROOT/n) != sha256(target/n) for n in names):
        raise ValueError('copied source changed')
    return dict(passed=True,isolated=True,new_integrations=0,stdout=child.stdout,stderr=child.stderr,
        sources={n:sha256(target/n) for n in sorted(names)})


def endpoint(result):
    if not result['transport_completed']:
        return None
    contact = base.previous.measure(result['rows'][-1]['folds'],inputs()['cycle'],base.load())
    return dict(contact=contact,fold_proximity=contact['envelope']['pair_state_distance'][3] <= 1e-4,
        reused_point_sha256=prior.POINT_SHA,boundary_distance=inputs()['boundary_analysis']['cycle_indices'][1]['maximum_distance'],
        scope='New endpoint folds compared with the unchanged audited EXP-508/509 cycle. No intermediate cycle inference and no new complete joint point.')


def execute(output,source,remote):
    p = load()
    def git(*args):
        return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    if (git('rev-parse','HEAD') != source or git('status','--porcelain')
            or git('ls-remote','origin',remote).split() != [source,remote]):
        raise ValueError('clean live-pushed exact source required')
    validate()
    root = ROOT/'artifacts/EXP-510'
    marker = root/'target-once.json'
    output = output.resolve()
    if root not in output.parents or output.exists() or marker.exists():
        raise ValueError('fresh output and unconsumed target marker required')
    free = shutil.disk_usage(ROOT).free
    if free < p['limits']['initial_free_bytes']:
        raise ValueError('initial disk reserve')
    output.mkdir(parents=True)
    binding = dict(source_commit=source,remote_ref=remote,started_utc=base.utc(),plan_sha256=sha256(PLAN),
        inputs=INPUTS,sources={n:sha256(ROOT/n) for n in p['source_paths']},initial_free_bytes=free,
        runtime=dict(python=sys.version,numpy=base.np.__version__,scipy=base.scipy.__version__),paid_review=p['paid_review'])
    start,calls = time.monotonic(),0
    stage_progress = []
    def write(name,value,reserve=True):
        return prior.old.prior.write(output,output/name,value,p,reserve)
    def budget(integrating=False):
        nonlocal calls
        if (time.monotonic()-start > p['limits']['wall_seconds']
                or shutil.disk_usage(ROOT).free < p['limits']['minimum_free_bytes']):
            raise RuntimeError('EXP-510 time/free-space cap')
        if integrating:
            if calls >= p['limits']['target_ivps']:
                raise RuntimeError('EXP-510 IVP cap')
            calls += 1
    def measure(spec,candidates):
        folder = output/spec['id']
        folder.mkdir()
        stage_progress.append(dict(id=spec['id'],status='started'))
        write(spec['id']+'/inputs.json',dict(spec=spec,candidates=candidates))
        rows = []
        for c in candidates:
            profiles = [base.fold_profile(folder,c,method,base.load()['fold'],budget) for method in p['solvers']]
            row = dict(base.compare(c,profiles,base.load()['fold']),parent_id=c['parent_id'])
            write(spec['id']+'/'+c['id']+'.json',row)
            rows.append(row)
        write(spec['id']+'/folds.json',rows)
        stage_progress[-1]['status'] = 'completed'
        print(json.dumps(dict(completed_substep=spec['id'],target_ivps=calls,
            qualified_folds=sum(r['qualified_in_region'] for r in rows))),flush=True)
        return rows
    def timeout(*_):
        raise TimeoutError('EXP-510 wall deadline')
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p['limits']['wall_seconds'])
    try:
        write('binding.json',binding)
        write('startup.json',startup(p))
        write('control-replay.json',prior.old.prior.prior.controls(ROOT/'artifacts/EXP-502/target-69efcd3',p))
        write_bounded_json(root,marker,binding,limit_bytes=directory_bytes(root)+1024**2,
            minimum_free_bytes=p['limits']['minimum_free_bytes'])
        with prior.old.prior.producers(base,output,p['limits']):
            result = model.follow(base.load(),prior.old.inputs(),inputs()['spec']['parameters'],offset,measure)
        budget(False)
        write('summary.json',dict(experiment_id='EXP-510',status='completed',binding=binding,result=result,
            endpoint_comparison=endpoint(result),stage_progress=stage_progress,target_ivps=calls,
            elapsed_seconds=time.monotonic()-start,completed_utc=base.utc(),files=inventory(output),
            marker_sha256=sha256(marker),ledger=base.load()['ledger'],symbolic_chains_verified=False))
        print(json.dumps(dict(completed=True,target_ivps=calls,transport_completed=result['transport_completed'],
            summary_sha256=sha256(output/'summary.json'))),flush=True)
    except BaseException as exc:
        signal.alarm(0)
        write('failure.json',dict(error_type=type(exc).__name__,message=str(exc),utc=base.utc(),
            target_ivps=calls,stage_progress=stage_progress,files=inventory(output)),reserve=False)
        raise
    finally:
        signal.alarm(0)


def main():
    from scripts import audit_exp510_fold_transport  # noqa: F401
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
            parser.error('output, source and remote ref required')
        execute(a.output_dir,a.source_commit,a.remote_ref)
    else:
        print(json.dumps(startup(load()) if a.startup else validate()))


if __name__ == '__main__':
    main()
