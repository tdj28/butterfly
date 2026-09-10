#!/usr/bin/env python3
"""Compact point/response replay, explicitly separate from the full raw audit."""
import argparse
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from butterfly._paired_startup import sha256
from butterfly.models import RosslerParameters, rossler_rhs
from butterfly.poincare import legacy_rossler_section, barrio_rossler_section
from scripts import run_exp519_fold_response as run
from scripts import audit_exp519_fold_response as raw

SOURCE = 'cdd08b37762e2c89bc368535331450c94cd33f53'
equal = run.public.equal


def require_same(actual, expected, message):
    if not equal(actual, expected):
        raise ValueError(message)


def check_cycle(cycle, spec, seed, settings):
    """Recompute compact event/metric gates, not missing dense flow polynomials."""
    if cycle['spec'] != spec or [p['method'] for p in cycle['profiles']] != settings['methods']:
        raise ValueError('complete cycle identity/method matrix required')
    par = RosslerParameters(**spec['parameters'])
    sections = dict(historical=replace(legacy_rossler_section(par), direction=-1), barrio=barrio_rossler_section(par))
    calls = 0
    for profile in cycle['profiles']:
        prefix = spec['id']+'--'+profile['method']
        files = profile['raw_files']; calls += len(files)
        shooting = [n for n in files if '--shooting-' in n]
        expected_files = [prefix+f'--shooting-{i:02d}.npz' for i in range(len(shooting))]
        if files and files[-1] == prefix+'--observation.npz':
            expected_files.append(prefix+'--observation.npz')
        if files != expected_files or len(files) != len(set(files)):
            raise ValueError('cycle raw-product identity/order differs')
        if 'observation' in profile and prefix+'--observation.npz' not in files:
            raise ValueError('cycle observation product missing')
        if 'correction' in profile:
            c = profile['correction']
            initial, final = np.asarray(c['initial_state']), np.asarray(c['final_state'])
            if initial.shape != (3,) or final.shape != (3,) or c['period_time'] <= 0:
                raise ValueError('complete finite cycle correction required')
            direction = rossler_rhs(0., np.asarray(seed['initial_state']), par)
            direction /= np.linalg.norm(direction)
            require_same(c['closure_error'], float(np.linalg.norm(final-initial)), 'cycle closure differs')
            require_same(c['phase_residual'], abs(float(np.dot(initial-seed['initial_state'], direction))), 'cycle phase differs')
            require_same(profile['correction_gate'], run.base.previous.cycles_run.correction_gate(c, seed, settings), 'cycle correction gate differs')
        if 'metric' not in profile:
            if profile['qualified']:
                raise ValueError('qualified cycle lacks observation metric')
            continue
        metric, report = profile['metric'], profile['observation']; period = profile['correction']['period_time']
        if set(report['events']) != set(sections) or [w['phase'] for w in metric['windows']] != [.25, 1.25]:
            raise ValueError('complete sections and repeat windows required')
        for name, events in report['events'].items():
            times = [e['time'] for e in events]
            if any(not 0 <= t <= 2.5*period for t in times) or any(b <= a for a, b in zip(times[:-1], times[1:])):
                raise ValueError('ordered in-horizon cycle events required')
            section = sections[name]
            for event in events:
                q = np.asarray(event['state']); f = rossler_rhs(event['time'], q, par)
                velocity = float(np.dot(section.normal, f))
                angle = abs(velocity)/float(np.linalg.norm(section.normal)*np.linalg.norm(f))
                require_same(event['normal_velocity'], velocity, 'cycle event velocity differs')
                require_same(event['angle'], angle, 'cycle crossing angle differs')
                require_same(event['residual'], float(section.value(q)), 'cycle plane residual differs')
                if event['accepted'] != bool(section.accepts(q) and section.direction*velocity > 0):
                    raise ValueError('cycle event acceptance differs')
        uncertain = []
        for event in report['extrema']:
            value = float(sections[event['section']].value(np.asarray(event['state'])))
            require_same(event['plane_value'], value, 'cycle extremum plane differs')
            if .25*period <= event['time'] <= 2.25*period and abs(value) <= 1e-8:
                uncertain.append(event)
        require_same(report['uncertain_extrema'], uncertain, 'cycle uncertain-extremum inventory differs')
        maximum = max((abs(e['residual']) for events in report['events'].values() for e in events), default=0.)
        require_same(report['maximum_event_residual'], maximum, 'cycle maximum plane residual differs')
        for w in metric['windows']:
            start, end = w['phase']*period, (w['phase']+1)*period
            selected = {name: [e for e in events if start <= e['time'] < end and e['accepted']]
                        for name, events in report['events'].items()}
            counts = {name: len(events) for name, events in selected.items()}
            states = {name: [e['state'] for e in events] for name, events in selected.items()}
            phases = {name: [(e['time']-start)/period for e in events] for name, events in selected.items()}
            distinct = {name: min((float(np.linalg.norm((np.asarray(a)-b)/[15., 15., .01]))
                                  for i, a in enumerate(events) for b in events[i+1:]), default=None)
                        for name, events in states.items()}
            for key, value in dict(counts=counts, event_states=states, event_phases=phases,
                                   minimum_distinct_event_separation=distinct).items():
                require_same(w[key], value, 'cycle window '+key+' differs')
            endpoints = np.asarray(w['endpoints'])
            if endpoints.shape != (2, 3):
                raise ValueError('complete window endpoints required')
            closure = float(np.linalg.norm((endpoints[1]-endpoints[0])/[15., 15., .01]))
            require_same(w['closure_scaled'], closure, 'window closure differs')
            angles = [e['angle'] for events in selected.values() for e in events]
            minimum = min(angles) if angles else None
            margin = min((min(abs(e['time']-start), abs(e['time']-end))/period
                          for events in report['events'].values() for e in events if e['accepted']), default=0.)
            require_same(w['minimum_crossing_angle'], minimum, 'window minimum angle differs')
            require_same(w['boundary_phase_margin'], margin, 'window phase margin differs')
            gcd = math.gcd(*counts.values()); divisors = [m for m in range(2, gcd+1) if gcd % m == 0]
            if [s['multiplicity'] for s in w['shorter_periods']] != divisors:
                raise ValueError('complete shorter-period divisor matrix required')
            for s in w['shorter_periods']:
                if s['scaled_separation'] < 0 or s['excluded'] != (s['scaled_separation'] >= 1e-5):
                    raise ValueError('shorter-period exclusion differs')
            primitive = all(n > 0 for n in counts.values()) and all(s['excluded'] for s in w['shorter_periods']) and all(v is None or v >= 1e-5 for v in distinct.values())
            if w['conditional_minimal_period'] != primitive:
                raise ValueError('conditional primitive gate differs')
            if set(w['geometry']) != {'raw', 'extrema_augmented', 'midpoint_enriched'}:
                raise ValueError('complete winding-resolution matrix required')
            for g in w['geometry'].values():
                if g['minimum_radius'] == 0:
                    if g['qualified'] or g['cut_index'] is not None:
                        raise ValueError('origin-intersecting polygon promoted')
                    continue
                turns = (g['angle_change']-g['endpoint_difference'])/(2*math.pi)
                index = round(turns); error = abs(turns-index)
                require_same(g['integer_error'], error, 'polygon integer error differs')
                if g['cut_index'] != index or g['qualified'] != (g['minimum_radius'] >= 1e-10 and g['maximum_angle_step'] <= 2.9 and error <= 1e-10):
                    raise ValueError('reported polygon gate differs')
            indices = [g['cut_index'] for g in w['geometry'].values()]
            good = (closure <= 1e-6 and all(g['qualified'] for g in w['geometry'].values())
                    and len(set(indices)) == 1 and indices[0] == counts['historical'] and primitive
                    and bool(angles) and minimum >= 1e-6 and margin >= 1e-7)
            if w['qualified'] != good:
                raise ValueError('complete compact window gate differs')
        repeat = run.base.previous.cycles_run.geometry.compare_windows(*metric['windows'])
        require_same(metric['repeat'], repeat, 'within-cycle repeat comparison differs')
        good = all(w['qualified'] for w in metric['windows']) and repeat['passed']
        if metric['qualified'] != good or metric['rigorous_minimal_period_proof'] is not False:
            raise ValueError('cycle metric qualification/claim differs')
        if profile['qualified'] != bool(profile['correction_gate']['passed'] and good and not uncertain and maximum <= 1e-8):
            raise ValueError('complete cycle profile qualification differs')
    pair = run.base.previous.cycles_run.compare_profiles(cycle['profiles'], settings)
    counts = pair['passed'] and all(w['counts'] == dict(historical=6, barrio=8) for profile in cycle['profiles'] for w in profile['metric']['windows'])
    expected = dict(spec=spec, profiles=cycle['profiles'], pair=pair, status='qualified' if counts else 'unqualified')
    if pair['passed'] and not counts:
        expected['count_failure'] = True
    require_same(cycle, expected, 'paired cycle status differs')
    return calls


def verify(path, expected_sha):
    path = Path(path)
    if sha256(path) != expected_sha:
        raise ValueError('public receipt byte identity differs')
    saved = json.loads(path.read_bytes()); run.public.folds.finite_packet(saved)
    p, source = run.load(), run.inputs()
    if (saved['experiment_id'] != 'EXP-519' or saved['passed'] is not True or saved['protocol_compliant'] is not True
            or saved['source_commit'] != SOURCE or saved['inputs'] != run.INPUTS or saved['plan_sha256'] != sha256(run.PLAN)
            or saved['new_integrations'] != 0 or saved['symbolic_chains_verified'] is not False or saved['paid_review'] != p['paid_review']
            or type(saved['target_ivps']) is not int or not 0 < saved['target_ivps'] <= p['limits']['target_ivps']
            or type(saved['output_bytes_including_summary']) is not int or not 0 < saved['output_bytes_including_summary'] <= p['limits']['output_bytes']
            or saved['output_limit_bytes'] != p['limits']['output_bytes']):
        raise ValueError('public source, input, resources or claim binding differs')
    encoded = (json.dumps(saved['controls'], sort_keys=True, indent=2, allow_nan=False)+'\n').encode()
    if hashlib.sha256(encoded).hexdigest() != run.public.folds.CONTROL_SHA:
        raise ValueError('pre-target control summary differs')
    points = saved['result']['points']+([] if saved['result']['correction'] is None else [saved['result']['correction']])
    seen, calls = [], 0
    def measure(spec):
        nonlocal calls
        if len(seen) >= len(points):
            raise ValueError('required response point missing')
        point = points[len(seen)]
        candidates = run.model.candidates(source['rows'], spec, run.prior.transport.offset(spec['parameters']))
        if point['spec'] != spec or len(point['rows']) != 4:
            raise ValueError('fixed complete point identity differs')
        for row, candidate in zip(point['rows'], candidates, strict=True):
            calls += run.public.check_row(row, candidate, p)
        calls += check_cycle(point['cycle'], spec, source['cycle']['profiles'][0]['correction'], p['periodic'])
        rebuilt = run.summarize(spec, point['rows'], point['cycle'], p, source)
        require_same(point, rebuilt, 'compact complete point differs')
        raw.transport_audit.scalar_decision(source['rows'], point['rows'], point['fold_identity'])
        if point['contact'] is not None:
            scalar = raw.raw.old.scalar_contact([r['assessment']['comparison'] for r in point['rows']], point['cycle'])
            require_same(scalar, point['contact'], 'separate scalar contact differs')
        seen.append(spec['id'])
        return rebuilt
    result = run.model.follow(source['anchor'], source['anchor_vectors'], measure)
    raw.scalar_response(result, source['anchor'], source['anchor_vectors'])
    require_same(result, saved['result'], 'complete response/correction verdict differs')
    if len(seen) != len(points) or calls != saved['target_ivps']:
        raise ValueError('complete point or integration count differs')
    return dict(experiment_id='EXP-519', passed=True, points=len(points), target_ivps=calls,
        response_qualified=result['response']['qualified'], correction_executed=result['correction'] is not None,
        decision=result['decision'], new_integrations=0, full_raw_audit_repeated=False, symbolic_chains_verified=False,
        scope='Compact fold algebra/prefixes, cycle event geometry and reported primitive/winding gates, full-state correspondence and response arithmetic replayed. Raw meshes, census completeness, polygon geometry, shorter-period interpolation and disk totals are not independently re-audited here.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result', type=Path, required=True); parser.add_argument('--expected-sha256', required=True)
    a = parser.parse_args(); print(json.dumps(verify(a.result, a.expected_sha256), sort_keys=True))
