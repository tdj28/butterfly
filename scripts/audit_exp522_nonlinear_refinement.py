#!/usr/bin/env python3
"""Full raw replay and separate scalar checks for the one new correction."""
import argparse
import json
import math
from pathlib import Path
import time
from butterfly._paired_startup import inventory, sha256
from butterfly.bounded_json import directory_bytes, write_bounded_json
from scripts import run_exp522_nonlinear_refinement as run
from scripts import audit_exp519_fold_response as folds
from scripts import audit_exp520_periodic_census as roots


def scalar_check(result, source):
    equal = folds.raw.old.periodic_audit.numeric_equal
    proposed = result['proposal']
    if proposed is None: return  # Deterministic controller replay enforces absence.
    f, j = source['vectors'], source['a_response']['variants']
    g, gj = source['gaps'], source['a_gaps']['variants']
    if not source['a_response']['qualified'] or not source['a_gaps']['qualified']:
        raise ValueError('unqualified derivative authorized step')
    mean_f = math.fsum(r['residual'][0] for r in f)/16
    mean_j = math.fsum(r['fine'][0] for r in j)/16
    anchor = source['anchor']; center = source['a_center']
    a = max(max(anchor['a']-1e-5, center-1e-5),
        min(min(anchor['a']+1e-5, center+1e-5), anchor['a']-1e-5*mean_f/mean_j))
    da = (a-anchor['a'])/1e-5
    pf = [dict(key=q['key'], residual=[x+y*da for x, y in zip(q['residual'], d['fine'], strict=True)])
        for q, d in zip(f, j, strict=True)]
    pg = [dict(key=q['key'], residual=q['residual']+d['fine']*da) for q, d in zip(g, gj, strict=True)]
    expected = dict(spec=dict(id='nonlinear-refinement', parameters=dict(anchor, a=a)),
        mean_signed_x=mean_f, mean_normalized_slope=mean_j, normalized_a_step=da,
        response_center=source['a_derivative_center'], prediction_center=anchor,
        progress_reference=source['progress_anchor'], predicted_vectors=pf, predicted_gaps=pg)
    if not equal(expected, proposed): raise ValueError('separate scalar parameter/prediction differs')
    point = result['correction']
    if point is None or point['spec'] != proposed['spec']: raise ValueError('prescribed point missing or changed')
    if not point['qualified']: return
    frows, grows, reduction, progress = [], [], [], []
    norm = lambda v: math.sqrt(math.fsum(x*x for x in v))
    for q, b, p in zip(point['vectors'], f, pf, strict=True):
        distance = max(map(abs, q['residual'])); old = max(map(abs, b['residual']))
        error = norm([x-y for x, y in zip(q['residual'], p['residual'], strict=True)])
        motion = max(norm([x-y for x, y in zip(p['residual'], b['residual'], strict=True)]), 1e-12)
        frows.append(dict(key=q['key'], distance=distance, prediction_error=error/motion,
            qualified=distance <= 1e-4 and error/motion <= .1))
        reduction.append(dict(key=q['key'], before=old, actual=distance, qualified=distance <= .1*old))
    for q, b, p, original in zip(point['gaps'], g, pg, source['progress_gaps'], strict=True):
        actual, old, pred = q['residual'], b['residual'], p['residual']
        error = abs(actual-pred)/max(abs(pred-old), 1e-8)
        grows.append(dict(key=q['key'], before=old, actual=actual, predicted=pred,
            prediction_error=error, qualified=error <= .1, improved=abs(actual) < abs(old)))
        progress.append(dict(key=q['key'], before=original['residual'], actual=actual,
            improved=abs(actual) < abs(original['residual'])))
    localgood = all(r['qualified'] for r in frows+grows) and all(r['improved'] for r in grows[::2])
    local = dict(qualified=localgood, reason=None if localgood else 'contact-prediction-or-progress-failed', folds=frows, gaps=grows)
    good = all(r['qualified'] for r in frows+grows+reduction) and all(r['improved'] for r in progress[::2])
    decision = dict(qualified=good, reason=None if good else 'prediction-refinement-or-net-progress-failed',
        local=local, reduction=reduction, net_progress=progress)
    if not equal(decision, result['decision']): raise ValueError('separate scalar decision differs')


def audit(output, expected_sha):
    output = Path(output); p = run.load(); source = run.inputs()
    if sha256(output/'summary.json') != expected_sha: raise ValueError('summary byte identity differs')
    saved, binding = run.read(output/'summary.json'), run.read(output/'binding.json')
    run.prior.public.folds.finite_packet(saved)
    if (saved['experiment_id'] != 'EXP-522' or saved['status'] != 'completed' or saved['binding'] != binding
            or binding['sources'] != {n: sha256(run.ROOT/n) for n in p['source_paths']}
            or binding['inputs'] != run.INPUTS or binding['plan_sha256'] != sha256(run.PLAN)
            or binding['paid_review'] != p['paid_review'] or saved['symbolic_chains_verified'] is not False
            or set(binding['runtime']) != {'python', 'numpy', 'scipy'} or not all(binding['runtime'].values())
            or binding['initial_free_bytes'] < p['limits']['initial_free_bytes']
            or saved['files'] != inventory(output, omit=('summary.json',))
            or not binding['started_utc'] <= saved['completed_utc']
            or not 0 <= saved['elapsed_seconds'] <= p['limits']['wall_seconds']
            or sha256(run.MARKER) != saved['marker_sha256'] or run.read(run.MARKER) != binding):
        raise ValueError('source, input, inventory, clock, marker or resource binding differs')
    handshake = run.read(output/'startup.json')
    if (not handshake['passed'] or not handshake['isolated'] or handshake['target_data_opened'] is not False
            or handshake['sources'] != {n: sha256(run.ROOT/n) for n in set(p['source_paths']) | set(run.INPUTS) | set(p['ancillary_inputs'])}
            or handshake['validation'] != run.validate() or run.read(output/'controls.json') != run.parent.census_run.controls()):
        raise ValueError('sealed startup or analytic controls differ')
    names = {'binding.json', 'startup.json', 'controls.json'}; calls = segments = 0; progress = []
    started = time.monotonic()
    def tick():
        nonlocal segments
        segments += 1
        if segments > p['limits']['maximum_segments'] or time.monotonic()-started > p['limits']['wall_seconds']:
            raise ValueError('bounded raw audit limit')
    def measure(spec):
        nonlocal calls
        stage = output/spec['id']
        candidates = run.prior.model.candidates(source['rows'], spec, run.prior.prior.transport.offset(spec['parameters']))
        if run.read(stage/'inputs.json') != dict(spec=spec, candidates=candidates): raise ValueError('candidate inputs differ')
        rows, paths, count = folds.check_rows(stage, candidates, p, binding, saved['completed_utc']); calls += count
        cycle = run.read(stage/'cycle.json')
        cycle_paths, count = folds.raw.old.check_cycle(stage, cycle, spec, source['cycle']['profiles'][0]['correction'], p['periodic'])
        calls += count
        point = run.prior.summarize(spec, rows, cycle, p, source)
        folds.transport_audit.scalar_decision(source['rows'], rows, point['fold_identity'])
        if point['contact'] is not None:
            scalar = folds.raw.old.scalar_contact([r['assessment']['comparison'] for r in rows], cycle)
            if not folds.raw.old.periodic_audit.numeric_equal(scalar, point['contact']): raise ValueError('scalar contact differs')
        if not run.prior.coverage.public.equal(point, run.read(stage/'point.json')): raise ValueError('raw point replay differs')
        certificates = {m: run.read(stage/('stationarity--'+m+'.json'))['certificates'] for m in p['solvers']}
        def check_product(name, value):
            if not roots.same(value, run.read(stage/name)): raise ValueError('separate exact polynomial census replay differs')
        extended = run.parent.stationarity(stage, point, source, check_product, tick, certificates)
        if not roots.same(extended, run.read(stage/'critical-point.json')): raise ValueError('root identity or critical-point replay differs')
        names.update(spec['id']+'/'+n for n in paths | cycle_paths | {'inputs.json', 'cycle.json', 'point.json',
            'critical-point.json', 'stationarity--DOP853.json', 'stationarity--Radau.json'})
        progress.append(dict(id=spec['id'], status='completed'))
        print(json.dumps(dict(audited_point=spec['id'], target_ivps=calls, segments=segments)), flush=True)
        return extended
    result = run.model.follow(source, measure); scalar_check(result, source)
    if (not run.prior.coverage.public.equal(result, saved['result']) or names != set(saved['files'])
            or calls != saved['target_ivps'] or calls > p['limits']['target_ivps'] or segments != saved['segments']
            or progress != saved['point_progress'] or directory_bytes(output) > p['limits']['output_bytes']
            or binding['sources'] != {n: sha256(run.ROOT/n) for n in p['source_paths']}):
        raise ValueError('complete raw accounting, outcome replay or final source differs')
    return dict(experiment_id='EXP-522', passed=True, source_commit=binding['source_commit'],
        plan_sha256=sha256(run.PLAN), summary_sha256=expected_sha, inputs=run.INPUTS, runtime=binding['runtime'],
        result=result, target_ivps=calls, segments=segments, output_bytes=directory_bytes(output), new_integrations=0,
        prediction_anchor=source['anchor'], progress_anchor=source['progress_anchor'],
        symbolic_chains_verified=False, D_identified=False, exact_critical_locus_proved=False,
        parent_predictor_qualified=False, paid_review=p['paid_review'],
        scope='Full retained raw replay, separate polynomial expansion and scalar checks; shared geometry/controller. New nonlinear refinement, never replacement of failed EXP-521. No exact-flow or critical-locus proof, homoclinic result, or Jones arrow.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True); parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True); args = parser.parse_args()
    result = audit(args.run, args.expected_sha256)
    write_bounded_json(args.output.parent, args.output, result, limit_bytes=directory_bytes(args.output.parent)+32*1024**2)
    print(json.dumps(dict(passed=True, receipt_sha256=sha256(args.output))))
