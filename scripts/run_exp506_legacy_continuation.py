#!/usr/bin/env python3
"""Repair word-record completion and reuse the entire failed EXP-505 fit prefix."""
import argparse
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

import numpy as np
from butterfly._paired_startup import inventory,sha256,write_json
from scripts import run_exp505_legacy_impact as old

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT/'experiments/manifests/EXP-506-legacy-word-adapter-continuation.json'
ORIGINAL = ROOT/'artifacts/EXP-505/target-04771d8'
FAILURE_SHA = 'f025767950859ec7846dbaea96a4374fac4137a0989e429332bfcabf2cc7b29c'
SOURCE = '04771d80f973b60a39a187f382db8d773a32c089'
EXPLICIT = ['scripts/run_exp506_legacy_continuation.py','scripts/audit_exp506_legacy_continuation.py',
    'tests/test_exp506_legacy_continuation.py','docs/experiments/EXP-506-legacy-word-adapter-continuation.md',
    'experiments/manifests/EXP-506-legacy-word-adapter-continuation.json']


def original():
    if sha256(ORIGINAL/'failure.json') != FAILURE_SHA:
        raise ValueError('immutable original failure differs')
    failed = json.loads((ORIGINAL/'failure.json').read_bytes())
    binding = json.loads((ORIGINAL/'binding.json').read_bytes())
    p = old.load()
    if (failed['error_type'] != 'ValueError' or failed['message'] != 'original partition or word replay differs'
            or (ORIGINAL/'summary.json').exists() or inventory(ORIGINAL,omit=('failure.json',)) != failed['files']
            or binding['source_commit'] != SOURCE or binding['plan_sha256'] != sha256(old.PLAN)
            or binding['sources'] != {n:sha256(ROOT/n) for n in p['source_paths']}
            or binding['inputs'] != old.INPUTS
            or json.loads((ORIGINAL.parent/'target-once.json').read_bytes()) != binding
            or len(failed['partial']) != 1):
        raise ValueError('failed attempt source/raw/marker binding differs')
    prefix = failed['partial'][0]
    manifest,_ = old.inputs()
    identities = [(v['name'],i) for v in manifest['oracle_variants'] for i in range(51)]
    if (prefix['profile'] != 'rk4_dt_001' or prefix['coordinate'] != 'x' or prefix['mode'] != 'original'
            or [(f['variant'],f['ordinal']) for f in prefix['fits']] != identities
            or any(f['status'] != 'completed' or f['mode'] != 'original' for f in prefix['fits'])):
        raise ValueError('complete exact 255-fit prefix required')
    return failed,binding,prefix


def targets():
    manifest,receipt = old.inputs()
    spec = manifest['target']
    if sha256(ROOT/spec['path']) != spec['sha256']:
        raise ValueError('original source word transcription differs')
    source = json.loads((ROOT/spec['path']).read_bytes())
    words = [r['word'] for r in source['figure6']['nodes'] if int(r['period']) == spec['expected_period']]
    if words != receipt['target_words_of_same_period']:
        raise ValueError('complete historical target list differs')
    return words


def complete_word(row,words):
    row = deepcopy(row)
    comparisons = ({target:asdict(old.historical.compare_cyclic_words(tuple(row['raw_word']),tuple(target)))
        for target in words} if row['resolved'] else {})
    matches = [target for target,result in comparisons.items() if result['cyclic_match']]
    reversal = [target for target,result in comparisons.items() if result['reversal_cyclic_match'] and not result['cyclic_match']]
    return dict(row,target_comparisons=comparisons,cyclic_target_matches=matches,
        reversal_only_target_matches=reversal,target_membership_passed=len(matches)==1)


def replay_prefix(source,target,manifest,trace,budget=lambda:None):
    saved = original()[2]['fits']
    count = 0
    def fit(x,y,**options):
        nonlocal count
        if count >= len(saved):
            raise ValueError('prefix exhausted; fresh fitting is forbidden')
        row = saved[count]
        if (hashlib.sha256(np.column_stack((x,y)).astype('<f8').tobytes()).hexdigest() != row['sample_sha256']
                or any(trace[-1][k] != row[k] for k in ('variant','ordinal','mode','sample_sha256'))):
            raise ValueError('retained prefix sample/fit identity differs')
        trace[-1]['geometry'] = deepcopy(row['geometry'])
        count += 1
        value = row['fit_result']
        return value[0],tuple(value[1]),value[2],value[3]
    with patch.object(old.legacy,'_fit_branch_count',fit):
        result = old.oracle(source,target,manifest,'original',trace,budget)
    if count != 255 or trace != saved:
        raise ValueError('complete reused prefix differs')
    return result


def preflight():
    old.geometry.controls()
    manifest,receipt = old.inputs()
    original()
    words = targets()
    additions = {'target_comparisons','cyclic_target_matches','reversal_only_target_matches','target_membership_passed'}
    for row in receipt['words']:
        if complete_word({k:v for k,v in row.items() if k not in additions},words) != row:
            raise ValueError('complete historical word schema differs')
    with np.load(ROOT/'artifacts/EXP-186/states.npz',allow_pickle=False) as data:
        name = 'rk4_dt_001'
        source,target = old.geometry.pairs(data[name+'_midpoint_states'],data[name+'_midpoint_times'],data[name+'_midpoint_ids'],0)
    rebuilt = replay_prefix(source,target,manifest,[])
    if not old.equal(rebuilt,old.plain(receipt['profiles'][0]['coordinates']['x']['robust'])):
        raise ValueError('retained original robust result differs')
    return dict(passed=True,reused_branch_fits=255,new_branch_fits=0,new_word_spline_fits=0,target_integrations=0,
        complete_word_schema_rows=len(receipt['words']))


def expected():
    failed,binding,_ = original()
    manifest,_ = old.inputs()
    inputs = dict(old.INPUTS)
    for name in list(failed['files'])+['failure.json']:
        path = ORIGINAL/name
        inputs[path.relative_to(ROOT).as_posix()] = sha256(path)
    marker = ORIGINAL.parent/'target-once.json'
    inputs[marker.relative_to(ROOT).as_posix()] = sha256(marker)
    inputs[manifest['target']['path']] = manifest['target']['sha256']
    return dict(experiment_id='EXP-506',inputs=inputs,original_source=SOURCE,original_failure_sha256=FAILURE_SHA,
        reused_branch_fits=255,limits=old.load()['limits'],paid_review='not-requested-human-approval-policy',
        original_attempt_reset=False,target_integrations=0,symbolic_chains_verified=False)


def load():
    p = json.loads(PLAN.read_bytes())
    if {k:v for k,v in p.items() if k != 'source_paths'} != expected() or not set(EXPLICIT)|set(old.load()['source_paths']) <= set(p['source_paths']):
        raise ValueError('frozen adapter continuation differs')
    return p


def validate():
    p = load()
    result = preflight()
    if not old.shared.base.imported() <= set(p['source_paths']):
        raise ValueError('complete consumer import closure differs')
    return result


def startup(p):
    target = Path(tempfile.mkdtemp(prefix='exp506-startup-')).resolve()
    names = set(p['source_paths'])|set(p['inputs'])|set(old.shared.INPUTS)
    for n in names:
        destination = target/n
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/n,destination)
    code = (f'import sys;from pathlib import Path;root=Path({str(target)!r});sys.path[:0]={[str(target),str(target/"python")]!r};'
        'from scripts.run_exp506_legacy_continuation import main;main();'
        'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
        'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    child = subprocess.run([sys.executable,'-I','-B','-c',code],cwd=target,text=True,capture_output=True,check=True,timeout=60)
    if any(sha256(ROOT/n) != sha256(target/n) for n in names):
        raise ValueError('copied continuation source/input identity')
    return dict(passed=True,isolated=True,new_branch_fits=0,new_word_spline_fits=0,target_integrations=0,
        stdout=child.stdout,stderr=child.stderr,sources={n:sha256(target/n) for n in sorted(names)})


def analyze(reuse=True,emit=lambda *_:None,budget=lambda:None,partial=None):
    oracle,word,spline = old.oracle,old.historical._word_row,old.historical.UnivariateSpline
    words = targets()
    calls = 0
    slopes = []
    def routed(source,target,manifest,mode,trace,check=lambda:None):
        nonlocal calls
        calls += 1
        if calls == 1 and reuse:
            if mode != 'original':
                raise ValueError('original prefix must be first')
            # replay_prefix calls old.oracle; restore it only for that call.
            with patch.object(old,'oracle',oracle):
                return replay_prefix(source,target,manifest,trace,check)
        return oracle(source,target,manifest,mode,trace,check)
    def wrapped_word(*args,**kwargs):
        return complete_word(word(*args,**kwargs),words)
    def retained_spline(x,y,**kwargs):
        result = spline(x,y,**kwargs)
        slopes.append(dict(x=np.asarray(x).tolist(),y=np.asarray(y).tolist(),options=kwargs,
            knots=result.get_knots().tolist(),coefficients=result.get_coeffs().tolist(),residual=float(result.get_residual())))
        budget()
        return result
    with patch.object(old,'oracle',routed),patch.object(old.historical,'_word_row',wrapped_word),\
            patch.object(old.historical,'UnivariateSpline',retained_spline):
        result = old.analyze(emit,budget,partial)
    if calls != 8:
        raise ValueError('all eight mode populations required')
    return dict(result,word_spline_fits=slopes,word_spline_fit_count=len(slopes))


def execute(output,source,remote):
    p = load()
    def git(*args):
        return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    if git('rev-parse','HEAD') != source or git('status','--porcelain') or git('ls-remote','origin',remote).split() != [source,remote]:
        raise ValueError('clean live-pushed source required')
    validate()
    output = output.resolve()
    marker = ROOT/'artifacts/EXP-506/target-once.json'
    if ROOT/'artifacts/EXP-506' not in output.parents or output.exists() or marker.exists():
        raise ValueError('new continuation marker/output required')
    output.mkdir(parents=True)
    binding = dict(source_commit=source,remote_ref=remote,started_utc=old.shared.base.utc(),plan_sha256=sha256(PLAN),
        inputs=p['inputs'],sources={n:sha256(ROOT/n) for n in p['source_paths']},python=sys.version,
        numpy=np.__version__,scipy=old.shared.base.scipy.__version__)
    write_json(output/'binding.json',binding)
    start,partial = time.monotonic(),[]
    def budget():
        if (time.monotonic()-start > p['limits']['wall_seconds'] or shutil.disk_usage(ROOT).free < p['limits']['minimum_free_bytes']
                or sum(f.stat().st_size for f in output.rglob('*') if f.is_file()) > p['limits']['output_bytes']):
            raise RuntimeError('continuation resource cap')
    def emit(name,entry):
        write_json(output/(name+'.json'),entry)
        budget()
        print(json.dumps(dict(completed=name,branch_fit_records=len(entry['fits']))),flush=True)
    def timeout(*_):
        raise RuntimeError('continuation wall deadline')
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p['limits']['wall_seconds'])
    try:
        write_json(output/'startup.json',startup(p))
        write_json(output/'preflight.json',preflight())
        budget()
        write_json(marker,binding)
        result = analyze(True,emit,budget,partial)
        write_json(output/'summary.json',dict(experiment_id='EXP-506',status='completed',binding=binding,result=result,
            original_failure_sha256=FAILURE_SHA,reused_branch_fits=255,new_branch_fits=result['fit_calls']-255,
            target_integrations=0,paid_review=p['paid_review'],symbolic_chains_verified=False,original_attempt_reset=False,
            files=inventory(output),marker_sha256=sha256(marker),completed_utc=old.shared.base.utc(),elapsed_seconds=time.monotonic()-start))
        print(json.dumps(dict(completed=True,summary_sha256=sha256(output/'summary.json'))),flush=True)
    except BaseException as exc:
        signal.alarm(0)
        write_json(output/'failure.json',dict(error_type=type(exc).__name__,message=str(exc),partial=partial,files=inventory(output)))
        raise
    finally:
        signal.alarm(0)


def main():
    from scripts import audit_exp506_legacy_continuation  # noqa: F401
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--prepare',action='store_true')
    mode.add_argument('--startup',action='store_true')
    mode.add_argument('--execute',action='store_true')
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--source-commit')
    parser.add_argument('--remote-ref')
    a = parser.parse_args()
    if a.prepare:
        p = expected()
        p['source_paths'] = sorted(set(EXPLICIT)|set(old.load()['source_paths'])|old.shared.base.imported())
        write_json(PLAN,p)
    elif a.execute:
        if not all((a.output_dir,a.source_commit,a.remote_ref)):
            parser.error('fresh output and source/ref required')
        execute(a.output_dir,a.source_commit,a.remote_ref)
    else:
        print(json.dumps(startup(load()) if a.startup else validate()))


if __name__ == '__main__':
    main()
