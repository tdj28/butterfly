#!/usr/bin/env python3
"""Bounded new collection and raw audit, reading private calibration in place."""
import argparse
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
from butterfly._paired_startup import inventory, sha256
from butterfly.bounded_json import directory_bytes, write_bounded_json
from scripts import run_exp523_refreshed_path as old
from scripts import verify_exp524_result as calibrated
from scripts import exp525_recovered_step as model
from scripts import audit_exp523_refreshed_path as full

ROOT = Path(__file__).resolve().parents[1]
PLAN = 'experiments/manifests/EXP-525-recovered-single-step.json'
REF = 'refs/heads/codex/exp525-prax-execution'
RAW_CALIBRATION = Path('/home/ubuntu/butterfly-research/exp524-partial-audit-da58089507c2/source/artifacts/EXP-524/audit-01/audit.json')
EXPLICIT = [PLAN, 'scripts/run_exp525_recovered_step.py', 'scripts/exp525_recovered_step.py',
    'scripts/deploy_exp525_prax.py', 'scripts/verify_exp524_result.py', 'tests/test_exp524_result.py',
    'tests/test_exp525_recovered_step.py', 'docs/experiments/EXP-525-recovered-single-step.md']


def expected():
    p = old.load()
    sources = set(old.read(ROOT/calibrated.audit.PLAN)['source_paths']) | set(EXPLICIT)
    return dict(experiment_id='EXP-525', status='prospective-outcome-informed-recovery-step',
        source_paths=sorted(sources), inputs=old.INPUTS, ancillary_inputs=p['ancillary_inputs'],
        external_input=dict(role='complete-private-EXP-524-audit', sha256=calibrated.SHA, bytes=18717419,
            source_commit=calibrated.SOURCE, distribution='Access-controlled; not uploaded or published by this experiment.'),
        recovery_cycle_sha256=calibrated.audit.CYCLE_SHA,
        numerical=p['numerical'], periodic=p['periodic'], historical_targets=p['historical_targets'],
        controls=p['controls'], solvers=p['solvers'], phases=p['phases'], census=p['census'],
        attempts=1, maximum_steps=1, maximum_new_points=2, reused_calibration_points=8,
        accepted_contact_radius=1e-7, full_state_radius=1e-4, prediction_relative_tolerance=.1,
        maximum_refinement_residual_ratio=.1, unchanged_scientific_controller='EXP-523 first step only',
        limits=dict(target_ivps=384, maximum_segments=200000, wall_seconds=21600,
            output_bytes=2*1024**3, initial_free_bytes=11*1024**3, minimum_free_bytes=8*1024**3,
            failure_reserve_bytes=1024**2),
        runtime=dict(python='3.13.13', numpy='2.5.1', scipy='1.18.0'),
        clock_policy='One six-hour ceiling for collection plus retained-raw audit, no automatic extension.',
        paid_review='not-requested-human-approval-policy', new_provider_creates=0, paid_api_calls=0,
        symbolic_chains_verified=False, D_identified=False, exact_critical_locus_proved=False)


def load():
    p = old.read(ROOT/PLAN)
    if p != expected(): raise ValueError('complete single-step plan differs')
    return p


def inputs(path):
    info = calibrated.verify(path)
    if not info['calibration_qualified']: raise ValueError('calibration does not qualify')
    receipt = old.read(path)
    if Path(path).stat().st_size != 18717419: raise ValueError('private audit byte count differs')
    return old.inputs(), receipt['result']


def validate(path=None):
    p = load()
    for n in p['source_paths']: calibrated.audit.preservation.safe_file(ROOT, n)
    missing = old.prior.base.imported()-set(p['source_paths'])
    if missing: raise ValueError('complete source closure required: '+str(sorted(missing)))
    result = dict(valid=True, new_integrations=0, maximum_new_points=2,
                  target_outcomes_opened=False, historical_calibration_checked=path is not None)
    if path is not None:
        source, calibration = inputs(path)
        if calibration['initial_anchor'] != source['anchor']: raise ValueError('historical anchor differs')
        # Construct candidates through the authentic production path, without
        # integrating. The proposed first point is not printed to public logs.
        proposed = model.prior.proposal(source, calibration['response'], 0)
        if proposed is not None:
            candidates = old.prior.model.candidates(source['rows'], proposed['spec'],
                old.prior.prior.transport.offset(proposed['spec']['parameters']))
            for c in candidates:
                rhs, _, section = old.prior.coverage.fields(c)
                for u in [*c['u_box'], c['seed_u']-c['epsilon'], c['seed_u']+c['epsilon']]:
                    q = old.prior.base.np.asarray(c['initial_state'])+u*old.prior.base.np.asarray(c['initial_tangent'])
                    f = rhs(0., q)
                    if (abs(section.value(q)) > 1e-10 or not section.accepts(q) or f[1] >= 0
                            or abs(f[1])/old.prior.base.np.linalg.norm(f) < p['numerical']['thresholds']['angle']):
                        raise ValueError('initial candidate section orientation differs')
        result['calibration_qualified'] = True
    return result


def preflight(commit):
    def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    if (git('rev-parse','HEAD') != commit or git('status','--porcelain')
            or git('ls-remote','origin',REF).split() != [commit,REF]):
        raise ValueError('clean live-pushed exact successor source required')
    p = load(); actual = calibrated.audit.runtime_check()
    if actual != p['runtime']: raise ValueError('exact managed runtime differs')
    if shutil.disk_usage(ROOT).free < p['limits']['initial_free_bytes']: raise ValueError('collection storage reserve')
    with calibrated.audit.forbid_integrations(): validation = validate(RAW_CALIBRATION)
    return dict(passed=True, validation=validation, source_commit=commit, runtime=actual,
        plan_sha256=sha256(ROOT/PLAN), historical_calibration_sha256=calibrated.SHA,
        source_hashes={n:sha256(ROOT/n) for n in p['source_paths']})


def raw_audit(output, summary, source, calibration, p, binding):
    names = {'binding.json', 'controls.json'}; calls = segments = 0
    def tick():
        nonlocal segments
        segments += 1
        if segments > p['limits']['maximum_segments']: raise ValueError('single-step audit segment cap')
    def measure(spec, current):
        nonlocal calls
        stage = output/spec['id']
        candidates = old.prior.model.candidates(current['rows'],spec,old.prior.prior.transport.offset(spec['parameters']))
        if old.read(stage/'inputs.json') != dict(spec=spec,candidates=candidates): raise ValueError('candidate inputs differ')
        rows, paths, count = full.folds.check_rows(stage,candidates,p,binding,summary['completed_utc']); calls += count
        cycle = old.read(stage/'cycle.json')
        cycle_paths, count = full.folds.raw.old.check_cycle(stage,cycle,spec,current['cycle']['profiles'][0]['correction'],p['periodic']); calls += count
        point = old.prior.summarize(spec,rows,cycle,p,current)
        full.folds.transport_audit.scalar_decision(current['rows'],rows,point['fold_identity'])
        if point['contact'] is not None:
            scalar = full.folds.raw.old.scalar_contact([r['assessment']['comparison'] for r in rows],cycle)
            if not full.folds.raw.old.periodic_audit.numeric_equal(scalar,point['contact']): raise ValueError('scalar contact differs')
        if not old.prior.coverage.public.equal(point,old.read(stage/'point.json')): raise ValueError('raw point replay differs')
        certificates = {m:old.read(stage/('stationarity--'+m+'.json'))['certificates'] for m in p['solvers']}
        def check_product(name,value):
            if not full.roots.same(value,old.read(stage/name)): raise ValueError('polynomial census differs')
        extended = old.parent.stationarity(stage,point,current,check_product,tick,certificates)
        if not full.roots.same(extended,old.read(stage/'critical-point.json')): raise ValueError('critical identity differs')
        names.update(spec['id']+'/'+n for n in paths|cycle_paths|{'inputs.json','cycle.json','point.json',
            'critical-point.json','stationarity--DOP853.json','stationarity--Radau.json'})
        return extended
    with calibrated.audit.forbid_integrations():
        result = model.follow(source,calibration['response'],measure)
        model.scalar_check(result,source,calibration)
    if (not old.prior.coverage.public.equal(result,summary['result']) or names != set(summary['files'])
            or calls != summary['target_ivps'] or segments != summary['segments']):
        raise ValueError('complete fresh-run replay/accounting differs')
    return dict(passed=True,result=result,target_ivps=calls,segments=segments,new_audit_integrations=0)


def execute(commit):
    handshake = preflight(commit); p = load(); source, calibration = inputs(RAW_CALIBRATION)
    root = ROOT/'artifacts/EXP-525'; output = root/'target-01'; marker = root/'target-once.json'
    if output.exists() or marker.exists() or output.is_symlink() or marker.is_symlink():
        raise ValueError('fresh successor attempt required')
    output.mkdir(parents=True); started = time.monotonic(); progress = []; segments = 0
    binding = dict(experiment_id='EXP-525', source_commit=commit, started_utc=old.prior.base.utc(),
        plan_sha256=sha256(ROOT/PLAN), sources=handshake['source_hashes'], runtime=handshake['runtime'],
        inputs=old.INPUTS, historical_calibration_sha256=calibrated.SHA, handshake=handshake,
        paid_review=p['paid_review'], initial_free_bytes=shutil.disk_usage(ROOT).free)
    budget = old.prior.Budget(p['limits'], ROOT, started)
    def save(name,value,reserve=True): old.prior.coverage.write(output,output/name,value,p['limits'],reserve)
    def tick():
        nonlocal segments
        segments += 1
        if segments > p['limits']['maximum_segments']: raise ValueError('fresh-run census cap')
        if segments % 1000 == 0: budget()
    def measure(spec,current):
        progress.append(dict(id=spec['id'],status='started'))
        point = old.prior.measure(spec,output,p,current,budget,save)
        extended = old.parent.stationarity(output/spec['id'],point,current,
            lambda n,v:save(spec['id']+'/'+n,v),tick)
        save(spec['id']+'/critical-point.json',extended); progress[-1]['status']='completed'
        print(json.dumps(dict(completed_point=spec['id'],new_target_ivps=budget.calls,segments=segments)),flush=True)
        return extended
    def timeout(*_): raise TimeoutError('EXP-525 six-hour combined collection/audit deadline')
    previous = signal.signal(signal.SIGALRM,timeout)
    try:
        save('binding.json',binding); save('controls.json',old.parent.census_run.controls())
        write_bounded_json(root,marker,binding,limit_bytes=directory_bytes(root)+1024**2,minimum_free_bytes=p['limits']['minimum_free_bytes'])
        signal.alarm(21600)
        calibrated.audit.protect_historical_tree()
        print(json.dumps(dict(started=True,utc=binding['started_utc'],hard_wall_seconds=21600)),flush=True)
        with old.prior.coverage.producers(old.prior.base,output,p['limits']):
            result = model.follow(source,calibration['response'],measure)
        budget()
        summary = dict(experiment_id='EXP-525',status='collection-completed',binding=binding,result=result,
            completed_utc=old.prior.base.utc(),elapsed_seconds=time.monotonic()-started,
            target_ivps=budget.calls,segments=segments,point_progress=progress,files=inventory(output))
        save('summary.json',summary)
        audited = raw_audit(output,summary,source,calibration,p,binding)
        if (inventory(output,omit=('summary.json',)) != summary['files']
                or old.read(marker) != binding or sha256(RAW_CALIBRATION) != calibrated.SHA
                or binding['sources'] != {n:sha256(ROOT/n) for n in p['source_paths']}
                or time.monotonic()-started > 21600):
            raise ValueError('final source/input/raw/deadline binding differs')
        save('audit.json',dict(experiment_id='EXP-525',source_commit=commit,plan_sha256=sha256(ROOT/PLAN),
            summary_sha256=sha256(output/'summary.json'),historical_calibration_sha256=calibrated.SHA,
            completed_utc=old.prior.base.utc(),elapsed_seconds=time.monotonic()-started,
            reused_ivps_not_new=864,symbolic_chains_verified=False,D_identified=False,
            exact_critical_locus_proved=False,**audited))
        print(json.dumps(dict(audit_completed=True,receipt_sha256=sha256(output/'audit.json'))),flush=True)
    except BaseException as exc:
        signal.alarm(0)
        save('failure.json',dict(experiment_id='EXP-525',utc=old.prior.base.utc(),error_type=type(exc).__name__,
            message=str(exc),target_ivp_calls_started=budget.calls,segments=segments,point_progress=progress,
            files=inventory(output)),False)
        raise
    finally:
        signal.alarm(0); signal.signal(signal.SIGALRM,previous)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group()
    for n in ('prepare','preflight','execute'): modes.add_argument('--'+n,action='store_true')
    parser.add_argument('--commit'); parser.add_argument('--calibration',type=Path)
    args=parser.parse_args()
    if args.prepare:
        write_bounded_json((ROOT/PLAN).parent,ROOT/PLAN,expected(),limit_bytes=64*1024**2)
    elif args.preflight or args.execute:
        if not args.commit: parser.error('exact source commit required')
        if args.execute: execute(args.commit)
        else: print(json.dumps(preflight(args.commit)))
    else: print(json.dumps(validate(args.calibration)))


if __name__=='__main__': main()
