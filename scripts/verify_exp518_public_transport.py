#!/usr/bin/env python3
"""Replay compact transport evidence; does not re-audit the retained raw meshes."""
import argparse
import hashlib
import json
from pathlib import Path

from butterfly._paired_startup import sha256
from scripts import run_exp518_fold_transport as run
from scripts import audit_exp518_fold_transport as raw
from scripts import verify_exp517_public_folds as folds

SOURCE = 'bc404a33d6270070f3ee91730105d5610e0024a0'
equal = folds.equal


def check_row(row, candidate, p):
    if row['candidate'] != candidate or [v['method'] for v in row['midpoints']] != p['solvers']:
        raise ValueError('complete candidate and midpoint matrix required')
    profiles = [run.prior.public.measurement(v, dict(candidate=candidate, u=candidate['seed_u']), p['numerical'])
                for v in row['midpoints']]
    calls = sum(len(v['products']) for v in profiles)
    seeded, pair = run.midpoint_seed(candidate, profiles, p)
    if not equal(seeded, row['seeded_candidate']) or not equal(pair, row['midpoint_pair']):
        raise ValueError('transport midpoint seed differs')
    if seeded is None:
        if row['status'] != 'midpoint-unqualified' or row['folds'] is not None or row['assessment'] is not None:
            raise ValueError('failed midpoint promoted to a fold')
        return calls
    if row['status'] != 'searched' or [v['method'] for v in row['folds']] != p['solvers']:
        raise ValueError('complete searched solver matrix required')
    rhs, _, section = run.coverage.fields(seeded)
    for profile in row['folds']:
        shooting = profile['shooting']
        trace = shooting['trace']
        if (not 1 <= len(trace) <= p['numerical']['iterations']
                or shooting['retained_labels'] != [f'newton-{i}' for i in range(len(trace))]):
            raise ValueError('compact shooting inventory differs')
        folds.compact_trace(shooting, seeded, p['numerical'])
        if shooting['reason'] == 'fixed search box exceeded':
            last = trace[-1]
            u, t = [last[k]-last['newton_step'][i] for i, k in enumerate(('u', 'time'))]
            if seeded['u_box'][0] <= u <= seeded['u_box'][1] and seeded['time_box'][0] <= t <= seeded['time_box'][1] and t > 0:
                raise ValueError('unfounded compact search-box failure')
        offsets = []
        if shooting['converged']:
            u = trace[-1]['u']
            if seeded['u_box'][0] <= u-seeded['epsilon'] < u+seeded['epsilon'] <= seeded['u_box'][1]:
                offsets = [-seeded['epsilon'], 0., seeded['epsilon']]
        if [v['offset'] for v in profile['censuses']] != offsets:
            raise ValueError('prescribed local census offsets differ')
        for census in profile['censuses']:
            report = census['report']
            observation = run.coverage.model.observation(report, seeded, rhs, section, p['numerical']['thresholds'])
            run.prior.public.measurement(dict(method=profile['method'], status='completed', products=['guard', 'main'],
                report=report, measurement=observation), dict(candidate=seeded, u=trace[-1]['u']+census['offset']), p['numerical'])
        qualification = run.base.previous.folds_run.qualify(shooting, profile['censuses'], seeded, rhs, section, p['numerical'])
        if not equal(qualification, profile['qualification']):
            raise ValueError('local fold qualification differs')
        calls += len(trace)+2*len(profile['censuses'])
    if not equal(run.assess(seeded, row['folds'], p), row['assessment']):
        raise ValueError('complete event-prefix assessment differs')
    return calls


def verify(path, expected_sha):
    path = Path(path)
    if sha256(path) != expected_sha:
        raise ValueError('public receipt byte identity differs')
    saved = json.loads(path.read_bytes())
    folds.finite_packet(saved)
    p = run.load()
    if (saved['experiment_id'] != 'EXP-518' or saved['passed'] is not True or saved['protocol_compliant'] is not True
            or saved['source_commit'] != SOURCE or saved['inputs'] != run.INPUTS or saved['plan_sha256'] != sha256(run.PLAN)
            or saved['new_integrations'] != 0 or saved['symbolic_chains_verified'] is not False
            or saved['paid_review'] != p['paid_review'] or type(saved['target_ivps']) is not int
            or not 0 < saved['target_ivps'] <= p['limits']['target_ivps']
            or type(saved['output_bytes_including_summary']) is not int
            or not 0 < saved['output_bytes_including_summary'] <= p['limits']['output_bytes']
            or saved['output_limit_bytes'] != p['limits']['output_bytes']):
        raise ValueError('public source, resources or claim binding differs')
    control_bytes = (json.dumps(saved['controls'], sort_keys=True, indent=2, allow_nan=False)+'\n').encode()
    if hashlib.sha256(control_bytes).hexdigest() != folds.CONTROL_SHA:
        raise ValueError('pre-target control summary differs')
    previous = run.inputs()
    seen, calls = [], 0
    def measure(spec, candidates):
        nonlocal previous, calls
        if len(seen) >= len(saved['result']['rows']):
            raise ValueError('required transport stage missing')
        item = saved['result']['rows'][len(seen)]
        rows = item['rows']
        if item['spec'] != spec or len(rows) != len(candidates):
            raise ValueError('complete fixed stage matrix required')
        for row, candidate in zip(rows, candidates, strict=True):
            calls += check_row(row, candidate, p)
        decision = run.model.decision(previous, rows)
        raw.scalar_decision(previous, rows, decision)
        previous = rows
        seen.append(spec['id'])
        return rows
    result = run.model.follow(previous, p['specifications'], run.transport.offset, measure)
    endpoint = run.endpoint(result)
    if (not equal(result, saved['result']) or not equal(endpoint, saved['endpoint_comparison'])
            or len(seen) != len(saved['result']['rows']) or calls != saved['target_ivps']):
        raise ValueError('complete stage decisions, endpoint or IVP accounting differs')
    if endpoint is not None:
        comparisons = [dict(r['assessment']['comparison'], parent_id=r['candidate']['parent_id']) for r in result['rows'][-1]['rows']]
        scalar = raw.fold_audit.old.scalar_contact(comparisons, run.transport.inputs()['cycle'])
        if not raw.fold_audit.old.periodic_audit.numeric_equal(scalar, endpoint['contact']):
            raise ValueError('separate endpoint arithmetic differs')
    return dict(experiment_id='EXP-518', passed=True, executed_substeps=len(seen), target_ivps=calls,
        transport_completed=result['transport_completed'], decisions=[r['decision'] for r in result['rows']],
        endpoint_fold_proximity=None if endpoint is None else endpoint['fold_proximity'],
        new_integrations=0, full_raw_audit_repeated=False, symbolic_chains_verified=False,
        scope='Compact shooting algebra, full accepted prefixes, qualification, transport and endpoint arithmetic replayed. Raw meshes, polynomial census completeness, control bundles and disk byte totals are not independently audited here.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.result, args.expected_sha256), sort_keys=True))
