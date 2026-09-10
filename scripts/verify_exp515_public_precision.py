#!/usr/bin/env python3
"""Public event algebra and decision replay; does not repeat raw mesh audits."""
import argparse
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import json
from pathlib import Path

from butterfly._paired_startup import sha256
from scripts import run_exp515_third_return_precision as run

SOURCE = 'bee18f1cf6f19f0b908521ba99a314349fc9bc59'


def measurement(profile, case, config):
    label = case['id']+'--'+config['name']
    if (profile['configuration'] != config['name'] or profile['raw_path'] != label+'.json.gz'
            or profile['certificate_path'] != label+'-certificates.json'
            or profile['rigorous_ode_enclosure'] is not False):
        raise ValueError('public profile identity differs')
    report = profile['census']
    if report['polynomial_census_only'] is not True or report['segments'] != int(D(case['horizon'])/D(config['step'])):
        raise ValueError('public census scope/domain differs')
    complete = not report['unresolved'] and not report['join_failures'] and all(e['classification_qualified'] for e in report['events'])
    if report['complete'] != complete:
        raise ValueError('public census completion differs')
    accepted = [e for e in report['events'] if e['accepted']]
    if len(accepted) != len(profile['measures']):
        raise ValueError('public accepted event/measurement matrix differs')
    with localcontext() as ctx:
        ctx.prec = 70
        def close(a, b):
            a, b = D(a), D(b)
            return a.is_finite() and b.is_finite() and abs(a-b) <= D('1e-55')*max(D(1), abs(a), abs(b))
        for e in report['events']:
            box = [F(v) for v in e['time_box']]
            if not 0 <= box[0] <= box[1] <= F(case['horizon']) or box[1]-box[0] > F('1e-25'):
                raise ValueError('public event time box differs')
            expected_time = (D((box[0]+box[1]).numerator)/D((box[0]+box[1]).denominator))/2
            if not close(e['time'], expected_time):
                raise ValueError('public event midpoint differs')
            accept = (e['classification_qualified'] and e['direction'] == -1
                      and e['half_plane'] == 'inside' and e['time_class'] == 'after')
            if e['accepted'] != accept:
                raise ValueError('public event acceptance differs')
        for m, e in zip(profile['measures'], accepted, strict=True):
            if not m['qualified']:
                if m != dict(qualified=False, reason='normal velocity interval includes zero'):
                    raise ValueError('public unresolved projection differs')
                continue
            if (m['time'] != e['time'] or m['time_box'] != e['time_box'] or m['state'] != e['state']
                    or m['rigorous_ode_enclosure'] is not False):
                raise ValueError('public corrected event identity differs')
            q, w = [list(map(D, m[k])) for k in ('state', 'raw_tangent')]
            field = case['field']
            f = [D(field['constant'][i]) for i in range(3)]
            for i, j, v in field['linear']:
                if i < 3:
                    f[i] += D(v)*q[j]
            for i, j, k, v in field['quadratic']:
                if i < 3:
                    f[i] += D(v)*q[j]*q[k]
            if not all(close(a, b) for a, b in zip(f, m['field'], strict=True)) or f[1] == 0:
                raise ValueError('public vector field differs')
            corrected = [(w[i]*f[1]-f[i]*w[1])/f[1] for i in range(3)]
            if not all(close(a, b) for a, b in zip(corrected, m['corrected'], strict=True)):
                raise ValueError('public determinant correction differs')
            norm = run.model.norm(m['corrected'])
            bounds = [[D(v) for v in r] for r in m['corrected_intervals']]
            if any(not a <= D(v) <= b for (a, b), v in zip(bounds, m['corrected'], strict=True)):
                raise ValueError('public corrected interval excludes midpoint')
            radius = run.model.norm([max(abs(D(v)-a), abs(D(v)-b)) for (a, b), v in zip(bounds, m['corrected'], strict=True)])
            condition = (run.model.norm(w)+run.model.norm([v*w[1]/f[1] for v in f]))/norm if norm else None
            checks = [(norm, m['scaled_norm']), (radius, m['root_box_radius'])]
            if norm:
                checks += [(radius/norm, m['box_relative_radius']), (condition, m['subtraction_condition'])]
            elif m['box_relative_radius'] is not None or m['subtraction_condition'] is not None:
                raise ValueError('public exact-zero resolution differs')
            if not all(close(a, b) for a, b in checks):
                raise ValueError('public norm/uncertainty algebra differs')


def verify(path, expected_sha):
    path = Path(path)
    if sha256(path) != expected_sha:
        raise ValueError('public receipt digest differs')
    r = json.loads(path.read_bytes())
    p = run.load()
    if (r['experiment_id'] != 'EXP-515' or r['passed'] is not True or r['protocol_compliant'] is not True
            or r['source_commit'] != SOURCE or r['plan_sha256'] != sha256(run.PLAN) or r['inputs'] != run.INPUTS
            or r['target_ivps'] != 12 or type(r['target_ivps']) is not int or r['control_ivps'] != 12
            or r['new_integrations'] != 0 or r['paid_review'] != p['paid_review']
            or r['symbolic_chains_verified'] is not False or r['historical_decisions_changed'] is not False
            or r['full_local_raw_audit'] is not True or r['independent_team_replication'] is not False
            or type(r['output_bytes_including_summary']) is not int
            or not 0 < r['output_bytes_including_summary'] <= p['limits']['output_bytes']
            or [row['id'] for row in r['rows']] != [c['id'] for c in p['cases']]):
        raise ValueError('public identity/resource/claim matrix differs')
    resolved, failed, failures = 0, 0, set()
    for case, row in zip(p['cases'], r['rows'], strict=True):
        if len(row['profiles']) != 2:
            raise ValueError('public precision pair missing')
        for profile, config in zip(row['profiles'], p['configurations'], strict=True):
            measurement(profile, case, config)
        comparison = run.model.compare(row['profiles'], case['historical'])
        if comparison != row['comparison']:
            raise ValueError('public full comparison differs')
        resolved += sum(v['resolved'] for v in comparison['ordinals'])
        for h in comparison['historical']:
            for v in h['comparisons']:
                if h['interpretable'] and not v['comparison']['within_one_percent']:
                    failed += 1
                    failures.add((case['id'], h['method'], v['ordinal']))
    expected = [(k, c) for k in run.KINDS for c in p['configurations']]
    if len(r['controls']) != 12:
        raise ValueError('public analytic control matrix missing')
    for row, (kind, config) in zip(r['controls'], expected, strict=True):
        case = run.control_case(kind)
        if row['kind'] != kind:
            raise ValueError('public analytic control order differs')
        measurement(row['profile'], case, config)
        if run.control_identity(case, row['profile']) != row['identity']:
            raise ValueError('public analytic control identity differs')
    return dict(experiment_id='EXP-515', passed=True, cases=6, resolved_return_comparisons=resolved,
        failed_historical_comparisons=failed, distinct_failed_historical_vectors=len(failures),
        new_integrations=0, full_raw_audit_repeated=False, symbolic_chains_verified=False,
        scope='Public scalar event algebra and complete comparison decisions only. No raw coefficient/certificate replay, control raw audit, actual storage audit, or rigorous ODE enclosure.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result', type=Path, required=True)
    p.add_argument('--expected-sha256', required=True)
    a = p.parse_args()
    print(json.dumps(verify(a.result, a.expected_sha256), sort_keys=True))
