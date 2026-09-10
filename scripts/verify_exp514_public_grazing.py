#!/usr/bin/env python3
"""Compact numerical grazing/event replay, explicitly without raw meshes."""
import argparse
import json
from pathlib import Path
import numpy as np
from butterfly._paired_startup import sha256
from scripts import run_exp514_grazing_candidates as run

SOURCE = 'c1fdf14749a28d5c907b4263c1a9dac935a69c3a'


def shooting(profile, c, p):
    """Separately coded Rössler section-root algebra and bounded iterates."""
    s = profile['shooting']
    if not 1 <= len(s['trace']) <= p['newton_iterations']:
        raise ValueError('public shooting trace length differs')
    u, t = c['seed_u'], c['seed_time']
    _, _, section = run.coverage.fields(c)
    a = c['parameters']['a']
    names = []
    for i, v in enumerate(s['trace']):
        names.append(c['id']+'--'+profile['method']+f'--newton-{i}.npz')
        if v['iteration'] != i or v['u'] != u or v['time'] != t:
            raise ValueError('public Newton sequence differs')
        if not v['solver_success']:
            if i != len(s['trace'])-1 or s['converged'] or s['reason'] != 'integration failed':
                raise ValueError('public failed integration promoted')
            continue
        if v['reached_time'] != t or not c['u_box'][0] <= u <= c['u_box'][1] or not c['time_box'][0] <= t <= c['time_box'][1]:
            raise ValueError('public shooting endpoint outside box')
        x, y, z = v['state']
        vx, vy, vz = v['raw_tangent']
        fx, fy = -y-z, x+a*y
        residual = np.array([y-section.offset, fy])
        matrix = np.array([[vy, fy], [vx+a*vy, fx+a*fy]])
        if (not np.isfinite([*v['state'], *v['raw_tangent'], u, t]).all()
                or not np.allclose(residual, v['residual'], rtol=0, atol=1e-13)
                or not np.allclose(matrix, v['jacobian'], rtol=1e-14, atol=1e-12)):
            raise ValueError('public Rössler grazing algebra differs')
        converged = abs(residual[0]) <= p['root_plane'] and abs(residual[1]) <= p['root_velocity']
        if converged:
            if i != len(s['trace'])-1 or not s['converged'] or s['reason'] != 'residual tolerances':
                raise ValueError('public convergence differs')
        elif 'newton_step' in v:
            step = np.linalg.solve(matrix, residual)
            if not np.allclose(step, v['newton_step'], rtol=1e-12, atol=1e-15):
                raise ValueError('public Newton correction differs')
            u, t = u-v['newton_step'][0], t-v['newton_step'][1]
            outside = not c['u_box'][0] <= u <= c['u_box'][1] or not c['time_box'][0] <= t <= c['time_box'][1] or t <= 0
            if i == len(s['trace'])-1 and (s['converged'] or s['reason'] != ('prospective search box exceeded' if outside else 'iteration limit') or (not outside and i != p['newton_iterations']-1)):
                raise ValueError('public Newton termination differs')
        else:
            try:
                np.linalg.solve(matrix, residual)
            except np.linalg.LinAlgError:
                if i == len(s['trace'])-1 and not s['converged'] and s['reason'] == 'singular Newton matrix':
                    continue
            raise ValueError('public missing Newton correction')
    if names != s['raw_files']:
        raise ValueError('public shooting raw labels differ')
    return len(names)


def verify(path, expected_sha):
    path = Path(path)
    if sha256(path) != expected_sha:
        raise ValueError('public receipt byte identity differs')
    r = json.loads(path.read_bytes())
    p = run.load()
    if (r['experiment_id'] != 'EXP-514' or r['passed'] is not True or r['protocol_compliant'] is not True
            or r['source_commit'] != SOURCE or r['plan_sha256'] != sha256(run.PLAN) or r['inputs'] != run.INPUTS
            or r['paid_review'] != p['paid_review'] or r['new_integrations'] != 0 or r['symbolic_chains_verified'] is not False
            or type(r['target_ivps']) is not int or not 0 < r['target_ivps'] <= p['limits']['target_ivps']
            or type(r['output_bytes_including_summary']) is not int or not 0 < r['output_bytes_including_summary'] <= p['limits']['output_bytes']
            or not 0 <= r['elapsed_seconds'] <= p['limits']['wall_seconds']
            or [row['candidate'] for row in r['rows']] != p['candidates']):
        raise ValueError('public identity/matrix/resource/claim binding differs')
    calls = 0
    for row in r['rows']:
        c = row['candidate']
        if [v['method'] for v in row['roots']] != p['grazing']['solvers']:
            raise ValueError('complete public root pair required')
        for v in row['roots']:
            calls += shooting(v, c, p['grazing'])
        eligible = run.model.boundary.root_pair(row['roots'], c, p['grazing'])['eligible']
        if row['skipped_doses'] != ([] if eligible else c['doses']):
            raise ValueError('public skipped doses differ')
        for s in row['sides']:
            for v in s['profiles']:
                run.previous.public.measurement(v, dict(candidate=c, u=s['u']), p['numerical'])
                calls += len(v['products'])
        decision = run.model.decision(c, row['roots'], row['sides'], p['grazing'])
        if not run.public.equal(decision, row['decision']):
            raise ValueError('public grazing mechanism decision differs')
    if calls != r['target_ivps']:
        raise ValueError('public call accounting differs')
    return dict(experiment_id='EXP-514', passed=True, candidates=len(r['rows']),
        qualified=sum(v['decision']['qualified'] for v in r['rows']), new_integrations=0,
        symbolic_chains_verified=False, full_raw_audit_repeated=False,
        scope='Compact root algebra, event measurements and two-sided mechanism decisions replayed. Raw shooting/dense meshes, analytic control products and actual disk bytes are not audited here.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result', type=Path, required=True)
    p.add_argument('--expected-sha256', required=True)
    a = p.parse_args()
    print(json.dumps(verify(a.result, a.expected_sha256), sort_keys=True))
