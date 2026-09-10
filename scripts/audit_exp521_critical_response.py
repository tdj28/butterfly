#!/usr/bin/env python3
"""Full new raw replay, exact polynomial proofs, and scalar predictor checks."""
import argparse
import json
import math
from pathlib import Path
import time

from butterfly._paired_startup import inventory, sha256
from butterfly.bounded_json import directory_bytes, write_bounded_json
from scripts import run_exp521_critical_response as run
from scripts import audit_exp519_fold_response as folds
from scripts import audit_exp520_periodic_census as roots


def scalar_check(result, source):
    """Separate scalar arithmetic: no NumPy differentiation or linear solve."""
    equal = folds.raw.old.periodic_audit.numeric_equal
    points = result['points']; response = result['response']
    if [p['spec'] for p in points] != run.model.stencil(source['anchor']):
        raise ValueError('scalar stencil identity')
    if not all(p['qualified'] for p in points):
        if response['qualified'] or result['proposal'] is not None or result['correction'] is not None:
            raise ValueError('failed stencil authorized a step')
        return
    frows, grows = [], []
    for name, keys, dimensions, destination in [('vectors', run.model.fold.KEYS, 6, frows), ('gaps', run.model.GKEYS, 1, grows)]:
        for i, key in enumerate(keys):
            slopes = []
            for lo, hi in ((0, 1), (2, 3)):
                x, y = [points[j][name][i] for j in (lo, hi)]
                if x['key'] != key or y['key'] != key: raise ValueError('scalar variant identity')
                a = x['residual'] if dimensions == 6 else [x['residual']]
                b = y['residual'] if dimensions == 6 else [y['residual']]
                width = points[hi]['spec']['parameters']['c']-points[lo]['spec']['parameters']['c']
                slopes.append([(v-u)*.005/width for u, v in zip(a, b, strict=True)])
            coarse, fine = slopes
            norm = lambda v: math.sqrt(math.fsum(x*x for x in v))
            error = norm([a-b for a, b in zip(coarse, fine, strict=True)])/max(norm(fine), 1e-8)
            xe = abs(coarse[0]-fine[0])/max(abs(fine[0]), 1e-8)
            if dimensions == 6:
                destination.append(dict(key=key, coarse=coarse, fine=fine, relative_error=error,
                    x_relative_error=xe, qualified=error <= .05 and xe <= .05))
            else: destination.append(dict(key=key, coarse=coarse[0], fine=fine[0], relative_error=xe, qualified=xe <= .05))
    if not equal(frows, response['folds']) or not equal(grows, response['gaps']['variants']):
        raise ValueError('separate scalar c derivatives differ')
    good = all(r['qualified'] for r in frows+grows)
    if response['qualified'] != good: raise ValueError('scalar response qualification differs')
    proposed = result['proposal']
    if proposed is None:
        # The full deterministic controller replay independently enforces when
        # a proposal is absent; this scalar pass makes no extra target call.
        return
    if not good or not source['a_gaps']['qualified'] or not source['a_response']['qualified']:
        raise ValueError('unqualified derivatives authorized predictor')
    ja, jc = source['a_response']['variants'], frows
    ga, gc = source['a_gaps']['variants'], grows
    af = math.fsum(r['fine'][0] for r in ja)/16
    cf = math.fsum(r['fine'][0] for r in jc)/16
    f0 = math.fsum(r['residual'][0] for r in source['vectors'])/16
    intercept, tangent = -f0/af, -cf/af
    anchor = source['anchor']; center = source['a_center']
    amin, amax = max(-1., (center-1e-5-anchor['a'])/1e-5), min(1., (center+1e-5-anchor['a'])/1e-5)
    lo, hi = -1., 1.
    if tangent:
        ends = sorted([(amin-intercept)/tangent, (amax-intercept)/tangent])
        lo, hi = max(lo, ends[0]), min(hi, ends[1])
    elif not amin <= intercept <= amax: raise ValueError('impossible constant-a predictor')
    g0 = math.fsum(r['residual'] for r in source['gaps'][::2])/4
    ag = math.fsum(r['fine'] for r in ga[::2])/4
    cg = math.fsum(r['fine'] for r in gc[::2])/4
    slope = cg+ag*tangent
    wanted_c = max(lo, min(hi, -(g0+ag*intercept)/slope))
    wanted_a = anchor['a']+1e-5*(intercept+tangent*wanted_c)
    wanted_c = anchor['c']+.005*wanted_c
    if proposed['spec']['parameters'] != dict(anchor, a=wanted_a, c=wanted_c):
        raise ValueError('separate scalar bounded optimum differs')
    da, dc = (wanted_a-anchor['a'])/1e-5, (wanted_c-anchor['c'])/.005
    if not amin-1e-10 <= da <= amax+1e-10 or abs(dc) > 1+1e-10:
        raise ValueError('scalar realized bounds differ')
    pf = [dict(key=x['key'], residual=[q+u*da+v*dc for q, u, v in zip(x['residual'], a['fine'], c['fine'], strict=True)])
        for x, a, c in zip(source['vectors'], ja, jc, strict=True)]
    pg = [dict(key=x['key'], residual=x['residual']+a['fine']*da+c['fine']*dc)
        for x, a, c in zip(source['gaps'], ga, gc, strict=True)]
    if not equal(pf, proposed['predicted_vectors']) or not equal(pg, proposed['predicted_gaps']):
        raise ValueError('separate scalar full predictions differ')
    point = result['correction']
    if point is None or not point['qualified']: return
    fdec, gdec = [], []
    for q, b, p in zip(point['vectors'], source['vectors'], pf, strict=True):
        error = math.sqrt(math.fsum((x-y)**2 for x, y in zip(q['residual'], p['residual'], strict=True)))
        move = max(math.sqrt(math.fsum((x-y)**2 for x, y in zip(p['residual'], b['residual'], strict=True))), 1e-12)
        distance = max(map(abs, q['residual']))
        fdec.append(dict(key=q['key'], distance=distance, prediction_error=error/move,
                         qualified=distance <= 1e-4 and error/move <= .1))
    for q, b, p in zip(point['gaps'], source['gaps'], pg, strict=True):
        x, old, pred = q['residual'], b['residual'], p['residual']
        error = abs(x-pred)/max(abs(pred-old), 1e-8)
        gdec.append(dict(key=q['key'], before=old, actual=x, predicted=pred, prediction_error=error,
                         qualified=error <= .1, improved=abs(x) < abs(old)))
    decision = result['decision']; good = all(r['qualified'] for r in fdec+gdec) and all(r['improved'] for r in gdec[::2])
    if not equal(fdec, decision['folds']) or not equal(gdec, decision['gaps']) or decision['qualified'] != good:
        raise ValueError('separate scalar full-state/progress decision differs')


def audit(output, expected_sha):
    output = Path(output); p = run.load(); source = run.inputs()
    if sha256(output/'summary.json') != expected_sha: raise ValueError('summary byte identity differs')
    saved, binding = run.read(output/'summary.json'), run.read(output/'binding.json')
    run.prior.public.folds.finite_packet(saved)
    if (saved['experiment_id'] != 'EXP-521' or saved['status'] != 'completed' or saved['binding'] != binding
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
            or handshake['validation'] != run.validate() or run.read(output/'controls.json') != run.census_run.controls()):
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
        extended = run.stationarity(stage, point, source, check_product, tick, certificates)
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
    return dict(experiment_id='EXP-521', passed=True, source_commit=binding['source_commit'],
        plan_sha256=sha256(run.PLAN), summary_sha256=expected_sha, inputs=run.INPUTS, runtime=binding['runtime'],
        result=result, reused_a_gap_response=source['a_gaps'], historical_root_matches=source['historical_matches'],
        target_ivps=calls, segments=segments, output_bytes=directory_bytes(output), new_integrations=0,
        symbolic_chains_verified=False, D_identified=False, exact_critical_locus_proved=False, paid_review=p['paid_review'],
        scope='Full retained new midpoint/fold/guard/cycle replay, separate exact polynomial expansion and scalar response checks. Shared geometry/controller code, not independent-team verification, an exact-flow proof, a homoclinic result or a Jones arrow.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True); parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True); args = parser.parse_args()
    result = audit(args.run, args.expected_sha256)
    write_bounded_json(args.output.parent, args.output, result, limit_bytes=directory_bytes(args.output.parent)+32*1024**2)
    print(json.dumps(dict(passed=True, receipt_sha256=sha256(args.output))))
