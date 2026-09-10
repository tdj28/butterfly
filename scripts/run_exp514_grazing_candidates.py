#!/usr/bin/env python3
"""Bounded all-five grazing-root and dense two-sided event qualification."""
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
from butterfly.poincare import PoincareSection
from scripts import run_exp513_candidate_folds as previous
from scripts import verify_exp513_public_folds as public
from scripts import run_exp492_event_boundaries as old
from scripts import exp514_grazing_candidates as model

ROOT = previous.ROOT
PLAN = ROOT/'experiments/manifests/EXP-514-candidate-grazing-boundaries.json'
RECEIPT = 'docs/experiments/receipts/EXP-513-candidate-fold-qualification-result.json'
INPUTS = dict(previous.INPUTS, **{RECEIPT: '64e60c557edf02ce0fabe17305e6049a6a043e3088812039e1dd07a9c2452741'})
EXPLICIT = ['scripts/run_exp514_grazing_candidates.py', 'scripts/audit_exp514_grazing_candidates.py',
    'scripts/exp514_grazing_candidates.py', 'scripts/verify_exp513_public_folds.py',
    'tests/test_exp514_grazing_candidates.py', 'docs/experiments/EXP-514-candidate-grazing-boundaries.md',
    'experiments/manifests/EXP-514-candidate-grazing-boundaries.json',
    'scripts/audit_exp492_event_boundaries.py', 'experiments/manifests/EXP-492-event-boundaries.json']
coverage, base = previous.coverage, previous.base


def expected():
    if any(sha256(ROOT/n) != h for n, h in INPUTS.items()):
        raise ValueError('fixed grazing inputs differ')
    public.verify(ROOT/RECEIPT, INPUTS[RECEIPT])
    # The real public verifier above validates this parent plan and every
    # inherited input. Reuse its authenticated values instead of recursively
    # re-running the entire historical verifier twice more.
    parent = json.loads(previous.PLAN.read_bytes())
    before = json.loads((ROOT/previous.RECEIPT).read_bytes())
    latest = json.loads((ROOT/RECEIPT).read_bytes())
    grazing = json.loads(old.PLAN.read_bytes())
    grazing = {k: v for k, v in grazing.items() if k in (
        'solvers', 'rtol', 'atol', 'max_step', 'newton_iterations', 'root_plane', 'root_velocity',
        'minimum_unfolding', 'minimum_curvature', 'solver_u', 'solver_time', 'solver_scaled_state',
        'scales', 'window', 'side_residual', 'minimum_angle', 'square_root_ratio_relative_error',
        'side_solver_time', 'side_solver_scaled_state', 'guard', 'extremum_margin')}
    return dict(experiment_id='EXP-514', status='prospective-outcome-informed-grazing-diagnostic',
        inputs=INPUTS, candidates=model.selection(before, latest), numerical=parent['numerical'],
        grazing=grazing, attempts=1, paid_review='not-requested-human-approval-policy',
        limits=dict(target_ivps=160, wall_seconds=3600, output_bytes=2*1024**3,
            initial_free_bytes=11*1024**3, minimum_free_bytes=8*1024**3, failure_reserve_bytes=1024**2),
        controls=dict(kinds=['grazing', 'no-root-in-box'], solvers=['DOP853', 'Radau'],
            maximum_ivps=64, output_bytes=64*1024**2, wall_seconds=180),
        symbolic_chains_verified=False,
        source_paths=sorted(set(parent['source_paths']) | set(old.SOURCES) | set(EXPLICIT)))


def load():
    p = json.loads(PLAN.read_bytes())
    if p != expected():
        raise ValueError('frozen grazing plan differs')
    return p


def validate():
    p = load()
    if not base.imported() <= set(p['source_paths']):
        raise ValueError('source closure incomplete: '+str(base.imported()-set(p['source_paths'])))
    if any(p['grazing'][k] != p['numerical'][k] for k in ('rtol', 'atol', 'max_step', 'guard', 'extremum_margin')):
        raise ValueError('shooting and dense settings diverge')
    return dict(valid=True, new_integrations=0, candidates=5, maximum_target_ivps=160)


def startup(p):
    target = Path(tempfile.mkdtemp(prefix='exp514-startup-')).resolve()
    names = set(p['source_paths']) | set(INPUTS)
    for name in names:
        dest = target/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/name, dest)
    code = (f'import sys;from pathlib import Path;root=Path({str(target)!r});'
        f'sys.path[:0]={[str(target),str(target/"python")]!r};'
        'from scripts.run_exp514_grazing_candidates import main;main();'
        'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
        'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    child = subprocess.run([sys.executable, '-I', '-B', '-c', code], cwd=target,
        capture_output=True, text=True, check=True, timeout=180)
    hashes = {n: sha256(target/n) for n in sorted(names)}
    if hashes != {n: sha256(ROOT/n) for n in sorted(names)}:
        raise ValueError('isolated sources changed')
    return dict(passed=True, isolated=True, new_integrations=0, sources=hashes,
                stdout=child.stdout, stderr=child.stderr)


def produce(c, p, folder, budget, save, fields=None):
    rhs, jac, section = coverage.fields(c) if fields is None else fields
    def shoot(candidate, method):
        label = c['id']+'--'+method
        save(label+'-started.json', dict(candidate=c, method=method, phase='shooting', started_utc=base.utc()))
        names = []
        def retain(i, raw):
            name = label+f'--newton-{i}.npz'
            base.retain_npz(folder/name, raw)
            names.append(name)
        result = model.boundary.shoot(rhs, jac, section, c, p['grazing'], method, retain, lambda: budget(True))
        result['raw_files'] = names
        save(label+'.json', result)
        return result
    def observe(candidate, i, u, method):
        label = c['id']+f'--side-{i}--'+method
        save(label+'-started.json', dict(candidate=c, method=method, phase='side', u=u, started_utc=base.utc()))
        result = coverage.dense.capture(c, u, method, p['numerical'], rhs, jac, section,
            lambda name, raw: base.retain_npz(folder/(label+'--'+name+'.npz'), raw), budget)
        save(label+'.json', result)
        return result
    result = model.run_candidate(c, p['grazing'], shoot, observe)
    save(c['id']+'.json', result)
    return result


def controls(p, output):
    """Actual combined producer, known analytic event mechanism and negative."""
    output.mkdir(parents=True, exist_ok=False)
    limits = dict(p['limits'], output_bytes=p['controls']['output_bytes'])
    calls, started = 0, time.monotonic()
    def budget(integrating=False):
        nonlocal calls
        if calls >= p['controls']['maximum_ivps'] or time.monotonic()-started > p['controls']['wall_seconds']:
            raise RuntimeError('control budget exceeded')
        if integrating:
            calls += 1
    def save(name, value):
        coverage.write(output, output/name, value, limits)
    rows = []
    with coverage.producers(base, output, limits):
        for spec in (old.control_specs()[0], old.control_specs()[3]):
            c = dict(spec, count=2)
            rhs, jac = old.fields_for_control(c)
            result = produce(c, p, output, budget, save,
                (rhs, jac, PoincareSection((0., 1., 0.), 0., -1)))
            positive = c['kind'] == 'grazing'
            if result['decision']['qualified'] != positive:
                raise ValueError('analytic grazing/no-root control failed')
            if positive:
                for r in result['roots']:
                    q = r['shooting']['trace'][-1]
                    if abs(q['u']+1e-5) > 1e-9 or abs(q['time']-1.) > 1e-8:
                        raise ValueError('analytic root differs')
                for s in result['sides']:
                    x = 2e-5+2*s['u']
                    exact = [1.-base.np.sqrt(-x)] if x < 0 else []
                    for v in s['profiles']:
                        times = [e['time'] for e in v['report']['reconstructed'] if e['accepted']]
                        if len(times) != len(exact) or not base.np.allclose(times, exact, rtol=0, atol=1e-7):
                            raise ValueError('complete analytic accepted events differ')
            elif result['sides'] or any(r['shooting']['reason'] != 'prospective search box exceeded' for r in result['roots']):
                raise ValueError('analytic negative termination differs')
            rows.append(result)
    saved = dict(passed=True, rows=rows, control_ivps=calls, files=inventory(output),
                 dense_control_replay=previous.previous.controls())
    save('controls.json', saved)
    return saved


def execute(output, source, remote):
    p = load()
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
    if git('rev-parse', 'HEAD') != source or git('status', '--porcelain') or git('ls-remote', 'origin', remote).split() != [source, remote]:
        raise ValueError('clean exact live-pushed source required')
    validate()
    root = ROOT/'artifacts/EXP-514'
    marker = root/'target-once.json'
    output = output.resolve()
    if root not in output.parents or output.exists() or marker.exists() or shutil.disk_usage(ROOT).free < p['limits']['initial_free_bytes']:
        raise ValueError('fresh unconsumed output and disk reserve required')
    isolated = startup(p)
    control_result = controls(p, root/('execution-controls-'+source[:7]))
    free = shutil.disk_usage(ROOT).free
    if free < p['limits']['initial_free_bytes']:
        raise ValueError('initial free-space reserve after controls')
    output.mkdir(parents=True)
    binding = dict(source_commit=source, remote_ref=remote, started_utc=base.utc(),
        plan_sha256=sha256(PLAN), inputs=INPUTS, sources={n: sha256(ROOT/n) for n in p['source_paths']},
        initial_free_bytes=free, runtime=dict(python=sys.version, numpy=base.np.__version__, scipy=base.scipy.__version__),
        paid_review=p['paid_review'])
    start, calls = time.monotonic(), 0
    progress = []
    def save(name, value, reserve=True):
        coverage.write(output, output/name, value, p['limits'], reserve)
    def budget(integrating=False):
        nonlocal calls
        if time.monotonic()-start > p['limits']['wall_seconds'] or shutil.disk_usage(ROOT).free < p['limits']['minimum_free_bytes']:
            raise RuntimeError('EXP-514 time/free-space cap')
        if integrating:
            if calls >= p['limits']['target_ivps']:
                raise RuntimeError('EXP-514 IVP cap')
            calls += 1
    def timeout(*_):
        raise TimeoutError('EXP-514 wall deadline')
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(p['limits']['wall_seconds'])
    try:
        save('binding.json', binding)
        save('startup.json', isolated)
        save('controls.json', control_result)
        write_bounded_json(root, marker, binding, limit_bytes=directory_bytes(root)+1024**2,
                           minimum_free_bytes=p['limits']['minimum_free_bytes'])
        rows = []
        with coverage.producers(base, output, p['limits']):
            for c in p['candidates']:
                progress.append(dict(id=c['id'], status='started'))
                rows.append(produce(c, p, output, budget, save))
                progress[-1]['status'] = 'completed'
                print(json.dumps(dict(candidate=c['id'], target_ivps=calls,
                    qualified=rows[-1]['decision']['qualified'])), flush=True)
        budget()
        save('summary.json', dict(experiment_id='EXP-514', status='completed', binding=binding,
            rows=rows, target_ivps=calls, progress=progress, elapsed_seconds=time.monotonic()-start,
            completed_utc=base.utc(), marker_sha256=sha256(marker), files=inventory(output),
            symbolic_chains_verified=False))
        print(json.dumps(dict(completed=True, target_ivps=calls, summary_sha256=sha256(output/'summary.json'))), flush=True)
    except BaseException as exc:
        signal.alarm(0)
        save('failure.json', dict(error_type=type(exc).__name__, message=str(exc), target_ivps=calls,
            utc=base.utc(), progress=progress, files=inventory(output)), False)
        raise
    finally:
        signal.alarm(0)


def main():
    from scripts import audit_exp514_grazing_candidates  # noqa: F401
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    for name in ('prepare', 'startup', 'controls', 'execute'):
        modes.add_argument('--'+name, action='store_true')
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--source-commit')
    parser.add_argument('--remote-ref')
    a = parser.parse_args()
    if a.prepare:
        write_bounded_json(PLAN.parent, PLAN, expected(), limit_bytes=directory_bytes(PLAN.parent)+1024**2)
    elif a.execute:
        if not all((a.output_dir, a.source_commit, a.remote_ref)):
            parser.error('output, source and remote required')
        execute(a.output_dir, a.source_commit, a.remote_ref)
    elif a.controls:
        if a.output_dir is None:
            parser.error('fresh control output required')
        r = controls(load(), a.output_dir)
        print(json.dumps(dict(passed=r['passed'], control_ivps=r['control_ivps'])))
    else:
        print(json.dumps(startup(load()) if a.startup else validate()))


if __name__ == '__main__':
    main()
