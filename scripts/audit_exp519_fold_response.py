#!/usr/bin/env python3
"""Retained raw fold/cycle replay and separate scalar response arithmetic."""
import argparse
import json
import math
from pathlib import Path

from butterfly._paired_startup import inventory, sha256
from butterfly.bounded_json import directory_bytes, write_bounded_json
from scripts import run_exp519_fold_response as run
from scripts import audit_exp502_joint_contact as raw
from scripts import audit_exp518_fold_transport as transport_audit


def read(path):
    return json.loads(path.read_bytes())


def scalar_response(result, anchor, anchor_vectors):
    """No NumPy/controller differentiation or linear-solve calls in this check."""
    if not all(p['qualified'] for p in result['points']):
        if result['response']['qualified'] or result['proposal'] is not None or result['correction'] is not None:
            raise ValueError('failed stencil authorized correction')
        return
    points = result['points']; rows = []
    for i, key in enumerate(run.model.KEYS):
        derivatives = []
        for lo, hi in [(0, 1), (2, 3)]:
            a, b = [points[j]['vectors'][i] for j in (lo, hi)]
            if a['key'] != key or b['key'] != key:
                raise ValueError('scalar response variant identity differs')
            width = points[hi]['spec']['parameters']['a']-points[lo]['spec']['parameters']['a']
            derivatives.append([(float(y)-float(x))*1e-5/width for x, y in zip(a['residual'], b['residual'], strict=True)])
        c, f = derivatives
        norm = math.sqrt(math.fsum(x*x for x in f))
        xe = abs(c[0]-f[0])/max(abs(f[0]), 1e-30)
        fe = math.sqrt(math.fsum((x-y)**2 for x, y in zip(c, f, strict=True)))/max(norm, 1e-30)
        rows.append(dict(key=key, coarse=c, fine=f, x_relative_error=xe, full_relative_error=fe,
                         qualified=abs(f[0]) > 1e-8 and xe <= .05 and fe <= .05))
    oriented = all(r['fine'][0] > 0 for r in rows) or all(r['fine'][0] < 0 for r in rows)
    good = oriented and all(r['qualified'] for r in rows)
    expected = dict(qualified=good, reason=None if good else 'unresolved-or-inconsistent-fresh-response',
                    consistent_orientation=oriented, variants=rows)
    if not raw.old.periodic_audit.numeric_equal(expected, result['response']):
        raise ValueError('separate scalar derivative/qualification differs')
    proposed = result['proposal']
    if not good:
        if proposed is not None or result['correction'] is not None:
            raise ValueError('unqualified response authorized correction')
        return
    f = math.fsum(r['residual'][0] for r in anchor_vectors)/16
    j = math.fsum(r['fine'][0] for r in rows)/16
    step = max(-1., min(1., -f/j)); a = anchor['a']+1e-5*step
    realized = (a-anchor['a'])/1e-5
    if realized == 0:
        if proposed is not None:
            raise ValueError('scalar-floor step differs')
        return
    predictions = [dict(key=r['key'], residual=[x+realized*y for x, y in zip(r['residual'], slope['fine'], strict=True)])
                   for r, slope in zip(anchor_vectors, rows, strict=True)]
    rebuilt = dict(spec=dict(id='correction', parameters=dict(anchor, a=a)), mean_signed_x=f,
        mean_normalized_slope=j, requested_normalized_step=step, realized_normalized_step=realized,
        predicted_vectors=predictions)
    if not raw.old.periodic_audit.numeric_equal(rebuilt, proposed):
        raise ValueError('separate scalar proposal differs')
    point = result['correction']
    if point is None or not point['qualified']:
        return
    decisions = []
    for q, b, pred in zip(point['vectors'], anchor_vectors, predictions, strict=True):
        error = math.sqrt(math.fsum((x-y)**2 for x, y in zip(q['residual'], pred['residual'], strict=True)))
        denominator = max(math.sqrt(math.fsum((x-y)**2 for x, y in zip(pred['residual'], b['residual'], strict=True))), 1e-12)
        distance = max(abs(x) for x in q['residual'])
        decisions.append(dict(key=q['key'], full_state_distance=distance, signed_x=q['residual'][0],
            prediction_error=error/denominator, contact=distance <= 1e-4, prediction_qualified=error/denominator <= .1))
    contact = all(d['contact'] for d in decisions); prediction = all(d['prediction_qualified'] for d in decisions)
    expected = dict(qualified_contact=contact and prediction, full_state_contact=contact, prediction_qualified=prediction,
        reason=None if contact and prediction else 'full-state-contact-or-prediction-failed', variants=decisions)
    if not raw.old.periodic_audit.numeric_equal(expected, result['decision']):
        raise ValueError('separate scalar full-state verdict differs')


def check_rows(stage, candidates, p, binding, completed):
    names, calls = set(), 0
    def probe(c):
        nonlocal calls
        folder = stage/c['id']; profiles = []; rhs, _, section = run.coverage.fields(c)
        for method in p['solvers']:
            label = 'midpoint--'+method
            profile = read(folder/(label+'.json')); start = read(folder/(label+'-started.json'))
            if start['candidate'] != c or start['method'] != method or profile['method'] != method or not binding['started_utc'] <= start['started_utc'] <= completed:
                raise ValueError('midpoint configuration or clock differs')
            rebuilt, paths = run.prior.prior.previous.previous_audit.check_profile(folder, label, profile, c, c['seed_u'], p['numerical'], rhs, section)
            calls += len(paths)
            names.update(c['id']+'/'+n for n in paths | {label+'.json', label+'-started.json'})
            profiles.append(rebuilt)
        seeded, pair = run.prior.midpoint_seed(c, profiles, p)
        if read(folder/'seed.json') != dict(candidate=seeded, pair=pair):
            raise ValueError('midpoint seed differs')
        names.add(c['id']+'/seed.json')
        return seeded, profiles, pair
    def shoot(c):
        nonlocal calls
        folder = stage/c['id']; profiles = []
        comparison, paths, count = raw.old.check_fold(folder, c, p['numerical'], binding, completed)
        calls += count
        for method in p['solvers']:
            label = c['id']+'--'+method; profile = read(folder/(label+'.json'))
            for i, entry in enumerate(profile['censuses']):
                name = label+f'--guard-{i}.npz'
                raw.check_guard(raw.old.load_raw(folder/name), raw.old.load_raw(folder/(label+f'--census-{i}.npz')),
                                entry['report'], p['numerical']['guard'])
                paths.add(name); calls += 1
            profiles.append(profile)
        if comparison != dict(run.base.compare(c, profiles, p['numerical']), parent_id=c['parent_id']):
            raise ValueError('raw fold comparison differs')
        names.update(c['id']+'/'+n for n in paths)
        return profiles
    rows = run.prior.prior.model.follow(candidates, probe, shoot, lambda c, r: run.prior.assess(c, r, p))
    for row in rows:
        name = row['candidate']['id']+'/result.json'
        if not run.coverage.public.equal(row, read(stage/name)):
            raise ValueError('complete raw candidate replay differs')
        names.add(name)
    return rows, names, calls


def audit(output, expected_sha):
    p = run.load(); source = run.inputs()
    if sha256(output/'summary.json') != expected_sha:
        raise ValueError('summary byte identity differs')
    saved, binding = read(output/'summary.json'), read(output/'binding.json')
    run.public.folds.finite_packet(saved)
    if (saved['experiment_id'] != 'EXP-519' or saved['status'] != 'completed' or saved['binding'] != binding
            or binding['sources'] != {n: sha256(run.ROOT/n) for n in p['source_paths']}
            or binding['inputs'] != run.INPUTS or binding['plan_sha256'] != sha256(run.PLAN)
            or binding['paid_review'] != p['paid_review'] or saved['symbolic_chains_verified'] is not False
            or binding['initial_free_bytes'] < p['limits']['initial_free_bytes']
            or saved['files'] != inventory(output, omit=('summary.json',))
            or not binding['started_utc'] <= saved['completed_utc']
            or not 0 <= saved['elapsed_seconds'] <= p['limits']['wall_seconds']):
        raise ValueError('source, input, inventory, clock or resource binding differs')
    marker = run.ROOT/'artifacts/EXP-519/target-once.json'
    if sha256(marker) != saved['marker_sha256'] or read(marker) != binding:
        raise ValueError('consumed marker differs')
    startup = read(output/'startup.json')
    if (startup['passed'] is not True or startup['isolated'] is not True or startup['new_integrations'] != 0
            or startup['sources'] != {n: sha256(run.ROOT/n) for n in set(p['source_paths']) | set(run.INPUTS)}
            or json.loads(startup['stdout']) != dict(valid=True, new_integrations=0, stencil_points=4, maximum_corrections=1, maximum_target_ivps=768)):
        raise ValueError('isolated startup differs')
    controls = run.prior.prior.controls(p)
    if controls != read(output/'control-replay.json'):
        raise ValueError('analytic control replay differs')
    names = {'binding.json', 'startup.json', 'control-replay.json'}; calls = 0; seen = []
    def measure(spec):
        nonlocal calls
        stage = output/spec['id']
        candidates = run.model.candidates(source['rows'], spec, run.prior.transport.offset(spec['parameters']))
        if read(stage/'inputs.json') != dict(spec=spec, candidates=candidates):
            raise ValueError('fixed-anchor candidate inputs differ')
        rows, paths, count = check_rows(stage, candidates, p, binding, saved['completed_utc'])
        calls += count
        cycle = read(stage/'cycle.json')
        cycle_paths, count = raw.old.check_cycle(stage, cycle, spec, source['cycle']['profiles'][0]['correction'], p['periodic'])
        calls += count
        names.update(spec['id']+'/'+n for n in paths | cycle_paths | {'inputs.json', 'cycle.json', 'point.json'})
        point = run.summarize(spec, rows, cycle, p, source)
        transport_audit.scalar_decision(source['rows'], rows, point['fold_identity'])
        if point['contact'] is not None:
            scalar = raw.old.scalar_contact([r['assessment']['comparison'] for r in rows], cycle)
            if not raw.old.periodic_audit.numeric_equal(scalar, point['contact']):
                raise ValueError('separate scalar fold/cycle contact differs')
        if not run.coverage.public.equal(point, read(stage/'point.json')):
            raise ValueError('complete raw point replay differs')
        seen.append(dict(id=spec['id'], status='completed'))
        print(json.dumps(dict(audited_point=spec['id'], target_ivps=calls)), flush=True)
        return point
    result = run.model.follow(source['anchor'], source['anchor_vectors'], measure)
    scalar_response(result, source['anchor'], source['anchor_vectors'])
    size = directory_bytes(output)
    if (not run.coverage.public.equal(result, saved['result']) or names != set(saved['files'])
            or calls != saved['target_ivps'] or calls > p['limits']['target_ivps']
            or saved['point_progress'] != seen or size > p['limits']['output_bytes']):
        raise ValueError('complete response/point/IVP/output accounting differs')
    return dict(experiment_id='EXP-519', passed=True, protocol_compliant=True, source_commit=binding['source_commit'],
        plan_sha256=sha256(run.PLAN), summary_sha256=expected_sha, inputs=run.INPUTS, result=result,
        controls=controls, target_ivps=calls, output_bytes_including_summary=size,
        output_limit_bytes=p['limits']['output_bytes'], new_integrations=0, symbolic_chains_verified=False,
        paid_review=p['paid_review'], scope='Full retained raw midpoint, fold, guard, cycle and event replay; separately coded scalar response and verdict. Not an independent-team or rigorous exact-flow proof.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True); parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args(); result = audit(a.run, a.expected_sha256)
    write_bounded_json(a.output.parent, a.output, result, limit_bytes=directory_bytes(a.output.parent)+32*1024**2)
    print(json.dumps(dict(passed=True, target_ivps=result['target_ivps'], audit_sha256=sha256(a.output))))
