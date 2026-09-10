#!/usr/bin/env python3
"""Fresh fixed-c fold/cycle response with a single gated correction."""
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
from scripts import run_exp518_fold_transport as prior
from scripts import verify_exp518_public_transport as public
from scripts import exp519_fold_response as model

ROOT = prior.ROOT
PLAN = ROOT/'experiments/manifests/EXP-519-fixed-c-fold-response.json'
RECEIPT = 'docs/experiments/receipts/EXP-518-recovered-fold-transport-result.json'
INPUTS = dict(prior.INPUTS, **{
    RECEIPT: 'f8a0b33cd13ff88d924928bc5f59a811468ae5a627ca007a0541702d194c8e01',
    'experiments/manifests/EXP-518-recovered-fold-transport.json': 'e217455377cbd0b3a8de00ef0455beb2f27c4c92b72dbdc8b4c519591929e058'})
EXPLICIT = ['scripts/run_exp519_fold_response.py', 'scripts/exp519_fold_response.py',
    'scripts/audit_exp519_fold_response.py', 'scripts/verify_exp518_public_transport.py',
    'tests/test_exp519_fold_response.py', 'docs/experiments/EXP-519-fixed-c-fold-response.md',
    'experiments/manifests/EXP-519-fixed-c-fold-response.json']
base, coverage = prior.base, prior.coverage
_CACHE = None


def inputs():
    """Replay authenticated compact ancestry once per unchanged byte closure."""
    global _CACHE
    if any(sha256(ROOT/n) != h for n, h in INPUTS.items()):
        raise ValueError('fixed EXP-519 input differs')
    parent = json.loads(prior.PLAN.read_bytes())  # Hash pinned above, not a floating authority.
    names = set(parent['source_paths']) | set(INPUTS) | {'scripts/verify_exp518_public_transport.py'}
    fingerprint = {n: sha256(ROOT/n) for n in sorted(names)}
    if _CACHE is None or _CACHE[0] != fingerprint:
        public.verify(ROOT/RECEIPT, INPUTS[RECEIPT])
        saved = json.loads((ROOT/RECEIPT).read_bytes())
        if not saved['result']['transport_completed']:
            raise ValueError('complete recovered transport anchor required')
        rows = saved['result']['rows'][-1]['rows']
        old = prior.transport.inputs()
        anchor = prior.model.matrix(rows)
        if anchor != old['spec']['parameters'] or old['cycle']['status'] != 'qualified':
            raise ValueError('exact qualified endpoint cycle required')
        # Relabel only the derived comparison keys, not any historical artifact.
        comparisons = [dict(r['assessment']['comparison'],
            family_id=f'exp519-history-{r["candidate"]["history"]}-direction-{r["candidate"]["direction"]}') for r in rows]
        joint = base.load()
        contact = base.previous.measure(comparisons, old['cycle'], joint)
        result = dict(parent=parent, joint=joint, rows=rows, anchor=anchor, cycle=old['cycle'],
                      anchor_vectors=model.vectors(contact), anchor_contact=contact)
        if fingerprint != {n: sha256(ROOT/n) for n in sorted(names)}:
            raise ValueError('input closure changed during authentication')
        _CACHE = (fingerprint, result)
    return deepcopy(_CACHE[1])


def expected():
    source = inputs(); parent = source['parent']
    return dict(experiment_id='EXP-519', status='prospective-outcome-informed-fixed-c-response',
        inputs=INPUTS, anchor=source['anchor'], specifications=model.stencil(source['anchor']),
        numerical=parent['numerical'], historical_targets=parent['historical_targets'],
        periodic=source['joint']['periodic'], solvers=['DOP853', 'Radau'], phases=[.25, 1.25],
        controls=parent['controls'], new_control_ivps=0, attempts=1, stencil_points=4,
        maximum_corrections=1, folds_per_point=4, new_boundaries=0, normalized_a_increment=model.H,
        response_relative_tolerance=.05, minimum_absolute_x_response=1e-8,
        full_state_radius=1e-4, prediction_relative_tolerance=.1,
        cycle_indices=[3, 4], coordinate_scales=[15., 15., .01],
        limits=dict(target_ivps=768, wall_seconds=7200, output_bytes=3*1024**3,
            initial_free_bytes=12*1024**3, minimum_free_bytes=8*1024**3, failure_reserve_bytes=1024**2),
        paid_review='not-requested-human-approval-policy', symbolic_chains_verified=False,
        source_paths=sorted(set(parent['source_paths']) | set(EXPLICIT)))


def load():
    saved = json.loads(PLAN.read_bytes())
    if saved != expected():
        raise ValueError('frozen fixed-c response plan differs')
    return saved


def validate():
    p = load(); source = inputs()
    if not base.imported() <= set(p['source_paths']):
        raise ValueError('deployed import closure incomplete: '+str(base.imported()-set(p['source_paths'])))
    for spec in p['specifications']:
        candidates = model.candidates(source['rows'], spec, prior.transport.offset(spec['parameters']))
        for c in candidates:
            rhs, _, section = coverage.fields(c)
            for u in [*c['u_box'], c['seed_u']-c['epsilon'], c['seed_u']+c['epsilon']]:
                q = base.np.asarray(c['initial_state'])+u*base.np.asarray(c['initial_tangent'])
                f = rhs(0., q)
                if abs(section.value(q)) > 1e-10 or not section.accepts(q) or f[1] >= 0 or abs(f[1])/base.np.linalg.norm(f) < p['numerical']['thresholds']['angle']:
                    raise ValueError('initial affine curve section/orientation differs')
    return dict(valid=True, new_integrations=0, stencil_points=4, maximum_corrections=1, maximum_target_ivps=768)


def startup(p):
    target = Path(tempfile.mkdtemp(prefix='exp519-startup-')).resolve()
    names = set(p['source_paths']) | set(INPUTS)
    for name in names:
        dest = target/name; dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/name, dest)
    code = (f'import sys;from pathlib import Path;root=Path({str(target)!r});'
        f'sys.path[:0]={[str(target), str(target/"python")]!r};'
        'from scripts.run_exp519_fold_response import main;main();'
        'assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() '
        'if n.startswith(("scripts.","butterfly")) and getattr(m,"__file__",None));'
        'assert not list(root.rglob("*.pyc"))')
    child = subprocess.run([sys.executable, '-I', '-B', '-c', code], cwd=target,
                           capture_output=True, text=True, check=True, timeout=240)
    hashes = {n: sha256(target/n) for n in sorted(names)}
    if hashes != {n: sha256(ROOT/n) for n in sorted(names)}:
        raise ValueError('isolated source changed')
    # This exact fresh directory contains only hash-identical public source/input
    # copies, never raw targets. Keep failed rehearsals; dispose of successful
    # duplicate copies after recording their complete hashes in the receipt.
    shutil.rmtree(target)
    return dict(passed=True, isolated=True, new_integrations=0, sources=hashes,
                stdout=child.stdout, stderr=child.stderr)


def summarize(spec, rows, cycle, p, source):
    check = prior.model.decision(source['rows'], rows)
    original = base.response.correspondence(cycle, source['joint']['reference_cycle'])
    adjacent = base.response.correspondence(cycle, source['cycle'])
    good = check['transport_qualified'] and cycle['status'] == 'qualified' and original['passed'] and adjacent['passed']
    contact = None
    if good:
        comparisons = [r['assessment']['comparison'] for r in rows]
        contact = base.previous.measure(comparisons, cycle, source['joint'])
    return dict(spec=spec, rows=rows, cycle=cycle, fold_identity=check,
                original_correspondence=original, anchor_correspondence=adjacent,
                qualified=bool(good), contact=contact, vectors=None if contact is None else model.vectors(contact))


class Budget:
    """A resource interruption stays fatal even if a numerical producer catches it."""
    def __init__(self, limits, root, started, clock=time.monotonic, free=None):
        self.limits, self.root, self.started, self.clock = limits, root, started, clock
        self.free = free if free is not None else lambda: shutil.disk_usage(root).free
        self.calls = 0
        self.failure = None

    def __call__(self, integrating=False):
        if self.failure is None:
            if self.clock()-self.started > self.limits['wall_seconds']:
                self.failure = 'EXP-519 wall deadline'
            elif self.free() < self.limits['minimum_free_bytes']:
                self.failure = 'EXP-519 free-space cap'
            elif integrating and self.calls >= self.limits['target_ivps']:
                self.failure = 'EXP-519 IVP cap'
        if self.failure is not None:
            raise base.previous.cycles_run.BudgetStop(self.failure)
        if integrating:
            self.calls += 1


def measure(spec, output, p, source, budget, save):
    stage = output/spec['id']; stage.mkdir()
    candidates = model.candidates(source['rows'], spec, prior.transport.offset(spec['parameters']))
    save(spec['id']+'/inputs.json', dict(spec=spec, candidates=candidates))
    profiles = []
    for method in p['solvers']:
        profile = base.previous.cycles_run.run_profile(spec, method, source['cycle']['profiles'][0]['correction'], p['periodic'], stage, budget)
        budget()
        profiles.append(profile)
    pair = base.previous.cycles_run.compare_profiles(profiles, p['periodic'])
    counts = pair['passed'] and all(w['counts'] == dict(historical=6, barrio=8) for r in profiles for w in r['metric']['windows'])
    cycle = dict(spec=spec, profiles=profiles, pair=pair, status='qualified' if counts else 'unqualified')
    if pair['passed'] and not counts:
        cycle['count_failure'] = True
    save(spec['id']+'/cycle.json', cycle)
    def probe(c):
        folder = stage/c['id']; folder.mkdir(); profiles = []
        rhs, jac, section = coverage.fields(c)
        for method in p['solvers']:
            label = spec['id']+'/'+c['id']+'/midpoint--'+method
            save(label+'-started.json', dict(candidate=c, method=method, started_utc=base.utc()))
            profile = coverage.dense.capture(c, c['seed_u'], method, p['numerical'], rhs, jac, section,
                lambda name, raw: base.retain_npz(output/(label+'--'+name+'.npz'), raw), budget)
            budget()
            save(label+'.json', profile); profiles.append(profile)
        seeded, pair = prior.midpoint_seed(c, profiles, p)
        save(spec['id']+'/'+c['id']+'/seed.json', dict(candidate=seeded, pair=pair))
        return seeded, profiles, pair
    def shoot(c):
        profiles = []
        for method in p['solvers']:
            with prior.prior.retain_failed_censuses(stage/c['id'], c, method):
                profiles.append(base.fold_profile(stage/c['id'], c, method, p['numerical'], budget))
            budget()
        return profiles
    rows = prior.prior.model.follow(candidates, probe, shoot, lambda c, r: prior.assess(c, r, p))
    for row in rows:
        save(spec['id']+'/'+row['candidate']['id']+'/result.json', row)
    result = summarize(spec, rows, cycle, p, source)
    save(spec['id']+'/point.json', result)
    return result


def execute(output, source_commit, remote):
    p = load(); source = inputs()
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
    if git('rev-parse', 'HEAD') != source_commit or git('status', '--porcelain') or git('ls-remote', 'origin', remote).split() != [source_commit, remote]:
        raise ValueError('clean exact live-pushed source required')
    validate(); controls = prior.prior.controls(p)
    root = ROOT/'artifacts/EXP-519'; marker = root/'target-once.json'; output = output.resolve()
    free = shutil.disk_usage(ROOT).free
    if root not in output.parents or output.exists() or marker.exists() or free < p['limits']['initial_free_bytes']:
        raise ValueError('fresh unconsumed output and disk reserve required')
    output.mkdir(parents=True)
    binding = dict(source_commit=source_commit, remote_ref=remote, started_utc=base.utc(), plan_sha256=sha256(PLAN),
        inputs=INPUTS, sources={n: sha256(ROOT/n) for n in p['source_paths']}, initial_free_bytes=free,
        runtime=dict(python=sys.version, numpy=base.np.__version__, scipy=base.scipy.__version__), paid_review=p['paid_review'])
    started = time.monotonic(); progress = []
    budget = Budget(p['limits'], ROOT, started)
    def save(name, value, reserve=True):
        coverage.write(output, output/name, value, p['limits'], reserve)
    def point(spec):
        progress.append(dict(id=spec['id'], status='started'))
        result = measure(spec, output, p, source, budget, save)
        progress[-1]['status'] = 'completed'
        print(json.dumps(dict(completed_point=spec['id'], target_ivps=budget.calls)), flush=True)
        return result
    def timeout(*_):
        budget.failure = 'EXP-519 wall deadline'
        raise base.previous.cycles_run.BudgetStop('EXP-519 wall deadline')
    signal.signal(signal.SIGALRM, timeout); signal.alarm(p['limits']['wall_seconds'])
    try:
        save('binding.json', binding); save('startup.json', startup(p)); save('control-replay.json', controls)
        write_bounded_json(root, marker, binding, limit_bytes=directory_bytes(root)+1024**2, minimum_free_bytes=p['limits']['minimum_free_bytes'])
        with coverage.producers(base, output, p['limits']):
            result = model.follow(source['anchor'], source['anchor_vectors'], point)
        budget()
        save('summary.json', dict(experiment_id='EXP-519', status='completed', binding=binding, result=result,
            point_progress=progress, target_ivps=budget.calls, elapsed_seconds=time.monotonic()-started,
            completed_utc=base.utc(), files=inventory(output), marker_sha256=sha256(marker), symbolic_chains_verified=False))
        print(json.dumps(dict(completed=True, target_ivps=budget.calls, summary_sha256=sha256(output/'summary.json'))), flush=True)
    except BaseException as exc:
        signal.alarm(0)
        save('failure.json', dict(error_type=type(exc).__name__, message=str(exc), utc=base.utc(), target_ivps=budget.calls,
            point_progress=progress, files=inventory(output)), False)
        raise
    finally:
        signal.alarm(0)


def main():
    from scripts import audit_exp519_fold_response  # noqa: F401
    parser = argparse.ArgumentParser(description=__doc__); modes = parser.add_mutually_exclusive_group()
    for name in ('prepare', 'startup', 'execute'):
        modes.add_argument('--'+name, action='store_true')
    parser.add_argument('--output-dir', type=Path); parser.add_argument('--source-commit'); parser.add_argument('--remote-ref')
    a = parser.parse_args()
    if a.prepare:
        write_bounded_json(PLAN.parent, PLAN, expected(), limit_bytes=directory_bytes(PLAN.parent)+1024**2)
    elif a.execute:
        if not all((a.output_dir, a.source_commit, a.remote_ref)):
            parser.error('output, source, and remote required')
        execute(a.output_dir, a.source_commit, a.remote_ref)
    else:
        print(json.dumps(startup(load()) if a.startup else validate()))


if __name__ == '__main__':
    main()
