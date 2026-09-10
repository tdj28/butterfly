#!/usr/bin/env python3
"""Frozen two-step contact continuation with refreshed derivatives and raw retention."""
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
from scripts import run_exp521_critical_response as parent
from scripts import exp523_refreshed_path as model
from scripts import run_exp522_nonlinear_refinement as accepted

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT/'experiments/manifests/EXP-523-refreshed-contact-path.json'
MARKER = ROOT/'artifacts/EXP-523/target-once.json'
P521 = 'experiments/manifests/EXP-521-critical-periodic-response.json'
R521 = 'docs/experiments/receipts/EXP-521-critical-periodic-response-result.json'
P522 = 'experiments/manifests/EXP-522-nonlinear-contact-refinement.json'
R522 = 'docs/experiments/receipts/EXP-522-nonlinear-contact-refinement-result.json'
INPUTS = dict(accepted.INPUTS, **{P522: '5caf77cfce8c6e3caac3ccd35ad1cbb4279d7d9386407d6958af9ac466bba783',
    R522: '0f942da7d44560dc57feed927263198f68e389bb53472f0f0e6028927d52c866'})
EXPLICIT = ['scripts/run_exp523_refreshed_path.py', 'scripts/exp523_refreshed_path.py',
    'scripts/audit_exp523_refreshed_path.py', 'tests/test_exp523_refreshed_path.py',
    'tests/test_exp523_runner.py', 'scripts/deploy_exp523_prax.py',
    'docs/experiments/EXP-523-refreshed-contact-path.md',
    'experiments/manifests/EXP-523-refreshed-contact-path.json', 'pyproject.toml', 'uv.lock', '.gitignore']
prior = parent.prior
read = parent.read


def inputs():
    if any(sha256(ROOT/n) != h for n, h in INPUTS.items()): raise ValueError('fixed audited parent bytes differ')
    receipt = read(ROOT/R522)
    if (receipt['experiment_id'] != 'EXP-522' or not receipt['passed']
            or receipt['source_commit'] != '41bb1943fdcd0756a1f8077241287272afbf8548'
            or receipt['plan_sha256'] != INPUTS[P522] or not receipt['result']['decision']['qualified']
            or any(receipt[n] for n in ('symbolic_chains_verified', 'D_identified', 'exact_critical_locus_proved'))):
        raise ValueError('authenticated accepted nonlinear correction required')
    point = receipt['result']['correction']
    if not model.tight(point): raise ValueError('tight qualified initial contact required')
    source = model.recenter(accepted.inputs(), point)
    match = parent.model.match(source['census'], source['census'])
    if not match['qualified'] or not prior.coverage.public.equal(match['gaps'], source['gaps']):
        raise ValueError('unique complete initial root identities required')
    return source


def expected():
    source = inputs(); p = read(ROOT/P522)
    return dict(experiment_id='EXP-523', status='prospective-outcome-informed-refreshed-continuation',
        inputs=INPUTS, anchor=source['anchor'], maximum_steps=model.MAX_STEPS,
        numerical=p['numerical'], historical_targets=p['historical_targets'], periodic=p['periodic'],
        controls=p['controls'], solvers=p['solvers'], phases=p['phases'], census=p['census'],
        attempts=1, response_points_per_step=8, maximum_measurements=20, folds_per_point=4,
        normalized_increments=dict(a=1e-5, c=.005), full_state_radius=1e-4,
        accepted_contact_radius=model.CONTACT, prediction_relative_tolerance=.1,
        response_relative_tolerance=.05, curvature_relative_tolerance=.05, maximum_refinement_residual_ratio=.1,
        progress='Root 5 improves in all four contexts relative to each accepted step anchor; root 13 retains prediction and identity.',
        derivative_policy='Refresh all a/c stencil points at every accepted anchor; one normal correction can reuse only that step response.',
        runtime_policy='Managed CPython 3.13; uv sync --locked --no-install-project; record exact runtime versions.',
        limits=dict(target_ivps=3200, wall_seconds=21600, maximum_segments=2200000, output_bytes=10*1024**3,
            initial_free_bytes=20*1024**3, minimum_free_bytes=8*1024**3, failure_reserve_bytes=1024**2),
        paid_review='not-requested-human-approval-policy',
        symbolic_chains_verified=False, D_identified=False, exact_critical_locus_proved=False,
        source_paths=sorted(set(p['source_paths']) | set(EXPLICIT)), ancillary_inputs=p['ancillary_inputs'])


def load():
    p = read(PLAN)
    if p != expected(): raise ValueError('complete frozen refreshed-path plan differs')
    if any(sha256(ROOT/n) != h for n, h in p['ancillary_inputs'].items()): raise ValueError('ancillary input differs')
    return p


def validate():
    from scripts import audit_exp523_refreshed_path  # noqa: F401
    p = load(); source = inputs()
    missing = prior.base.imported()-set(p['source_paths'])
    if missing: raise ValueError('deployed import closure incomplete: '+str(sorted(missing)))
    for spec in model.stencil(source['anchor'], 0, 'a')+model.stencil(source['anchor'], 0, 'c'):
        for candidate in prior.model.candidates(source['rows'], spec, prior.prior.transport.offset(spec['parameters'])):
            rhs, _, section = prior.coverage.fields(candidate)
            for u in [*candidate['u_box'], candidate['seed_u']-candidate['epsilon'], candidate['seed_u']+candidate['epsilon']]:
                q = prior.base.np.asarray(candidate['initial_state'])+u*prior.base.np.asarray(candidate['initial_tangent'])
                f = rhs(0., q)
                if (abs(section.value(q)) > 1e-10 or not section.accepts(q) or f[1] >= 0
                        or abs(f[1])/prior.base.np.linalg.norm(f) < p['numerical']['thresholds']['angle']):
                    raise ValueError('initial affine section orientation differs')
    return dict(valid=True, new_integrations=0, maximum_steps=2, maximum_target_ivps=3200,
                analytic_controls=parent.census_run.controls())


def startup(p):
    root = Path(tempfile.mkdtemp(prefix='exp523-startup-')).resolve()
    names = set(p['source_paths']) | set(INPUTS) | set(p['ancillary_inputs'])
    for n in names:
        dest = root/n; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT/n, dest)
    code = (f'import sys;from pathlib import Path;root=Path({str(root)!r});'
        'sys.path[:0]=[str(root),str(root/"python")];'
        'from scripts.run_exp523_refreshed_path import validate;import json;print(json.dumps(validate()));'
        'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
        'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    child = subprocess.run([sys.executable, '-I', '-B', '-c', code], cwd=root, capture_output=True,
        text=True, check=True, timeout=120)
    hashes = {n: sha256(root/n) for n in sorted(names)}
    if hashes != {n: sha256(ROOT/n) for n in names} or list(root.rglob('*.pyc')): raise ValueError('sealed startup bytes changed')
    shutil.rmtree(root)
    return dict(passed=True, isolated=True, target_data_opened=False, sources=hashes, validation=json.loads(child.stdout))


def execute(output, commit, remote):
    p = load(); source = inputs()
    def git(*args): return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
    if git('rev-parse', 'HEAD') != commit or git('status', '--porcelain') or git('ls-remote', 'origin', remote).split() != [commit, remote]:
        raise ValueError('clean exact live-pushed source required')
    validate(); handshake = startup(p)
    root = MARKER.parent; output = output.resolve(); free = shutil.disk_usage(ROOT).free
    if root not in output.parents or output.exists() or output.is_symlink() or MARKER.exists() or free < p['limits']['initial_free_bytes']:
        raise ValueError('fresh unconsumed namespace and disk reserve required')
    output.mkdir(parents=True)
    binding = dict(experiment_id='EXP-523', source_commit=commit, remote_ref=remote, started_utc=prior.base.utc(),
        plan_sha256=sha256(PLAN), inputs=INPUTS, sources={n: sha256(ROOT/n) for n in p['source_paths']},
        initial_free_bytes=free, runtime=dict(python=sys.version, numpy=prior.base.np.__version__, scipy=prior.base.scipy.__version__),
        paid_review=p['paid_review'])
    started = time.monotonic(); budget = prior.Budget(p['limits'], ROOT, started); segments = 0; progress = []
    def save(name, value, reserve=True): prior.coverage.write(output, output/name, value, p['limits'], reserve)
    def tick():
        nonlocal segments
        segments += 1
        if segments > p['limits']['maximum_segments']: raise ValueError('refreshed-path segment cap')
        if segments % 1000 == 0: budget()
    def measure(spec, current):
        progress.append(dict(id=spec['id'], status='started'))
        point = prior.measure(spec, output, p, current, budget, save)
        extended = parent.stationarity(output/spec['id'], point, current,
            lambda name, value: save(spec['id']+'/'+name, value), tick)
        save(spec['id']+'/critical-point.json', extended); progress[-1]['status'] = 'completed'
        print(json.dumps(dict(completed_point=spec['id'], target_ivps=budget.calls, segments=segments)), flush=True)
        return extended
    def timeout(*_):
        budget.failure = 'EXP-523 wall deadline'
        raise prior.base.previous.cycles_run.BudgetStop(budget.failure)
    signal.signal(signal.SIGALRM, timeout); signal.alarm(p['limits']['wall_seconds'])
    try:
        save('binding.json', binding); save('startup.json', handshake); save('controls.json', parent.census_run.controls())
        write_bounded_json(root, MARKER, binding, limit_bytes=directory_bytes(root)+1024**2,
                           minimum_free_bytes=p['limits']['minimum_free_bytes'])
        with prior.coverage.producers(prior.base, output, p['limits']): result = model.follow(source, measure)
        budget()
        if binding['sources'] != {n: sha256(ROOT/n) for n in p['source_paths']}: raise ValueError('source changed during target')
        save('summary.json', dict(experiment_id='EXP-523', status='completed', binding=binding, result=result,
            point_progress=progress, target_ivps=budget.calls, segments=segments, elapsed_seconds=time.monotonic()-started,
            completed_utc=prior.base.utc(), files=inventory(output), marker_sha256=sha256(MARKER), symbolic_chains_verified=False))
        print(json.dumps(dict(completed=True, summary_sha256=sha256(output/'summary.json'))), flush=True)
    except BaseException as exc:
        signal.alarm(0)
        save('failure.json', dict(error_type=type(exc).__name__, message=str(exc), utc=prior.base.utc(),
            target_ivps=budget.calls, segments=segments, point_progress=progress, files=inventory(output)), False)
        raise
    finally: signal.alarm(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); modes = parser.add_mutually_exclusive_group()
    for name in ('prepare', 'startup', 'execute'): modes.add_argument('--'+name, action='store_true')
    parser.add_argument('--output', type=Path); parser.add_argument('--source-commit'); parser.add_argument('--remote-ref')
    args = parser.parse_args()
    if args.prepare:
        if MARKER.exists(): raise ValueError('consumed attempt cannot be prepared')
        write_bounded_json(PLAN.parent, PLAN, expected(), limit_bytes=directory_bytes(PLAN.parent)+1024**2)
    elif args.execute:
        if not all((args.output, args.source_commit, args.remote_ref)): parser.error('output, source, remote required')
        execute(args.output, args.source_commit, args.remote_ref)
    else: print(json.dumps(startup(load()) if args.startup else validate()))
