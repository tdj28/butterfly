#!/usr/bin/env python3
"""Full raw replay and scalar checks for refreshed two-step continuation."""
import argparse
from copy import deepcopy
import json
import math
from pathlib import Path
import time
from butterfly._paired_startup import inventory, sha256
from butterfly.bounded_json import directory_bytes, write_bounded_json
from scripts import run_exp523_refreshed_path as run
from scripts import audit_exp519_fold_response as folds
from scripts import audit_exp520_periodic_census as roots


def scalar_check(result, source):
    """Separate scalar derivatives, curvature, predictions and endpoint tests."""
    from scripts import audit_exp521_critical_response as linear
    from scripts import audit_exp522_nonlinear_refinement as normal
    equal = folds.raw.old.periodic_audit.numeric_equal
    current = deepcopy(source)
    norm = lambda xs: math.sqrt(math.fsum(x*x for x in xs))
    accepted = []
    for row in result['steps']:
        fresh = row['response']; ap = row['a_points']; cp = row['c_points']
        if row['anchor'] != current['anchor'] or fresh['center'] != current['anchor']:
            raise ValueError('scalar derivative center differs')
        # Check a-fold and a-gap slopes directly, including all variant keys.
        if all(p['qualified'] for p in ap):
            expected_a, expected_g = [], []
            for name, keys, dest in [('vectors', run.model.local.fold.KEYS, expected_a),
                                      ('gaps', run.model.local.GKEYS, expected_g)]:
                for i, key in enumerate(keys):
                    slopes = []
                    for lo, hi in [(0, 1), (2, 3)]:
                        x, y = ap[lo][name][i], ap[hi][name][i]
                        if x['key'] != key or y['key'] != key: raise ValueError('scalar key differs')
                        left = x['residual'] if name == 'vectors' else [x['residual']]
                        right = y['residual'] if name == 'vectors' else [y['residual']]
                        width = ap[hi]['spec']['parameters']['a']-ap[lo]['spec']['parameters']['a']
                        slopes.append([(b-a)*1e-5/width for a, b in zip(left, right, strict=True)])
                    co, fi = slopes
                    xe = abs(co[0]-fi[0])/max(abs(fi[0]), 1e-30 if name == 'vectors' else 1e-8)
                    fe = norm([x-y for x, y in zip(co, fi, strict=True)])/max(norm(fi), 1e-30)
                    if name == 'vectors':
                        dest.append(dict(key=key, coarse=co, fine=fi, x_relative_error=xe,
                            full_relative_error=fe, qualified=abs(fi[0]) > 1e-8 and xe <= .05 and fe <= .05))
                    else: dest.append(dict(key=key, coarse=co[0], fine=fi[0], relative_error=xe, qualified=xe <= .05))
            if not equal(expected_a, fresh['a']['variants']) or not equal(expected_g, fresh['a_gaps']['variants']):
                raise ValueError('scalar a response differs')
            oriented = all(r['fine'][0] > 0 for r in expected_a) or all(r['fine'][0] < 0 for r in expected_a)
            if (fresh['a']['consistent_orientation'] != oriented
                    or fresh['a']['qualified'] != (oriented and all(r['qualified'] for r in expected_a))
                    or fresh['a_gaps']['qualified'] != all(r['qualified'] for r in expected_g)):
                raise ValueError('scalar a qualification differs')
        elif fresh['a']['qualified'] or fresh['a_gaps']['qualified']:
            raise ValueError('failed a stencil qualified')
        # Existing separate scalar c arithmetic also verifies the bounded linear seed.
        cpoints = [dict(p, spec=s) for p, s in zip(cp, run.model.local.stencil(current['anchor']), strict=True)]
        linear_source = dict(current, a_response=fresh['a'], a_gaps=fresh['a_gaps'], a_center=current['anchor']['a'])
        proposed = row['proposal']
        linear.scalar_check(dict(points=cpoints, response=fresh['c'],
            proposal=None if proposed is None else proposed['linear_seed'], correction=None), linear_source)
        curvature = fresh['curvature']
        if curvature is not None:
            for name, prefix in [('vectors', 'fold'), ('gaps', 'gap')]:
                computed = []
                for lo, hi in [(0, 1), (2, 3)]:
                    width = (cp[hi]['spec']['parameters']['c']-cp[lo]['spec']['parameters']['c'])/2
                    q = []
                    for low, high, center in zip(cp[lo][name], cp[hi][name], current[name], strict=True):
                        if name == 'vectors':
                            q.append([((a+b)/2-z)*(.005/width)**2 for a, b, z in
                                zip(low['residual'], high['residual'], center['residual'], strict=True)])
                        else: q.append(((low['residual']+high['residual'])/2-center['residual'])*(.005/width)**2)
                    computed.append(q)
                errors = []
                for co, fi in zip(*computed, strict=True):
                    errors.append(norm([x-y for x, y in zip(co, fi, strict=True)])/max(norm(fi), 1e-8)
                        if name == 'vectors' else abs(co-fi)/max(abs(fi), 1e-8))
                if any(not equal(value, curvature[prefix+'_'+key]) for value, key in
                       zip([*computed, errors], ['coarse', 'fine', 'errors'], strict=True)):
                    raise ValueError('scalar curvature differs')
            if curvature['qualified'] != all(e <= .05 for e in curvature['fold_errors']+curvature['gap_errors']):
                raise ValueError('scalar curvature qualification differs')
        qualified = all(fresh[n]['qualified'] for n in ('a', 'a_gaps', 'c'))
        if fresh['qualified'] != (qualified and curvature is not None and curvature['qualified']):
            raise ValueError('scalar complete response qualification differs')
        if proposed is not None and not fresh['qualified']:
            raise ValueError('failed response authorized a predictor')
        if proposed is None: continue
        ja, jc = fresh['a']['variants'], fresh['c']['folds']
        ga, gc = fresh['a_gaps']['variants'], fresh['c']['gaps']['variants']
        dc = proposed['linear_seed']['normalized_c_step']
        qf, qg = curvature['fold_fine'], curvature['gap_fine']
        # Match the prescribed parenthesized scalar update, not a reassociated expression.
        correction = math.fsum(x[0] for x in qf)/math.fsum(x['fine'][0] for x in ja)*dc*dc
        a = proposed['linear_seed']['spec']['parameters']['a']-1e-5*correction
        da = (a-current['anchor']['a'])/1e-5
        pf = [dict(key=x['key'], residual=[v+j*da+k*dc+q*dc*dc for v, j, k, q in
            zip(x['residual'], aa['fine'], cc['fine'], qq, strict=True)])
            for x, aa, cc, qq in zip(current['vectors'], ja, jc, qf, strict=True)]
        pg = [dict(key=x['key'], residual=x['residual']+aa['fine']*da+cc['fine']*dc+q*dc*dc)
            for x, aa, cc, q in zip(current['gaps'], ga, gc, qg, strict=True)]
        if (not abs(da) <= 1 or proposed['spec']['parameters'] != dict(proposed['linear_seed']['spec']['parameters'], a=a)
                or proposed['derivative_center'] != current['anchor']
                or not equal(pf, proposed['predicted_vectors']) or not equal(pg, proposed['predicted_gaps'])
                or not equal(da, proposed['normalized_a_step']) or not equal(dc, proposed['normalized_c_step'])):
            raise ValueError('scalar quadratic parameter or prediction differs')
        trial = row['predictor']
        if trial['qualified']:
            fd, gd = [], []
            for q, b, p in zip(trial['vectors'], current['vectors'], pf, strict=True):
                distance = max(map(abs, q['residual']))
                error = norm([x-y for x, y in zip(q['residual'], p['residual'], strict=True)])/max(
                    norm([x-y for x, y in zip(p['residual'], b['residual'], strict=True)]), 1e-12)
                fd.append(dict(key=q['key'], distance=distance, prediction_error=error, qualified=distance <= 1e-4 and error <= .1))
            for q, b, p in zip(trial['gaps'], current['gaps'], pg, strict=True):
                x, old, pred = q['residual'], b['residual'], p['residual']; error = abs(x-pred)/max(abs(pred-old), 1e-8)
                gd.append(dict(key=q['key'], before=old, actual=x, predicted=pred, prediction_error=error,
                    qualified=error <= .1, improved=abs(x) < abs(old)))
            good = all(r['qualified'] for r in fd+gd) and all(r['improved'] for r in gd[::2])
            if not equal(dict(qualified=good, reason=None if good else 'contact-prediction-or-progress-failed',
                    folds=fd, gaps=gd), row['predictor_decision']):
                raise ValueError('scalar predictor decision differs')
        if row['refinement'] is not None:
            decision = row['predictor_decision']
            if (not trial['qualified'] or not all(r['qualified'] for r in decision['gaps'])
                    or not all(r['improved'] for r in decision['gaps'][::2])
                    or max(r['distance'] for r in decision['folds']) > 1e-4
                    or (decision['qualified'] and all(max(map(abs, r['residual'])) <= 1e-7 for r in trial['vectors']))):
                raise ValueError('scalar unauthorized normal correction')
            origin = dict(run.model.recenter(current, trial), a_response=fresh['a'], a_gaps=fresh['a_gaps'],
                a_center=current['anchor']['a'], a_derivative_center=current['anchor'],
                progress_anchor=current['anchor'], progress_gaps=current['gaps'])
            packet = deepcopy(dict(proposal=row['refinement_proposal'], correction=row['refinement'], decision=row['refinement_decision']))
            packet['proposal']['spec']['id'] = 'nonlinear-refinement'
            packet['correction']['spec']['id'] = 'nonlinear-refinement'
            normal.scalar_check(packet, origin)
        if row['accepted'] is not None:
            endpoint = row['refinement'] if row['refinement'] is not None else trial
            decision = row['refinement_decision'] if row['refinement'] is not None else row['predictor_decision']
            if (not endpoint['qualified'] or row['accepted'] != endpoint['spec']
                    or not decision['qualified']
                    or any(max(map(abs, r['residual'])) > 1e-7 for r in endpoint['vectors'])):
                raise ValueError('scalar accepted contact differs')
            accepted.append(endpoint['spec']); current = run.model.recenter(current, endpoint)
    if accepted != result['accepted'] or result['completed_steps'] != len(accepted) or result['qualified'] != (len(accepted) == 2):
        raise ValueError('scalar complete path accounting differs')


def audit(output, expected_sha):
    output = Path(output); p = run.load(); source = run.inputs()
    if sha256(output/'summary.json') != expected_sha: raise ValueError('summary byte identity differs')
    saved, binding = run.read(output/'summary.json'), run.read(output/'binding.json')
    run.prior.public.folds.finite_packet(saved)
    if (saved['experiment_id'] != 'EXP-523' or saved['status'] != 'completed' or saved['binding'] != binding
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
    def measure(spec, current):
        nonlocal calls
        stage = output/spec['id']
        candidates = run.prior.model.candidates(current['rows'], spec, run.prior.prior.transport.offset(spec['parameters']))
        if run.read(stage/'inputs.json') != dict(spec=spec, candidates=candidates): raise ValueError('candidate inputs differ')
        rows, paths, count = folds.check_rows(stage, candidates, p, binding, saved['completed_utc']); calls += count
        cycle = run.read(stage/'cycle.json')
        cycle_paths, count = folds.raw.old.check_cycle(stage, cycle, spec, current['cycle']['profiles'][0]['correction'], p['periodic'])
        calls += count
        point = run.prior.summarize(spec, rows, cycle, p, current)
        folds.transport_audit.scalar_decision(current['rows'], rows, point['fold_identity'])
        if point['contact'] is not None:
            scalar = folds.raw.old.scalar_contact([r['assessment']['comparison'] for r in rows], cycle)
            if not folds.raw.old.periodic_audit.numeric_equal(scalar, point['contact']): raise ValueError('scalar contact differs')
        if not run.prior.coverage.public.equal(point, run.read(stage/'point.json')): raise ValueError('raw point replay differs')
        certificates = {m: run.read(stage/('stationarity--'+m+'.json'))['certificates'] for m in p['solvers']}
        def check_product(name, value):
            if not roots.same(value, run.read(stage/name)): raise ValueError('separate exact polynomial census replay differs')
        extended = run.parent.stationarity(stage, point, current, check_product, tick, certificates)
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
    return dict(experiment_id='EXP-523', passed=True, source_commit=binding['source_commit'],
        plan_sha256=sha256(run.PLAN), summary_sha256=expected_sha, inputs=run.INPUTS, runtime=binding['runtime'],
        result=result, target_ivps=calls, segments=segments, output_bytes=directory_bytes(output), new_integrations=0,
        initial_anchor=source['anchor'],
        symbolic_chains_verified=False, D_identified=False, exact_critical_locus_proved=False,
        paid_review=p['paid_review'],
        scope='Full retained raw replay, separate polynomial expansion and scalar arithmetic; shared geometry/controller. At most two refreshed locally qualified sampled steps, not a continuous exact locus, grazing endpoint, homoclinic result or Jones arrow.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True); parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True); args = parser.parse_args()
    result = audit(args.run, args.expected_sha256)
    write_bounded_json(args.output.parent, args.output, result, limit_bytes=directory_bytes(args.output.parent)+128*1024**2)
    print(json.dumps(dict(passed=True, receipt_sha256=sha256(args.output))))
