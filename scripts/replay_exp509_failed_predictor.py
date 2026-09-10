#!/usr/bin/env python3
"""Outcome-informed forensic replay of EXP-508; no new flow integrations."""
import argparse
import json
import math
from pathlib import Path
import signal
import subprocess
import time
from types import FunctionType

from butterfly._paired_startup import inventory, sha256
from butterfly.bounded_json import directory_bytes, write_bounded_json
from scripts import run_exp508_constrained_step as old
from scripts import audit_exp502_joint_contact as raw_audit

ROOT = old.ROOT
PLAN = ROOT/'experiments/manifests/EXP-509-failed-predictor-replay.json'
FAILED = ROOT/'artifacts/EXP-508/target-709af03'
MARKER = ROOT/'artifacts/EXP-508/target-once.json'
FAILURE_SHA = 'c7051cdb6767ef9a277972db99f01dd103f851772698dee368c0ce9737051d1f'
POINT_SHA = 'efafea877ea6427758fdf8af70e2b0136626b004f0f3abb22a22fde362bf071a'
MARKER_SHA = '993ee23661cc59b0e8ca5f526864c5553ec4219bb517de4fc7e37c1bf78c4ded'
SOURCE = '709af03fe9a8f6c6d9b5480a886cb7d0a2c3ce5a'
EXPLICIT = ['scripts/replay_exp509_failed_predictor.py',
    'tests/test_exp509_failed_predictor.py',
    'docs/experiments/EXP-509-failed-predictor-replay.md',
    'experiments/manifests/EXP-509-failed-predictor-replay.json']


def qualification(numerical, start, point):
    """Missing, malformed or nonfinite envelopes cannot license continuation."""
    original = old.model.old.response.correspondence(point['cycle'], numerical['reference_cycle'])
    anchor = old.model.old.response.correspondence(point['cycle'], start['cycle'])
    contact = point.get('contact')
    envelope = contact.get('envelope') if isinstance(contact, dict) else None
    distances = envelope.get('pair_state_distance') if isinstance(envelope, dict) else None
    complete = (isinstance(distances, list) and len(distances) == 6
        and all(isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v) and v >= 0 for v in distances))
    distance = distances[3] if complete else None
    qualified = bool(complete and point['qualified'] and point['correspondence']['passed']
        and original['passed'] and anchor['passed'])
    return dict(qualified=qualified, original_correspondence=original, start_correspondence=anchor,
        fold_proximity=bool(qualified and distance <= 1e-4), worst_fold_distance=distance)


def follow(*args, **kwargs):
    # Copy only the controller globals. Never patch the frozen module in place.
    fn = old.model.follow
    revised = FunctionType(fn.__code__, dict(fn.__globals__, qualification=qualification),
        fn.__name__, fn.__defaults__, fn.__closure__)
    return revised(*args, **kwargs)


def expected():
    return dict(experiment_id='EXP-509', kind='outcome-informed-forensic-replay',
        original_source_commit=SOURCE, failure_sha256=FAILURE_SHA, point_sha256=POINT_SHA,
        marker_sha256=MARKER_SHA, original_plan_sha256=sha256(old.PLAN),
        original_inputs=old.INPUTS, attempts=1, new_integrations=0, original_ivps=196,
        limits=dict(wall_seconds=3600, output_bytes=16*1024**2, failure_reserve_bytes=1024**2),
        exposure='EXP-508 crash, unqualified point, qualified cycle, complete boundary analysis and two unqualified depth-8 folds were visible before this freeze. Fold failure causes and numerical comparisons have not been reinterpreted.',
        paid_review='not-requested-human-approval-policy', symbolic_chains_verified=False,
        source_paths=sorted(set(old.load()['source_paths']) | set(EXPLICIT)))


def load():
    p = json.loads(PLAN.read_bytes())
    if p != expected():
        raise ValueError('forensic replay plan differs')
    return p


def validate():
    p = load()
    old.public.verify(ROOT/old.RECEIPT,old.INPUTS[old.RECEIPT])
    if not old.load()['predictor']['qualified'] or not old.base.imported() <= set(p['source_paths']):
        raise ValueError('initial predictor or successor source closure differs')
    old.prior.prior.model.warm_plan(old.base.load(),old.inputs())
    return dict(valid=True,new_integrations=0)


def authenticate():
    """Authenticate all retained bytes before interpreting the scientific row."""
    if (sha256(FAILED/'failure.json') != FAILURE_SHA
            or sha256(FAILED/'predictor/point.json') != POINT_SHA or sha256(MARKER) != MARKER_SHA):
        raise ValueError('original failure, point or marker identity differs')
    failure = json.loads((FAILED/'failure.json').read_bytes())
    binding = json.loads((FAILED/'binding.json').read_bytes())
    if (failure['files'] != inventory(FAILED, omit=('failure.json',))
            or binding != json.loads(MARKER.read_bytes()) or binding['source_commit'] != SOURCE
            or binding['plan_sha256'] != sha256(old.PLAN) or binding['inputs'] != old.INPUTS
            or binding['sources'] != {n:sha256(ROOT/n) for n in old.load()['source_paths']}
            or failure['target_ivps'] != 196 or failure['error_type'] != 'TypeError'
            or failure['message'] != "'NoneType' object is not subscriptable"
            or failure['progress'] != [
                dict(id='predictor',status='started',reason=None),
                dict(id='corrector',status='not-run',reason=None)]
            or not binding['started_utc'] <= failure['utc']
            or (FAILED/'summary.json').exists() or (FAILED/'corrector').exists()
            or (FAILED/'predictor-comparison.json').exists()):
        raise ValueError('original failure/source/inventory binding differs')
    startup = json.loads((FAILED/'startup.json').read_bytes())
    if (startup['passed'] is not True or startup['isolated'] is not True
            or startup['target_integrations'] != 0
            or startup['sources'] != {n:sha256(ROOT/n) for n in set(old.load()['source_paths'])|set(old.INPUTS)}
            or json.loads(startup['stdout']) != dict(valid=True,target_integrations=0,maximum_points=2,variants=256)):
        raise ValueError('original isolated startup differs')
    return failure, binding


def replay():
    failure, binding = authenticate()
    validate()
    control = old.prior.prior.controls(ROOT/'artifacts/EXP-502/target-69efcd3',old.load())
    if control != json.loads((FAILED/'control-replay.json').read_bytes()):
        raise ValueError('original analytic control replay differs')
    row = json.loads((FAILED/'predictor/point.json').read_bytes())
    seen, counts = [], []
    def measure(numerical, spec):
        if seen or spec != row['spec'] or spec['id'] != 'predictor':
            raise ValueError('no new point or corrector is authorized')
        paths, calls, products = raw_audit.check_point(FAILED/'predictor',row,numerical,binding,failure['utc'])
        if ({'predictor/'+n for n in paths}|{'binding.json','startup.json','control-replay.json'}
                != set(failure['files']) or calls != failure['target_ivps']):
            raise ValueError('full failed-run inventory or actual IVP count differs')
        seen.append(spec['id'])
        counts.append(dict(target_ivps=calls,inherited_archive_products=products))
        return row
    progress = old.model.ledger()
    result = follow(old.base.load(),old.prior.prior.inputs(),old.prior.inputs(),old.inputs(),measure,progress)
    # Separately stated forensic stopping rule, not an invented original summary.
    if (seen != ['predictor'] or row['qualified'] is not False
            or result['analysis']['accepted'] or result['analysis']['status'] != 'predictor-unqualified'
            or progress[1] != dict(id='corrector',status='not-run',reason='predictor-unqualified')):
        raise ValueError('unqualified predictor did not safely stop')
    final_failure, final_binding = authenticate()
    if final_failure != failure or final_binding != binding:
        raise ValueError('retained original bytes changed during replay')
    return dict(experiment_id='EXP-509', raw_replay_passed=True, original_run_completed=False,
        original_failure=failure, original_binding=binding, original_point_sha256=POINT_SHA,
        original_marker_sha256=MARKER_SHA, original_output_bytes=directory_bytes(FAILED),
        original_target_ivps=counts[0]['target_ivps'], counts=counts,
        reconstructed_result=result, reconstructed_progress=progress, original_ledger=old.base.load()['ledger'],
        new_integrations=0, symbolic_chains_verified=False,
        scope='Local shared-code full raw replay of the sole saved predictor, not independent-team replication or a completed EXP-508 run. No corrector and no new target; unchanged numerical thresholds.')


def execute(output, source, remote):
    p = load()
    def git(*args):
        return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    if (git('rev-parse','HEAD') != source or git('status','--porcelain')
            or git('ls-remote','origin',remote).split() != [source,remote]):
        raise ValueError('clean live-pushed exact replay source required')
    root = ROOT/'artifacts/EXP-509'
    marker = root/'replay-once.json'
    output = output.resolve()
    if root not in output.parents or output.exists() or marker.exists():
        raise ValueError('fresh replay namespace and marker required')
    output.mkdir(parents=True)
    binding = dict(source_commit=source,remote_ref=remote,started_utc=old.base.utc(),
        plan_sha256=sha256(PLAN),sources={n:sha256(ROOT/n) for n in p['source_paths']},
        paid_review=p['paid_review'],new_integrations=0)
    def write(name, value, reserve=True):
        return write_bounded_json(output,output/name,value,limit_bytes=p['limits']['output_bytes'],
            reserve_bytes=p['limits']['failure_reserve_bytes'] if reserve else 0)
    def timeout(*_):
        raise TimeoutError('EXP-509 replay deadline')
    start = time.monotonic()
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p['limits']['wall_seconds'])
    try:
        write('binding.json',binding)
        write_bounded_json(root,marker,binding,limit_bytes=directory_bytes(root)+1024**2)
        result = replay()
        write('result.json',dict(result,binding=binding,elapsed_seconds=time.monotonic()-start,
            completed_utc=old.base.utc(),replay_marker_sha256=sha256(marker)))
        print(json.dumps(dict(raw_replay_passed=True,original_target_ivps=result['original_target_ivps'],
            new_integrations=0,result_sha256=sha256(output/'result.json'))),flush=True)
    except BaseException as exc:
        signal.alarm(0)
        write('failure.json',dict(error_type=type(exc).__name__,message=str(exc),utc=old.base.utc(),
            files=inventory(output)),reserve=False)
        raise
    finally:
        signal.alarm(0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--prepare',action='store_true')
    modes.add_argument('--execute',action='store_true')
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--source-commit')
    parser.add_argument('--remote-ref')
    a = parser.parse_args()
    if a.prepare:
        write_bounded_json(PLAN.parent,PLAN,expected(),limit_bytes=directory_bytes(PLAN.parent)+1024**2)
    elif a.execute:
        if not all((a.output_dir,a.source_commit,a.remote_ref)):
            parser.error('output, exact source and remote ref required')
        execute(a.output_dir,a.source_commit,a.remote_ref)
    else:
        print(json.dumps(validate()))


if __name__ == '__main__':
    main()
