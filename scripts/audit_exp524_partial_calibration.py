#!/usr/bin/env python3
"""One-shot read-only numerical replay of EXP-523's eight complete points."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

from butterfly._paired_startup import sha256
from butterfly.bounded_json import write_bounded_json
from scripts import inspect_exp523_failure as preservation
from scripts import run_exp523_refreshed_path as parent
from scripts import audit_exp523_refreshed_path as full

ROOT = Path(__file__).resolve().parents[1]
PLAN = 'experiments/manifests/EXP-524-partial-calibration-audit.json'
CYCLE = 'experiments/manifests/EXP-524-recovery-cycle.json'
RECEIPT = 'docs/experiments/receipts/EXP-523-timeout-preservation.json'
REF = 'refs/heads/codex/exp524-prax-execution'
CYCLE_SHA = '7bdd491d1c2da013d4dc07b25bd925b339a1d32859a7283ae71480ed577b5f18'
HOURS = 43200
MAX_OUTPUT = 128*1024**2
MIN_FREE = 8*1024**3
IDS = [f'step-0-{axis}-{i}' for axis in ('a', 'c') for i in range(4)]
PROGRESS = [dict(id=n, status='completed') for n in IDS]+[dict(id='step-0-predictor', status='started')]
EXPLICIT = [PLAN, CYCLE, RECEIPT, 'scripts/audit_exp524_partial_calibration.py',
    'scripts/deploy_exp524_prax.py', 'scripts/inspect_exp523_failure.py',
    'tests/test_exp524_partial_calibration.py', 'docs/experiments/EXP-524-partial-calibration-audit.md']


def utc():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_bytes())


def expected():
    p = parent.load()
    return dict(experiment_id='EXP-524', status='post-timeout-recovery-audit',
        parent_source_commit=preservation.COMMIT, parent_diagnostic_hashes=preservation.EXPECTED,
        recovery_cycle_sha256=sha256(ROOT/CYCLE), parent_preservation_sha256=sha256(ROOT/RECEIPT),
        completed_ids=IDS, incomplete_id='step-0-predictor', expected_audited_ivps=864,
        expected_census_segments=667500, parent_ivp_calls_started=875,
        parent_inventory_files=1299, parent_inventory_bytes=3241861585,
        limits=dict(wall_seconds=HOURS, output_bytes=MAX_OUTPUT, minimum_free_bytes=MIN_FREE,
                    initial_free_bytes=MIN_FREE+MAX_OUTPUT+1024**2),
        attempts=1, new_integrations=0, paid_api_calls=0, new_provider_creates=0,
        numerical_policy='Unchanged EXP-523 raw point, root census and scalar response checks; no successful path summary invented.',
        incomplete_policy='Byte inventory only. Do not parse or reuse incomplete predictor measurements.',
        decision='Audit all eight points regardless of scientific qualification. Integrity failures abort. Only complete qualified geometry and response can license a separately frozen successor.',
        runtime=dict(python='3.13.13', numpy='2.5.1', scipy='1.18.0'),
        paid_review='not-requested-human-approval-policy',
        source_paths=sorted(set(p['source_paths']) | set(p['inputs']) | set(p['ancillary_inputs']) | set(EXPLICIT)),
        symbolic_chains_verified=False, complete_exp523_audit=False)


def validate():
    p = read(ROOT/PLAN)
    if p != expected():
        raise ValueError('complete recovery audit plan differs')
    cycle = read(ROOT/CYCLE)
    if sha256(ROOT/CYCLE) != CYCLE_SHA:
        raise ValueError('approved recovery ledger byte identity differs')
    if (cycle['experiment_id'] != 'EXP-524' or cycle['tier'] != 'C'
            or cycle['audit_wall_seconds'] != HOURS or cycle['audit_attempts'] != 1
            or cycle['new_integrations'] != 0 or cycle['paid_api_calls'] != 0
            or cycle['new_provider_creates'] != 0 or cycle['attempt_id'] != 'EXP-524-audit-01'
            or cycle['parent_source_commit'] != preservation.COMMIT
            or cycle['parent_failure_sha256'] != preservation.EXPECTED['failure.json']
            or cycle['human_approval']['response'] != 'please proceed'):
        raise ValueError('historical recovery authority differs')
    if sha256(ROOT/RECEIPT) != '0c440f75221792c55b5c83b0dcc2c7175dbd9a9057bbc32fb380ed4c3783a19a':
        raise ValueError('fixed preservation receipt differs')
    if sha256(ROOT/'scripts/inspect_exp523_failure.py') != 'ca9abfab3e34b613e02536df174d19be8e9ce33cde1ebda84e3f60cfeadaf67e':
        raise ValueError('historical inspector differs')
    names = set(p['source_paths'])
    for n in names:
        preservation.safe_file(ROOT, n)
    missing = parent.prior.base.imported()-names
    if missing:
        raise ValueError('recovery import closure incomplete: '+str(sorted(missing)))
    return dict(valid=True, raw_inputs_opened=False, new_integrations=0,
                source_files=len(names), wall_seconds=HOURS)


def partition(files):
    """Separate every retained byte; partial predictor is never a measured point."""
    common = {'binding.json', 'startup.json', 'controls.json'}
    groups = {n: {} for n in IDS+['step-0-predictor']}
    for name, item in files.items():
        if name in common:
            continue
        head, sep, tail = name.partition('/')
        if not sep or not tail or head not in groups:
            raise ValueError('unplanned retained stage/file')
        groups[head][tail] = item
    if not common.issubset(files) or any(not g for g in groups.values()):
        raise ValueError('missing retained stage or common metadata')
    if any(n in groups['step-0-predictor'] for n in ('point.json', 'critical-point.json', 'cycle.json')):
        raise ValueError('expected interrupted predictor, not completed measurement')
    return groups


def check_failure(failure, binding):
    if (failure['error_type'] != 'BudgetStop' or failure['message'] != 'EXP-523 wall deadline'
            or failure['point_progress'] != PROGRESS or failure['target_ivps'] != 875
            or failure['segments'] != 667500 or binding['source_commit'] != preservation.COMMIT
            or binding['plan_sha256'] != preservation.EXPECTED['plan']):
        raise ValueError('authenticated historical failure semantics differ')
    elapsed = (datetime.fromisoformat(failure['utc'])-datetime.fromisoformat(binding['started_utc'])).total_seconds()
    if not 21600 <= elapsed < 21601:
        raise ValueError('historical failure interval differs')
    groups = partition(failure['files'])
    if len(failure['files']) != 1299 or sum(r['bytes'] for r in failure['files'].values()) != 3241861585:
        raise ValueError('complete historical inventory accounting differs')
    return groups


@contextmanager
def forbid_integrations():
    """Deny solver execution even through imported function aliases."""
    import scipy.integrate
    import scipy.integrate._ivp.ivp
    objects = {scipy.integrate.solve_ivp}
    def forbidden(*args, **kwargs):
        raise RuntimeError('EXP-524 forbids new integrations')
    patches = []
    for module in list(sys.modules.values()):
        if module is None:
            continue
        for name, value in list(vars(module).items()):
            if any(value is obj for obj in objects):
                patches.append((module, name, value)); setattr(module, name, forbidden)
    # Low-level stepping is also forbidden; dense-output evaluation remains legal.
    for cls in (scipy.integrate.DOP853, scipy.integrate.Radau, scipy.integrate.RK45,
                scipy.integrate.RK23, scipy.integrate.BDF, scipy.integrate.LSODA):
        patches.append((cls, 'step', cls.step)); cls.step = forbidden
    try:
        yield
    finally:
        for obj, name, value in reversed(patches):
            setattr(obj, name, value)


def response_audit(source, points):
    """Reuse separate scalar checks without claiming a completed path/predictor."""
    aa, cc = points[:4], points[4:]
    fresh = parent.model.response(source, aa, cc, 0)
    row = dict(anchor=source['anchor'], a_points=aa, c_points=cc, response=fresh, proposal=None)
    full.scalar_check(dict(steps=[row], accepted=[], completed_steps=0, qualified=False), source)
    # No predictor proposal is consumed here. Its existence/forecast will be
    # checked inside the separately frozen one-step successor.
    return fresh


def replay(raw, failure, binding, groups, progress):
    p = parent.load(); source = parent.inputs()
    startup = read(raw/'startup.json')
    original_files = set(p['source_paths']) | set(parent.INPUTS) | set(p['ancillary_inputs'])
    expected_validation = dict(valid=True, new_integrations=0, maximum_steps=2,
                              maximum_target_ivps=3200, analytic_controls=parent.parent.census_run.controls())
    if (startup['passed'] is not True or startup['isolated'] is not True
            or startup['target_data_opened'] is not False
            or startup['sources'] != {n: sha256(ROOT/n) for n in original_files}
            or startup['validation'] != expected_validation
            or read(raw/'controls.json') != parent.parent.census_run.controls()
            or binding['sources'] != {n: sha256(ROOT/n) for n in p['source_paths']}
            or binding['inputs'] != parent.INPUTS
            or binding['initial_free_bytes'] < p['limits']['initial_free_bytes']):
        raise ValueError('original startup/source/input/controls differ')
    points = []; calls = segments = 0
    def tick():
        nonlocal segments
        segments += 1
        if segments > 667500:
            raise ValueError('partial audit census exceeds retained complete set')
    specs = parent.model.stencil(source['anchor'], 0, 'a')+parent.model.stencil(source['anchor'], 0, 'c')
    for spec in specs:
        stage = raw/spec['id']
        progress.append(dict(id=spec['id'], status='started'))
        candidates = parent.prior.model.candidates(source['rows'], spec, parent.prior.prior.transport.offset(spec['parameters']))
        if read(stage/'inputs.json') != dict(spec=spec, candidates=candidates):
            raise ValueError('candidate inputs differ')
        rows, paths, count = full.folds.check_rows(stage, candidates, p, binding, failure['utc'])
        calls += count
        cycle = read(stage/'cycle.json')
        cycle_paths, count = full.folds.raw.old.check_cycle(stage, cycle, spec, source['cycle']['profiles'][0]['correction'], p['periodic'])
        calls += count
        point = parent.prior.summarize(spec, rows, cycle, p, source)
        full.folds.transport_audit.scalar_decision(source['rows'], rows, point['fold_identity'])
        if point['contact'] is not None:
            scalar = full.folds.raw.old.scalar_contact([r['assessment']['comparison'] for r in rows], cycle)
            if not full.folds.raw.old.periodic_audit.numeric_equal(scalar, point['contact']):
                raise ValueError('scalar contact differs')
        if not parent.prior.coverage.public.equal(point, read(stage/'point.json')):
            raise ValueError('raw point replay differs')
        certificates = {m: read(stage/('stationarity--'+m+'.json'))['certificates'] for m in p['solvers']}
        def check_product(name, value):
            if not full.roots.same(value, read(stage/name)):
                raise ValueError('separate exact polynomial census replay differs')
        extended = parent.parent.stationarity(stage, point, source, check_product, tick, certificates)
        if not full.roots.same(extended, read(stage/'critical-point.json')):
            raise ValueError('root identity or critical point differs')
        names = paths | cycle_paths | {'inputs.json', 'cycle.json', 'point.json', 'critical-point.json',
                                      'stationarity--DOP853.json', 'stationarity--Radau.json'}
        if names != set(groups[spec['id']]):
            raise ValueError('complete point file accounting differs')
        points.append(extended); progress[-1]['status'] = 'completed'
        progress[-1].update(audited_ivps=calls, census_segments=segments)
        print(json.dumps(dict(audited_point=spec['id'], audited_ivps=calls, census_segments=segments)), flush=True)
    if calls != 864 or segments != 667500:
        raise ValueError('audited complete point IVP/census accounting differs')
    response = response_audit(source, points)
    return dict(points=points, response=response, initial_anchor=source['anchor'],
        audited_ivps=calls, census_segments=segments,
        calibration_qualified=bool(all(p['qualified'] for p in points) and response['qualified']))


def runtime_check():
    import numpy
    import scipy
    actual = dict(python=sys.version.split()[0], numpy=numpy.__version__, scipy=scipy.__version__)
    if actual != read(ROOT/PLAN)['runtime'] or '/uv/python/' not in sys.base_prefix:
        raise ValueError('exact retained managed runtime required')
    return actual


def protect_historical_tree():
    """Process-local write deny for the retained task; no change to its bytes."""
    import os
    root = preservation.TASK.resolve()
    def protected(value):
        if not isinstance(value, (str, bytes, os.PathLike)):
            return False
        return Path(os.fsdecode(value)).resolve().is_relative_to(root)
    def hook(event, args):
        if event == 'open':
            path, mode, flags = args
            writing = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (
                isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if writing and protected(path):
                raise PermissionError('EXP-524 historical tree is read-only')
        elif event in ('os.remove', 'os.rmdir', 'os.mkdir', 'os.chmod', 'os.utime', 'os.truncate'):
            if protected(args[0]): raise PermissionError('EXP-524 historical tree is read-only')
        elif event in ('os.rename', 'os.link', 'os.symlink'):
            if any(protected(a) for a in args[:2]): raise PermissionError('EXP-524 historical tree is read-only')
    sys.addaudithook(hook)


def preflight(commit, *, runtime=True):
    valid = validate()
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
    if (git('rev-parse', 'HEAD') != commit or git('status', '--porcelain')
            or git('ls-remote', 'origin', REF).split() != [commit, REF]):
        raise ValueError('clean exact publicly frozen audit source required')
    p = read(ROOT/PLAN)
    if shutil.disk_usage(ROOT).free < p['limits']['initial_free_bytes']:
        raise ValueError('audit output and disk reserve required')
    actual = runtime_check() if runtime else None
    with forbid_integrations():
        parent.parent.census_run.controls()
    return dict(passed=True, raw_inputs_opened=False, new_integrations=0, source_commit=commit,
                plan_sha256=sha256(ROOT/PLAN), sources={n: sha256(ROOT/n) for n in p['source_paths']},
                runtime=actual, validation=valid)


def execute(commit):
    """Entrypoint: preflight before marker/raw; deadline covers audit and receipts."""
    handshake = preflight(commit)
    output = ROOT/'artifacts/EXP-524/audit-01'
    marker = ROOT/'artifacts/EXP-524/audit-once.json'
    if output.exists() or marker.exists() or output.is_symlink() or marker.is_symlink():
        raise ValueError('fresh recovery audit namespace required')
    output.mkdir(parents=True)
    started = time.monotonic(); progress = []
    binding = dict(experiment_id='EXP-524', attempt_id='EXP-524-audit-01', started_utc=utc(),
        source_commit=commit, plan_sha256=sha256(ROOT/PLAN), recovery_cycle_sha256=sha256(ROOT/CYCLE),
        handshake=handshake, hard_wall_seconds=HOURS, paid_api_calls=0, new_integrations=0)
    def save(name, value, failure=False):
        write_bounded_json(output, output/name, value, limit_bytes=MAX_OUTPUT,
                           minimum_free_bytes=MIN_FREE, reserve_bytes=0 if failure else 1024**2)
    def expired(*_):
        raise TimeoutError('EXP-524 twelve-hour audit deadline')
    previous = signal.signal(signal.SIGALRM, expired)
    try:
        save('binding.json', binding)
        write_bounded_json(marker.parent, marker, binding, limit_bytes=MAX_OUTPUT, minimum_free_bytes=MIN_FREE)
        signal.alarm(HOURS)
        print(json.dumps(dict(audit_started=True, started_utc=binding['started_utc'], wall_seconds=HOURS)), flush=True)
        protect_historical_tree()
        before = preservation.inspect()
        raw = preservation.TASK/'source/artifacts/EXP-523/target-eae6745d124c'
        failure = read(raw/'failure.json'); old_binding = read(raw/'binding.json')
        groups = check_failure(failure, old_binding)
        with forbid_integrations():
            result = replay(raw, failure, old_binding, groups, progress)
        after = preservation.inspect()
        if {k:v for k,v in before.items() if k != 'observed_utc'} != {k:v for k,v in after.items() if k != 'observed_utc'}:
            raise ValueError('original retained evidence changed during audit')
        if handshake['sources'] != {n: sha256(ROOT/n) for n in handshake['sources']}:
            raise ValueError('recovery source changed during audit')
        partial = groups['step-0-predictor']
        receipt = dict(experiment_id='EXP-524', passed=True, result=result, binding=binding,
            completed_utc=utc(), elapsed_seconds=time.monotonic()-started,
            original_experiment_id='EXP-523', original_status='incomplete-timeout',
            original_failure_sha256=preservation.EXPECTED['failure.json'],
            original_source_commit=preservation.COMMIT, original_preservation=after,
            original_execution_runtime=old_binding['runtime'],
            complete_points_audited=IDS, incomplete_predictor=dict(files=partial,
                file_count=len(partial), bytes=sum(r['bytes'] for r in partial.values()),
                scientifically_audited=False, used_as_measurement=False),
            point_progress=progress, new_integrations=0, paid_api_calls=0,
            complete_exp523_audit=False, symbolic_chains_verified=False, D_identified=False,
            exact_critical_locus_proved=False,
            scope='Post-timeout full retained-raw replay of all eight complete calibration points only. Separate polynomial expansion and scalar responses share parent geometry; not independent-team replication, completed EXP-523 continuation, grazing, homoclinic connection or a Jones arrow.')
        if receipt['elapsed_seconds'] > HOURS:
            raise TimeoutError('EXP-524 twelve-hour audit deadline')
        save('audit.json', receipt)
        print(json.dumps(dict(audit_completed=True, receipt_sha256=sha256(output/'audit.json'))), flush=True)
    except BaseException as exc:
        signal.alarm(0)
        save('failure.json', dict(experiment_id='EXP-524', utc=utc(), error_type=type(exc).__name__,
            message=str(exc), elapsed_seconds=time.monotonic()-started, point_progress=progress,
            new_integrations=0, historical_write_denied=True, preservation_verified=False), failure=True)
        raise
    finally:
        signal.alarm(0); signal.signal(signal.SIGALRM, previous)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--prepare', action='store_true')
    modes.add_argument('--preflight', action='store_true')
    modes.add_argument('--execute', action='store_true')
    parser.add_argument('--commit')
    args = parser.parse_args()
    if args.prepare:
        write_bounded_json(ROOT/PLAN.rsplit('/', 1)[0], ROOT/PLAN, expected(), limit_bytes=64*1024**2)
    elif args.preflight or args.execute:
        if not args.commit: parser.error('exact source commit required')
        if args.execute: execute(args.commit)
        else: print(json.dumps(preflight(args.commit)))
    else:
        print(json.dumps(validate()))


if __name__ == '__main__':
    main()
