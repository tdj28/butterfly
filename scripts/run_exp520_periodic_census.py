#!/usr/bin/env python3
"""Prospective saved-cycle stationarity census, with zero new integrations."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

import numpy as np
from numpy.lib.format import read_magic, read_array_header_1_0, read_array_header_2_0
from butterfly._paired_startup import inventory, safe_file, sha256, write_json
from butterfly.bounded_json import write_bounded_json
from butterfly.models import RosslerParameters, rossler_equilibria
from scripts import exp520_periodic_census as model

ROOT = Path(__file__).resolve().parents[1]
PARENT = 'docs/experiments/receipts/EXP-519-fixed-c-fold-response-result.json'
PARENT_SHA = '92ff9159ca3de7794a481e9d682d02626b945495f3ad87e6c7d095137f0117ec'
RAW = ROOT/'artifacts/EXP-519/target-cdd08b3'
RAW_SHA = '6aded74665ff16d63ff3f4e2b53cea49f5aec445db7c644e98f88f6bce54aa89'
PARENT_SOURCE = 'cdd08b37762e2c89bc368535331450c94cd33f53'
PLAN = ROOT/'experiments/manifests/EXP-520-periodic-stationarity-census.json'
META = ROOT/'experiments/manifests/EXP-520-observation-inputs.json'
MARKER = ROOT/'artifacts/EXP-520/target-once.json'
IDS = ['coarse--1', 'coarse-+1', 'fine--1', 'fine-+1', 'correction']
METHODS = ['DOP853', 'Radau']
EXPLICIT = ['scripts/exp520_periodic_census.py', 'scripts/run_exp520_periodic_census.py',
    'scripts/audit_exp520_periodic_census.py', 'tests/test_exp520_periodic_census.py',
    'tests/test_exp520_runner.py', 'docs/experiments/EXP-520-periodic-stationarity-census.md',
    'experiments/manifests/EXP-520-periodic-stationarity-census.json',
    'experiments/manifests/EXP-520-observation-inputs.json', 'pyproject.toml', 'uv.lock']


def utc():
    return datetime.now(timezone.utc).isoformat()


def parent_points():
    if sha256(ROOT/PARENT) != PARENT_SHA:
        raise ValueError('immutable EXP-519 audit receipt differs')
    saved = json.loads((ROOT/PARENT).read_bytes())
    points = saved['result']['points']+[saved['result']['correction']]
    if (saved['summary_sha256'] != RAW_SHA or saved['source_commit'] != PARENT_SOURCE
            or not saved['passed'] or not saved['result']['decision']['qualified_contact']
            or [p['spec']['id'] for p in points] != IDS):
        raise ValueError('complete qualified parent identity differs')
    return points


def headers(path):
    result = {}
    with zipfile.ZipFile(path) as z:
        for name in ('times.npy', 'dense_old.npy', 'dense_coefficients.npy'):
            with z.open(name) as stream:
                version = read_magic(stream)
                if version not in ((1, 0), (2, 0)):
                    raise ValueError('unsupported numeric array header')
                reader = read_array_header_1_0 if version == (1, 0) else read_array_header_2_0
                shape, order, dtype = reader(stream)
                result[name] = dict(shape=list(shape), fortran=order, dtype=str(dtype))
    return result


def input_metadata():
    """Read only saved parent outcomes, file hashes and array headers, not new gaps."""
    if sha256(RAW/'summary.json') != RAW_SHA:
        raise ValueError('original raw summary differs')
    saved = json.loads((RAW/'summary.json').read_bytes())
    rows = []
    for point in parent_points():
        name = point['spec']['id']
        for method in METHODS:
            relative = f'{name}/{name}--{method}--observation.npz'
            path = safe_file(RAW, relative)
            meta = headers(path)
            entry = dict(bytes=path.stat().st_size, sha256=sha256(path))
            if saved['files'][relative] != entry:
                raise ValueError('original observation inventory differs')
            rows.append(dict(point=name, method=method, raw_path=relative, arrays=meta, **entry))
    return dict(experiment_id='EXP-520', purpose='shape-and-hash-only preflight',
                raw_summary_sha256=RAW_SHA, observations=rows)


def expected():
    metadata = json.loads(META.read_bytes())
    if metadata['experiment_id'] != 'EXP-520' or metadata['raw_summary_sha256'] != RAW_SHA:
        raise ValueError('input inventory identity differs')
    observations = metadata['observations']
    if [(r['point'], r['method']) for r in observations] != [(i, m) for i in IDS for m in METHODS]:
        raise ValueError('complete input observation matrix required')
    total = 0
    for row in observations:
        count = row['arrays']['times.npy']['shape'][0]-1
        shape = [count, 7, 3] if row['method'] == 'DOP853' else [count, 3, 3]
        if (row['arrays'] != {'times.npy': dict(shape=[count+1], fortran=False, dtype='float64'),
                'dense_old.npy': dict(shape=[count, 3], fortran=False, dtype='float64'),
                'dense_coefficients.npy': dict(shape=shape, fortran=False, dtype='float64')}
                or not re.fullmatch('[0-9a-f]{64}', row['sha256']) or not 0 < row['bytes'] < 16*1024**2):
            raise ValueError('bounded complete binary64 observation metadata required')
        total += count
    if total != 417460:
        raise ValueError('exact preflight segment inventory differs')
    trials = []
    for point in parent_points():
        profiles = point['cycle']['profiles']
        if [p['method'] for p in profiles] != METHODS or not all(p['qualified'] for p in profiles):
            raise ValueError('complete qualified parent solver pair required')
        trials.append(dict(id=point['spec']['id'], parameters=point['spec']['parameters'],
            profiles=[dict(method=p['method'], period=p['correction']['period_time']) for p in profiles]))
    # This package's __init__ imports numerical helpers. Ship their exact source
    # closure, not the many unrelated historical experiment runners.
    package = sorted(str(p.relative_to(ROOT)) for p in (ROOT/'python/butterfly').glob('*.py'))
    return dict(experiment_id='EXP-520', status='prospective-saved-data-followup-after-EXP-519',
        trials=trials, observations=observations, total_segments=total,
        inputs={PARENT: PARENT_SHA, str(META.relative_to(ROOT)): sha256(META)},
        source_paths=sorted(set(package+EXPLICIT)), parent_raw_sha256=RAW_SHA,
        limits=dict(wall_seconds=7200, output_bytes=256*1024**2,
                    initial_free_bytes=9*1024**3, minimum_free_bytes=8*1024**3,
                    maximum_segments=500000, failure_reserve_bytes=65536),
        isolation=dict(time_width=str(model.TIME_WIDTH), max_depth=160, max_nodes=2048, max_refinements=256),
        comparisons=dict(scaled_state=model.STATE_TOL, phase=model.PHASE_TOL,
            join_scaled=float(model.JOIN_TOL), unique_nearest_gap_separation=model.GAP_SEPARATION),
        windows=[.25, 1.25], new_integrations=0, paid_review='not_requested-human-approval-policy',
        exact_flow_completeness=False, symbolic_chains_verified=False, D_identified=False)


def load():
    plan = json.loads(PLAN.read_bytes())
    if plan != expected():
        raise ValueError('frozen plan differs from complete design')
    for name, digest in plan['inputs'].items():
        if sha256(safe_file(ROOT, name)) != digest:
            raise ValueError('input bytes differ')
    return plan


def controls():
    cases = [([1, 0, 1], 0, True), ([-1, 2], 1, True), ([3, -16, 16], 2, True),
             ([0, -1, 1], 2, True), ([1, -4, 4], 1, True), ([0, 0, 0], 0, False)]
    for power, count, complete in cases:
        proof = model.roots.isolate(power, 1, time_width=model.TIME_WIDTH)
        audit = model.roots.verify(power, 1, proof, time_width=model.TIME_WIDTH)
        if len(audit['roots']) != count or audit['complete'] != complete:
            raise ValueError('analytic root control failed')
    return dict(passed=True, cases=len(cases), target_data_opened=False, new_integrations=0)


def startup(plan):
    with tempfile.TemporaryDirectory(prefix='exp520-startup-') as folder:
        root = Path(folder).resolve()
        names = set(plan['source_paths']) | set(plan['inputs'])
        for name in names:
            destination = root/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(safe_file(ROOT, name), destination)
        code = ('import sys;from pathlib import Path;'
            f'root=Path({str(root)!r});sys.path[:0]=[str(root),str(root/"python")];'
            'from scripts import run_exp520_periodic_census as r;'
            'from scripts import audit_exp520_periodic_census;'
            'assert r.load()["experiment_id"]=="EXP-520";assert r.controls()["passed"];'
            'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
            'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
        subprocess.run([sys.executable, '-I', '-B', '-c', code], cwd=root,
                       capture_output=True, text=True, check=True, timeout=120)
        if list(root.rglob('*.pyc')) or inventory(root) != {n: dict(bytes=(ROOT/n).stat().st_size, sha256=sha256(ROOT/n)) for n in sorted(names)}:
            raise ValueError('sealed startup source topology changed')
    return dict(passed=True, target_data_opened=False, source_files=len(names), controls=controls())


def authenticate_raw(plan):
    if sha256(RAW/'summary.json') != RAW_SHA:
        raise ValueError('raw summary differs')
    summary = json.loads((RAW/'summary.json').read_bytes())
    if summary['status'] != 'completed' or summary['binding']['source_commit'] != PARENT_SOURCE:
        raise ValueError('completed original raw source binding required')
    for row in plan['observations']:
        path = safe_file(RAW, row['raw_path'])
        entry = dict(bytes=path.stat().st_size, sha256=sha256(path))
        if entry != summary['files'][row['raw_path']] or entry != {k: row[k] for k in entry} or headers(path) != row['arrays']:
            raise ValueError('complete original observation hash/shape binding differs')
    return summary


def execute(output, source, remote):
    plan = load(); sources = {n: sha256(ROOT/n) for n in plan['source_paths']}
    if not re.fullmatch('[0-9a-f]{40}', source):
        raise ValueError('full frozen source commit required')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    observed = subprocess.check_output(['git', 'ls-remote', 'origin', remote], cwd=ROOT, text=True).split()
    if head != source or observed != [source, remote]:
        raise ValueError('live pushed source barrier differs')
    for name, digest in sources.items():
        committed = subprocess.check_output(['git', 'show', f'{source}:{name}'], cwd=ROOT)
        import hashlib
        if hashlib.sha256(committed).hexdigest() != digest:
            raise ValueError('committed source differs from working bytes')
    if MARKER.exists() or output.exists() or output.is_symlink():
        raise ValueError('fresh one-shot census namespace required')
    if shutil.disk_usage(ROOT).free < plan['limits']['initial_free_bytes']:
        raise ValueError('initial census disk reserve unavailable')
    handshake = startup(plan)
    authenticate_raw(plan)  # Hash/shape only: no new polynomial roots or gaps.
    if sources != {n: sha256(ROOT/n) for n in sources}:
        raise ValueError('source changed before outcome access')
    output.mkdir(parents=True, exist_ok=False)
    MARKER.parent.mkdir(parents=True, exist_ok=True)
    binding = dict(experiment_id='EXP-520', source_commit=source, remote_ref=remote,
        plan_sha256=sha256(PLAN), sources=sources, inputs=plan['inputs'], started_utc=utc(),
        parent_raw_summary_sha256=RAW_SHA, startup=handshake)
    write_json(MARKER, binding)
    started, segments = time.monotonic(), 0
    def save(name, value, failure=False):
        return write_bounded_json(output, output/name, value, limit_bytes=plan['limits']['output_bytes'],
            minimum_free_bytes=plan['limits']['minimum_free_bytes'],
            reserve_bytes=0 if failure else plan['limits']['failure_reserve_bytes'])
    def tick():
        nonlocal segments
        segments += 1
        if segments > plan['limits']['maximum_segments'] or time.monotonic()-started > plan['limits']['wall_seconds']:
            raise ValueError('bounded census resource limit reached')
        if segments % 1000 == 0 and shutil.disk_usage(output).free < plan['limits']['minimum_free_bytes']:
            raise ValueError('census disk floor reached')
    save('binding.json', binding)
    try:
        points = []
        for trial in plan['trials']:
            profiles = []
            origin = rossler_equilibria(RosslerParameters(**trial['parameters']))[0].tolist()
            for config in trial['profiles']:
                row = next(r for r in plan['observations'] if (r['point'], r['method']) == (trial['id'], config['method']))
                with np.load(RAW/row['raw_path'], allow_pickle=False) as saved:
                    raw = {n: saved[n] for n in saved.files}
                result, proof = model.profile(raw, config['method'], trial['parameters'], origin, config['period'], tick=tick)
                filename = trial['id']+'--'+config['method']+'.json'
                save(filename, dict(trial=trial, method=config['method'], input=row, result=result, certificates=proof))
                profiles.append(result)
                print(json.dumps(dict(completed_profile=filename, segments_processed=segments)), flush=True)
            points.append(dict(id=trial['id'], parameters=trial['parameters'], origin=origin,
                profiles=profiles, comparison=model.point_comparison(profiles, [p['period'] for p in trial['profiles']])))
        if segments != plan['total_segments'] or sources != {n: sha256(ROOT/n) for n in sources}:
            raise ValueError('complete segment count or frozen source binding changed')
        authenticate_raw(plan)
        save('summary.json', dict(experiment_id='EXP-520', status='completed', binding=binding,
            marker_sha256=sha256(MARKER), points=points, segments=segments, files=inventory(output),
            completed_utc=utc(), elapsed_seconds=time.monotonic()-started,
            new_integrations=0, exact_flow_completeness=False, symbolic_chains_verified=False, D_identified=False,
            all_profiles_qualified=all(p['comparison']['qualified'] for p in points),
            all_nearest_consistent=all(p['comparison']['consistent_nearest'] for p in points)))
        print(json.dumps(dict(completed=True, summary_sha256=sha256(output/'summary.json'))), flush=True)
    except Exception as error:
        save('failure.json', dict(experiment_id='EXP-520', error_type=type(error).__name__, error=str(error),
            consumed_attempt=True, segments_processed=segments, utc=utc(), new_integrations=0), failure=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true'); parser.add_argument('--validate', action='store_true')
    parser.add_argument('--startup', action='store_true'); parser.add_argument('--execute', action='store_true')
    parser.add_argument('--source-commit'); parser.add_argument('--remote-ref'); parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if sum((args.prepare, args.validate, args.startup, args.execute)) != 1:
        parser.error('choose exactly one operation')
    if args.prepare:
        if MARKER.exists(): raise ValueError('consumed experiment cannot be prepared again')
        metadata = input_metadata()
        if META.exists():
            if json.loads(META.read_bytes()) != metadata: raise ValueError('existing metadata differs')
        else: write_json(META, metadata)
        plan = expected()
        if PLAN.exists():
            if json.loads(PLAN.read_bytes()) != plan: raise ValueError('existing plan differs')
        else: write_json(PLAN, plan)
        print(json.dumps(dict(plan_sha256=sha256(PLAN), segments=plan['total_segments'], target_data_opened=False)))
    elif args.validate: print(json.dumps(dict(valid=True, plan_sha256=sha256(PLAN), experiment_id=load()['experiment_id'])))
    elif args.startup: print(json.dumps(startup(load())))
    else:
        if not args.source_commit or not args.remote_ref or not args.output: parser.error('execution requires source, remote and fresh output')
        execute(args.output.resolve(), args.source_commit, args.remote_ref)


if __name__ == '__main__':
    main()
