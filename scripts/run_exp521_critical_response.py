#!/usr/bin/env python3
"""Frozen c-response test of contact-preserving periodic reinjection geometry."""
import argparse
from copy import deepcopy
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
from butterfly.models import RosslerParameters, rossler_equilibria
from scripts import run_exp519_fold_response as prior
from scripts import exp520_periodic_census as census
from scripts import run_exp520_periodic_census as census_run
from scripts import exp521_critical_response as model

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT/'experiments/manifests/EXP-521-critical-periodic-response.json'
MARKER = ROOT/'artifacts/EXP-521/target-once.json'
P519 = 'experiments/manifests/EXP-519-fixed-c-fold-response.json'
P502 = 'experiments/manifests/EXP-502-joint-contact-search.json'
R519 = 'docs/experiments/receipts/EXP-519-fixed-c-fold-response-result.json'
R520 = 'docs/experiments/receipts/EXP-520-periodic-stationarity-census-result.json'
INPUTS = {P519: '59b960184c36eedfa69dca805a721ddd1d9ea38b229747419bfed9492b3ce81e',
    P502: '20c9fc885f2eeaf8df6225e487f67ee5d531b64ccaa4e0fe2e7e32bb28091038',
    R519: '92ff9159ca3de7794a481e9d682d02626b945495f3ad87e6c7d095137f0117ec',
    R520: 'cb0c5983e0ec2d6c0dc6e7ebf4f4569c028d84f7f6ce8b8ea67fac5465a00b23'}
EXPLICIT = ['scripts/run_exp521_critical_response.py', 'scripts/exp521_critical_response.py',
    'scripts/audit_exp521_critical_response.py', 'tests/test_exp521_critical_response.py',
    'tests/test_exp521_runner.py', 'docs/experiments/EXP-521-critical-periodic-response.md',
    'experiments/manifests/EXP-521-critical-periodic-response.json']


def read(path):
    return json.loads(path.read_bytes())


def inputs():
    """Fixed completed audits are inputs, not freshly rerun historical reviews."""
    if any(sha256(ROOT/n) != h for n, h in INPUTS.items()):
        raise ValueError('fixed audited parent bytes differ')
    parent, joint, r519, r520 = [read(ROOT/n) for n in INPUTS]
    if (not r519['passed'] or not r520['passed'] or not r519['result']['decision']['qualified_contact']
            or r520['parent_audit_sha256'] != INPUTS[R519]
            or not r520['all_profiles_qualified'] or r520['segments'] != 417460):
        raise ValueError('qualified complete audited parents required')
    old = r519['result']; point = old['correction']; points = r520['points']
    if [p['id'] for p in points] != ['coarse--1', 'coarse-+1', 'fine--1', 'fine-+1', 'correction']:
        raise ValueError('complete parent stationarity matrix required')
    if [p['parameters'] for p in points] != [p['spec']['parameters'] for p in old['points']+[point]]:
        raise ValueError('parent census and fold parameters differ')
    anchor_census = points[-1]
    matched = [model.match(anchor_census, p) for p in points]
    a_points = [dict(spec=q['spec'], qualified=m['qualified'], gaps=m['gaps'])
        for q, m in zip(old['points'], matched[:4], strict=True)]
    if not matched[-1]['qualified']:
        raise ValueError('complete unique anchor self-correspondence required')
    return dict(parent=parent, joint=joint, rows=point['rows'], cycle=point['cycle'],
        anchor=point['spec']['parameters'], vectors=point['vectors'], census=anchor_census,
        gaps=matched[-1]['gaps'], a_response=old['response'], a_gaps=model.gap_response(a_points, 'a', model.HA),
        a_center=parent['anchor']['a'], historical_matches=matched, a_points=a_points)


def expected():
    source = inputs(); parent = source['parent']
    # Direct fixed input identities replace recursive historical *execution*.
    # The numerical implementation remains byte-identical to its parent runs.
    p520 = read(census_run.PLAN)
    return dict(experiment_id='EXP-521', status='prospective-outcome-informed-local-mechanism-test',
        inputs=INPUTS, anchor=source['anchor'], specifications=model.stencil(source['anchor']),
        numerical=parent['numerical'], historical_targets=parent['historical_targets'], periodic=parent['periodic'],
        solvers=['DOP853', 'Radau'], phases=[.25, 1.25], controls=parent['controls'],
        attempts=1, stencil_points=4, maximum_corrections=1, folds_per_point=4,
        reused_a_response_center=source['a_center'], normalized_increments=dict(a=model.HA, c=model.HC),
        derivative_reuse='Two-center approximation; new full-vector prediction checks mandatory.',
        census=dict(objects=[5, 13], all_roots=16, time_width=str(census.TIME_WIDTH),
            match_phase=.01, match_state=.05, match_scales=model.MATCH_SCALES.tolist(),
            matching='Unique cyclic order, phase, full state, and curvature; every root retained.'),
        response_relative_tolerance=.05, prediction_relative_tolerance=.1, full_state_radius=1e-4,
        progress='All four contexts of source root 5 improve; root 13 also passes prediction and identity.',
        limits=dict(target_ivps=768, wall_seconds=7200, output_bytes=3*1024**3,
            initial_free_bytes=12*1024**3, minimum_free_bytes=8*1024**3,
            maximum_segments=600000, failure_reserve_bytes=1024**2),
        paid_review='not-requested-human-approval-policy', new_boundaries=0,
        symbolic_chains_verified=False, D_identified=False, exact_critical_locus_proved=False,
        source_paths=sorted(set(parent['source_paths']) | set(p520['source_paths']) | set(EXPLICIT)),
        ancillary_inputs={n: h for n, h in p520['inputs'].items() if n not in INPUTS})


def load():
    p = read(PLAN)
    if p != expected(): raise ValueError('complete frozen critical-response plan differs')
    for n, h in p['ancillary_inputs'].items():
        if sha256(ROOT/n) != h: raise ValueError('ancillary input differs')
    return p


def validate():
    from scripts import audit_exp521_critical_response  # noqa: F401
    p = load(); source = inputs()
    missing = prior.base.imported()-set(p['source_paths'])
    if missing: raise ValueError('deployed import closure incomplete: '+str(sorted(missing)))
    for spec in p['specifications']:
        candidates = prior.model.candidates(source['rows'], spec, prior.prior.transport.offset(spec['parameters']))
        for c in candidates:
            rhs, _, section = prior.coverage.fields(c)
            for u in [*c['u_box'], c['seed_u']-c['epsilon'], c['seed_u']+c['epsilon']]:
                q = prior.base.np.asarray(c['initial_state'])+u*prior.base.np.asarray(c['initial_tangent'])
                f = rhs(0., q)
                if (abs(section.value(q)) > 1e-10 or not section.accepts(q) or f[1] >= 0
                        or abs(f[1])/prior.base.np.linalg.norm(f) < p['numerical']['thresholds']['angle']):
                    raise ValueError('initial affine section orientation differs')
    return dict(valid=True, new_integrations=0, stencil_points=4, maximum_corrections=1,
                maximum_target_ivps=768, analytic_controls=census_run.controls())


def startup(p):
    root = Path(tempfile.mkdtemp(prefix='exp521-startup-')).resolve()
    names = set(p['source_paths']) | set(INPUTS) | set(p['ancillary_inputs'])
    for n in names:
        destination = root/n; destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/n, destination)
    code = (f'import sys;from pathlib import Path;root=Path({str(root)!r});'
        'sys.path[:0]=[str(root),str(root/"python")];'
        'from scripts.run_exp521_critical_response import validate;import json;print(json.dumps(validate()));'
        'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
        'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None))')
    child = subprocess.run([sys.executable, '-I', '-B', '-c', code], cwd=root,
        capture_output=True, text=True, check=True, timeout=120)
    hashes = {n: sha256(root/n) for n in sorted(names)}
    if hashes != {n: sha256(ROOT/n) for n in names} or list(root.rglob('*.pyc')):
        raise ValueError('sealed startup bytes changed')
    shutil.rmtree(root)
    return dict(passed=True, isolated=True, target_data_opened=False, sources=hashes, validation=json.loads(child.stdout))


def stationarity(stage, point, source, save, tick, certificates=None):
    """Census both full stored observations, regardless of point qualification."""
    spec = point['spec']; profiles = []; periods = []
    origin = rossler_equilibria(RosslerParameters(**spec['parameters']))[0].tolist()
    for config in point['cycle']['profiles']:
        method = config['method']; period = config['correction']['period_time']
        filename = f'{spec["id"]}--{method}--observation.npz'
        with prior.base.np.load(stage/filename, allow_pickle=False) as saved:
            raw = {n: saved[n] for n in saved.files}
        cert = None if certificates is None else certificates[method]
        result, proof = census.profile(raw, method, spec['parameters'], origin, period, certificate=cert, tick=tick)
        save('stationarity--'+method+'.json', dict(method=method, observation_sha256=sha256(stage/filename),
            result=result, certificates=proof))
        profiles.append(result); periods.append(period)
    product = dict(id=spec['id'], parameters=spec['parameters'], origin=origin, profiles=profiles,
                   comparison=census.point_comparison(profiles, periods))
    identity = model.match(source['census'], product)
    return dict(spec=spec, qualified=bool(point['qualified'] and product['comparison']['qualified'] and identity['qualified']),
                vectors=point['vectors'], gaps=identity['gaps'], census=product, identity=identity, fold_point=point)


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
    binding = dict(experiment_id='EXP-521', source_commit=commit, remote_ref=remote, started_utc=prior.base.utc(),
        plan_sha256=sha256(PLAN), inputs=INPUTS, sources={n: sha256(ROOT/n) for n in p['source_paths']},
        initial_free_bytes=free, runtime=dict(python=sys.version, numpy=prior.base.np.__version__, scipy=prior.base.scipy.__version__),
        paid_review=p['paid_review'])
    started = time.monotonic(); budget = prior.Budget(p['limits'], ROOT, started); segments = 0; progress = []
    def save(name, value, reserve=True): prior.coverage.write(output, output/name, value, p['limits'], reserve)
    def tick():
        nonlocal segments
        segments += 1
        if segments > p['limits']['maximum_segments']: raise ValueError('critical-response segment cap')
        if segments % 1000 == 0: budget()
    def measure(spec):
        progress.append(dict(id=spec['id'], status='started'))
        point = prior.measure(spec, output, p, source, budget, save)
        extended = stationarity(output/spec['id'], point, source,
            lambda name, value: save(spec['id']+'/'+name, value), tick)
        save(spec['id']+'/critical-point.json', extended)
        progress[-1]['status'] = 'completed'
        print(json.dumps(dict(completed_point=spec['id'], target_ivps=budget.calls, segments=segments)), flush=True)
        return extended
    def timeout(*_):
        budget.failure = 'EXP-521 wall deadline'
        raise prior.base.previous.cycles_run.BudgetStop(budget.failure)
    signal.signal(signal.SIGALRM, timeout); signal.alarm(p['limits']['wall_seconds'])
    try:
        save('binding.json', binding); save('startup.json', handshake); save('controls.json', census_run.controls())
        write_bounded_json(root, MARKER, binding, limit_bytes=directory_bytes(root)+1024**2,
                           minimum_free_bytes=p['limits']['minimum_free_bytes'])
        with prior.coverage.producers(prior.base, output, p['limits']):
            result = model.follow(source, measure)
        budget()
        if binding['sources'] != {n: sha256(ROOT/n) for n in p['source_paths']}: raise ValueError('source changed during target')
        save('summary.json', dict(experiment_id='EXP-521', status='completed', binding=binding, result=result,
            point_progress=progress, target_ivps=budget.calls, segments=segments, elapsed_seconds=time.monotonic()-started,
            completed_utc=prior.base.utc(), files=inventory(output), marker_sha256=sha256(MARKER), symbolic_chains_verified=False))
        print(json.dumps(dict(completed=True, summary_sha256=sha256(output/'summary.json'))), flush=True)
    except BaseException as exc:
        signal.alarm(0)
        save('failure.json', dict(error_type=type(exc).__name__, message=str(exc), utc=prior.base.utc(),
            target_ivps=budget.calls, segments=segments, point_progress=progress, files=inventory(output)), False)
        raise
    finally: signal.alarm(0)


def main():
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


if __name__ == '__main__': main()
