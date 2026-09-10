#!/usr/bin/env python3
"""Replay all five grazing searches, raw side polynomials and decisions."""
import argparse
import json
from pathlib import Path
from butterfly._paired_startup import inventory, sha256
from butterfly.bounded_json import directory_bytes, write_bounded_json
from scripts import run_exp514_grazing_candidates as run
from scripts import audit_exp492_event_boundaries as grazing_audit
from scripts import audit_exp511_curve_coverage as dense_audit


def read(path):
    return json.loads(path.read_bytes())


def audit(output, expected_sha):
    p = run.load()
    if sha256(output/'summary.json') != expected_sha:
        raise ValueError('summary byte identity differs')
    saved, b = read(output/'summary.json'), read(output/'binding.json')
    if (saved['experiment_id'] != 'EXP-514' or saved['status'] != 'completed' or saved['binding'] != b
            or b['sources'] != {n: sha256(run.ROOT/n) for n in p['source_paths']}
            or b['inputs'] != run.INPUTS or b['plan_sha256'] != sha256(run.PLAN)
            or b['paid_review'] != p['paid_review'] or saved['symbolic_chains_verified'] is not False
            or b['initial_free_bytes'] < p['limits']['initial_free_bytes']
            or saved['files'] != inventory(output, omit=('summary.json',))
            or not b['started_utc'] <= saved['completed_utc']
            or not 0 <= saved['elapsed_seconds'] <= p['limits']['wall_seconds']):
        raise ValueError('source/input/inventory/resource binding differs')
    marker = run.ROOT/'artifacts/EXP-514/target-once.json'
    if sha256(marker) != saved['marker_sha256'] or read(marker) != b:
        raise ValueError('consumed marker differs')
    startup = read(output/'startup.json')
    if (startup['passed'] is not True or startup['isolated'] is not True or startup['new_integrations'] != 0
            or startup['sources'] != {n: sha256(run.ROOT/n) for n in set(p['source_paths']) | set(run.INPUTS)}
            or json.loads(startup['stdout']) != dict(valid=True, new_integrations=0, candidates=5, maximum_target_ivps=160)):
        raise ValueError('isolated startup differs')
    controls = read(output/'controls.json')
    control_dir = run.ROOT/'artifacts/EXP-514'/('execution-controls-'+b['source_commit'][:7])
    if (controls != read(control_dir/'controls.json') or controls['passed'] is not True
            or controls['files'] != inventory(control_dir, omit=('controls.json',))
            or controls['dense_control_replay'] != run.previous.previous.controls()
            or directory_bytes(control_dir) > p['controls']['output_bytes']):
        raise ValueError('analytic control identity differs')
    specs = [dict(c, count=2) for c in (run.old.control_specs()[0], run.old.control_specs()[3])]
    if [r['candidate'] for r in controls['rows']] != specs:
        raise ValueError('complete analytic matrix required')
    control_calls = 0
    for c, r in zip(specs, controls['rows'], strict=True):
        rhs, jac = run.old.fields_for_control(c)
        section = run.PoincareSection((0., 1., 0.), 0., -1)
        for root in r['roots']:
            trace = root['shooting']['trace']
            control_calls += len(trace)
            if len(trace) != len(root['shooting']['raw_files']):
                raise ValueError('analytic shooting matrix differs')
            for v, name in zip(trace, root['shooting']['raw_files'], strict=True):
                raw = dense_audit.raw(control_dir/name)
                initial = run.base.np.r_[run.base.np.asarray(c['initial_state'])+v['u']*run.base.np.asarray(c['initial_tangent']), c['initial_tangent']]
                if (not run.base.np.array_equal(raw['integration_augmented_states'][0], initial)
                        or not run.base.np.array_equal(raw['integration_augmented_states'][-1], v['state']+v['raw_tangent'])
                        or raw['integration_times'][-1] != v['time']):
                    raise ValueError('analytic shooting raw endpoints differ')
                # For this polynomial h=(t-1)^2 + initial_x, h_t=2(t-1).
                exact = [(v['time']-1.)**2+2e-5+2*v['u'] if c['kind']=='grazing'
                         else (v['time']-1.)**2+.1+2*v['u'], 2*(v['time']-1.)]
                if not run.base.np.allclose(v['residual'], exact, rtol=0, atol=1e-10):
                    raise ValueError('analytic grazing residual differs')
        for i, side in enumerate(r['sides']):
            for profile in side['profiles']:
                label = c['id']+f'--side-{i}--'+profile['method']
                _, paths = dense_audit.check_profile(control_dir, label, profile, c, side['u'], p['numerical'], rhs, section)
                control_calls += len(paths)
        if run.model.decision(c, r['roots'], r['sides'], p['grazing']) != r['decision'] or r['decision']['qualified'] != (c['kind']=='grazing'):
            raise ValueError('analytic mechanism decision differs')
    if control_calls != controls['control_ivps'] or control_calls > p['controls']['maximum_ivps']:
        raise ValueError('analytic call accounting differs')
    names, calls, rows = {'binding.json', 'startup.json', 'controls.json'}, 0, []
    for c in p['candidates']:
        row = read(output/(c['id']+'.json'))
        if row['candidate'] != c or [r['method'] for r in row['roots']] != p['grazing']['solvers']:
            raise ValueError('candidate/solver matrix differs')
        rhs, _, section = run.coverage.fields(c)
        def check_start(label, expected):
            start = read(output/(label+'-started.json'))
            if {k: v for k, v in start.items() if k != 'started_utc'} != expected or not b['started_utc'] <= start['started_utc'] <= saved['completed_utc']:
                raise ValueError('profile start differs')
            names.add(label+'-started.json')
        for r in row['roots']:
            label = c['id']+'--'+r['method']
            check_start(label, dict(candidate=c, method=r['method'], phase='shooting'))
            if read(output/(label+'.json')) != r['shooting']:
                raise ValueError('shooting profile differs')
            paths = grazing_audit.check_shooting(output, r, c, p['grazing'], r['method'])
            names.update(paths | {label+'.json'})
            calls += len(paths)
        pair = run.model.boundary.root_pair(row['roots'], c, p['grazing'])
        if row['skipped_doses'] != ([] if pair['eligible'] else c['doses']):
            raise ValueError('skipped doses differ')
        for i, side in enumerate(row['sides']):
            if [v['method'] for v in side['profiles']] != p['grazing']['solvers']:
                raise ValueError('side solver matrix differs')
            for profile in side['profiles']:
                label = c['id']+f'--side-{i}--'+profile['method']
                check_start(label, dict(candidate=c, method=profile['method'], phase='side', u=side['u']))
                if read(output/(label+'.json')) != profile:
                    raise ValueError('side profile differs')
                _, paths = dense_audit.check_profile(output, label, profile, c, side['u'], p['numerical'], rhs, section)
                names.update(paths | {label+'.json'})
                calls += len(paths)
        if not run.public.equal(run.model.decision(c, row['roots'], row['sides'], p['grazing']), row['decision']):
            raise ValueError('grazing mechanism decision differs')
        names.add(c['id']+'.json')
        rows.append(row)
    size = directory_bytes(output)
    if (not run.public.equal(rows, saved['rows']) or names != set(saved['files'])
            or saved['progress'] != [dict(id=c['id'], status='completed') for c in p['candidates']]
            or calls != saved['target_ivps'] or calls > p['limits']['target_ivps'] or size > p['limits']['output_bytes']):
        raise ValueError('complete decisions/accounting differ')
    return dict(experiment_id='EXP-514', passed=True, protocol_compliant=True,
        source_commit=b['source_commit'], plan_sha256=sha256(run.PLAN), summary_sha256=expected_sha,
        inputs=run.INPUTS, rows=rows, target_ivps=calls, output_bytes_including_summary=size,
        control_ivps=control_calls, elapsed_seconds=saved['elapsed_seconds'],
        new_integrations=0, symbolic_chains_verified=False, paid_review=p['paid_review'],
        scope='Full local target shooting mesh/independent Rössler algebra and side dense/guard/event replay; analytic controls replayed. Historical compact inputs reused. Same-agent numerical audit, not independent-team replication or exact-flow proof.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    result = audit(a.run, a.expected_sha256)
    write_bounded_json(a.output.parent, a.output, result, limit_bytes=directory_bytes(a.output.parent)+32*1024**2)
    print(json.dumps(dict(passed=True, target_ivps=result['target_ivps'],
        qualified=sum(r['decision']['qualified'] for r in result['rows']), audit_sha256=sha256(a.output))))
