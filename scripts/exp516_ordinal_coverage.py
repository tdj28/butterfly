#!/usr/bin/env python3
"""Public, zero-IVP post-result coverage screen across all retained ordinals."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = 'docs/experiments/receipts/EXP-512-censored-return-extension-result.json'
PRIOR_PLAN = 'experiments/manifests/EXP-511-direct-curve-coverage.json'
ANCESTOR = 'docs/experiments/receipts/EXP-486-return-image-fold-result.json'
TRANSPORT = 'scripts/exp510_fold_transport.py'
INPUTS = {
    RECEIPT: 'c89bb30f90bf26a4f4902e349459b234201a66b00d3d2b4a500d6849fdb96e76',
    PRIOR_PLAN: 'c6e22b10ba2d8169dbb5aaeb456cd8e97bb2b79cd23b4d6e0eb451edb5d5080f',
    ANCESTOR: '74fd97ef7c32e56a8c29d32113ab7cfa2531f9a48caf543906beb8cb2b5762d4',
    TRANSPORT: 'e67653ea97bc167559a0d37d5c70e96e48e51660ae952e257c1a37f4ebd8b0a7',
}
SOURCES = ['scripts/exp516_ordinal_coverage.py', 'tests/test_exp516_ordinal_coverage.py',
           'docs/experiments/EXP-516-event-ordinal-coverage.md']
SCALES = [15., 15., .01]
METHODS = ['DOP853', 'Radau']
LIMIT = 16 * 1024**2


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def finite(values):
    if not all(math.isfinite(v) for v in values):
        raise ValueError('finite measurements required')


def distance(a, b):
    if len(a) != 3 or len(b) != 3:
        raise ValueError('complete three-coordinate state required')
    finite([*a, *b])
    return max(abs(x-y)/s for x, y, s in zip(a, b, SCALES, strict=True))


def field(q, parameters):
    x, y, z = q
    return [-y-z, x+parameters['a']*y, parameters['b']+z*(x-parameters['c'])]


def corrected(raw, f):
    finite([*raw, *f])
    if len(raw) != 3 or len(f) != 3 or f[1] == 0:
        raise ValueError('transverse three-dimensional correction required')
    # A determinant-form evaluation, independently of the saved correction.
    return [(raw[0]*f[1]-f[0]*raw[1])/f[1], 0.,
            (raw[2]*f[1]-f[2]*raw[1])/f[1]]


def event(e, parameters, offset, gate, uncertain):
    q, t = e['state'], e['time']
    finite([t, e['angle'], e['residual'], e['normal_velocity'], *q, *e['raw_tangent']])
    f = field(q, parameters)
    angle = abs(f[1])/math.hypot(*f) if math.hypot(*f) else 0.
    if (abs(e['normal_velocity']-f[1]) > 1e-10*max(1., abs(f[1]))
            or abs(e['angle']-angle) > 1e-12 or abs(e['residual']-(q[1]-offset)) > 1e-12
            or e['accepted'] != bool(q[0] < gate and f[1] < 0)):
        raise ValueError('saved event geometry disagrees with field/section')
    good = bool(e['accepted'] and angle >= 1e-7 and abs(q[1]-offset) <= 1e-8
                and not any(v['time'] <= t for v in uncertain))
    v = corrected(e['raw_tangent'], f) if f[1] else None
    gain = math.hypot(*(v[i]/SCALES[i] for i in (0, 2))) if v else None
    fraction = abs(v[0]/15)/gain if gain else 0.
    return dict(time=t, state=q, tangent=v, angle=angle, transverse=good,
                scaled_gain=gain, x_fraction=fraction)


def observations(profile, parameters, offset, gate):
    if profile['status'] != 'completed':
        return dict(status=profile['status'], events=[], pairs=[], last_event=None, horizon=None)
    report = profile['report']
    if report['method'] != profile['method']:
        raise ValueError('method identity differs')
    all_events = report['reconstructed']
    times = [e['time'] for e in all_events]
    if not all(report['guard'] < t <= report['horizon'] for t in times) or any(a >= b for a, b in zip(times, times[1:])):
        raise ValueError('strictly ordered in-horizon census required')
    # Validate rejected crossings too; do not silently trust the acceptance bit.
    checked = [event(e, parameters, offset, gate, report['uncertain_extrema']) for e in all_events]
    events = [v for e, v in zip(all_events, checked, strict=True) if e['accepted']]
    pairs = []
    prefix = True
    for i, e in enumerate(events):
        prefix = prefix and e['transverse']
        if i == 0:
            continue
        before = events[i-1]
        valid = bool(prefix and before['scaled_gain'] is not None and before['scaled_gain'] >= 1e-4
                     and before['x_fraction'] >= .001)
        pairs.append(dict(ordinal=i, input=before, output=e, regular=valid,
            slope=e['tangent'][0]/before['tangent'][0] if valid else None))
    return dict(status='completed', events=events, pairs=pairs,
                last_event=events[-1] if events else None, horizon=report['horizon'])


def compare(profiles, ordinal, targets):
    available = [next((p for p in row['pairs'] if p['ordinal'] == ordinal), None) for row in profiles]
    result = dict(ordinal=ordinal, methods=available, paired_regular=False,
        reason='missing ordinal', state_error=None, time_error=None, tangent_error=None,
        slope_error=None, input_distances=None, output_distances=None, joint_distance=None,
        sampled_reference_coverage=False)
    if any(p is None for p in available):
        return result
    aa, bb = [p['events'][:ordinal+1] for p in profiles]
    se = max(distance(a['state'], b['state']) for a, b in zip(aa, bb, strict=True))
    te = max(abs(a['time']-b['time']) for a, b in zip(aa, bb, strict=True))
    inside, outside = [[[distance(p[k]['state'], t[ref]) for t in targets] for p in available]
                       for k, ref in [('input', 'image_state'), ('output', 'next_state')]]
    joint = max(*[x for r in inside for x in r], *[x for r in outside for x in r])
    regular, ve, slope = False, None, None
    if se <= 1e-6 and te <= 1e-7 and all(p['regular'] for p in available):
        a, b = [p['input'] for p in available]
        ve = max(abs(a['tangent'][i]/SCALES[i]/a['scaled_gain']-
                     b['tangent'][i]/SCALES[i]/b['scaled_gain']) for i in (0, 2))
        slope = abs(available[0]['slope']-available[1]['slope'])
        regular = ve <= 1e-6 and slope <= 1e-6*max(1., *(abs(p['slope']) for p in available))
    return dict(result, paired_regular=regular, reason=None if regular else 'prefix disagreement or irregular input',
        state_error=se, time_error=te, tangent_error=ve, slope_error=slope,
        input_distances=inside, output_distances=outside, joint_distance=joint,
        sampled_reference_coverage=bool(regular and joint <= 1e-6))


def cell(left, right):
    if left['ordinal'] != right['ordinal']:
        raise ValueError('never bridge different ordinals')
    nominated = False
    jumps = None
    if all(p is not None for row in (left, right) for p in row['methods']):
        jumps = [[abs(a[k]['time']-b[k]['time']) for k in ('input', 'output')]
                 for a, b in zip(left['methods'], right['methods'], strict=True)]
    if left['paired_regular'] and right['paired_regular']:
        signs = [math.copysign(1., p['input']['tangent'][0]) for row in (left, right) for p in row['methods']]
        nominated = len(set(signs)) == 1 and all(a['slope']*b['slope'] < 0
            for a, b in zip(left['methods'], right['methods'], strict=True))
    return dict(endpoint_candidate=nominated, endpoint_time_jumps=jumps,
                interior_continuity_certified=False, fold_qualified=False)


def minima(rows, regular_only=False):
    values = [(r['node'], r['comparison']['joint_distance']) for r in rows
              if r['comparison']['joint_distance'] is not None
              and (not regular_only or r['comparison']['paired_regular'])]
    if not values:
        return None
    value = min(v for _, v in values)
    return dict(distance=value, nodes=[i for i, v in values if v == value])


def load_inputs():
    if any(sha(ROOT/n) != h for n, h in INPUTS.items()):
        raise ValueError('fixed public input changed')
    saved, plan, ancestor = [json.loads((ROOT/n).read_bytes()) for n in (RECEIPT, PRIOR_PLAN, ANCESTOR)]
    if saved['experiment_id'] != 'EXP-512' or not saved['passed'] or not saved['protocol_compliant']:
        raise ValueError('audited predecessor required')
    rows, curves = saved['result']['rows'], plan['selection']['curves']
    targets = plan['selection']['targets']
    if len(rows) != 2 or len(curves) != 2 or len(targets) != 4:
        raise ValueError('complete two-direction/four-reference matrix required')
    for row, curve in zip(rows, curves, strict=True):
        if row['candidate'] != curve or len(row['samples']) != 20 or [s['u'] for s in row['samples']] != curve['grid']:
            raise ValueError('complete original grid/candidate required')
        if any([p['method'] for p in s['profiles']] != METHODS for s in row['samples']):
            raise ValueError('complete solver matrix required')
    return saved, plan, ancestor


def analyze(saved, plan, ancestor):
    result = []
    for direction, row in enumerate(saved['result']['rows']):
        c = row['candidate']
        parameters = c['parameters']
        offset = c['initial_state'][1]
        # The legacy small-equilibrium x gate is -a times this section offset.
        gate = -parameters['a']*offset
        original = next(f for f in ancestor['families'] if f['id'] == c['family_id'])
        lineage = dict(original_parameters=original['parameters'], current_parameters=parameters,
            original_anchor=original['initial_state'], current_anchor=c['initial_state'],
            xz_anchor_unchanged=all(original['initial_state'][i] == c['initial_state'][i] for i in (0, 2)),
            initial_tangent_unchanged=original['initial_tangent'] == c['initial_tangent'])
        samples = []
        for i, s in enumerate(row['samples']):
            profiles = [observations(p, parameters, offset, gate) for p in s['profiles']]
            count = max((len(p['pairs']) for p in profiles), default=0)
            samples.append(dict(node=i, u=s['u'], profiles=profiles,
                comparisons=[compare(profiles, j, plan['selection']['targets']) for j in range(1, count+1)]))
        ordinals = []
        for ordinal in range(1, max(len(s['comparisons']) for s in samples)+1):
            data = [dict(node=s['node'], comparison=next((r for r in s['comparisons'] if r['ordinal'] == ordinal),
                compare(s['profiles'], ordinal, plan['selection']['targets']))) for s in samples]
            cells = [dict(nodes=[a['node'], b['node']], **cell(a['comparison'], b['comparison']))
                     for a, b in zip(data, data[1:])]
            ordinals.append(dict(ordinal=ordinal, nodes=data, cells=cells,
                nearest_any=minima(data), nearest_regular=minima(data, True),
                sampled_coverage_nodes=[r['node'] for r in data if r['comparison']['sampled_reference_coverage']]))
        result.append(dict(direction=direction, family_id=c['family_id'], lineage=lineage,
                           samples=samples, ordinals=ordinals))
    return dict(experiment_id='EXP-516', status='post-result-saved-data-diagnostic', inputs=INPUTS,
        rows=result, references=plan['selection']['targets'], new_integrations=0, paid_calls=0,
        historical_decisions_changed=False, symbolic_chains_verified=False,
        full_raw_audit_repeated=False, global_root_absence_proved=False,
        scope='Every saved consecutive accepted pair; endpoint-only candidates, no certified interiors or new folds.')


def encode(value):
    data = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n').encode()
    if len(data) > LIMIT:
        raise ValueError('16-MiB result cap exceeded before write')
    return data


def verify(path, expected_sha=None):
    if expected_sha is not None and sha(path) != expected_sha:
        raise ValueError('published receipt hash differs')
    saved, plan, ancestor = load_inputs()
    value = json.loads(path.read_bytes())
    if value['analysis'] != analyze(saved, plan, ancestor):
        raise ValueError('complete saved-data replay differs')
    if set(value['sources']) != set(SOURCES) or any(sha(ROOT/n) != h for n, h in value['sources'].items()):
        raise ValueError('bound analysis source changed')
    return dict(passed=True, new_integrations=0, full_raw_audit_repeated=False,
                receipt_sha256=sha(path), directions=len(value['analysis']['rows']))


def execute(output, commit, remote):
    saved, plan, ancestor = load_inputs()
    git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
    if git('rev-parse', 'HEAD') != commit or git('status', '--porcelain', '--untracked-files=normal'):
        raise ValueError('exact clean source required')
    lines = git('ls-remote', 'origin', 'refs/heads/'+remote).splitlines()
    if len(lines) != 1 or lines[0].split()[0] != commit:
        raise ValueError('live remote source differs')
    if output.exists():
        raise ValueError('fresh output required')
    marker = ROOT/'artifacts/EXP-516/target-once.json'
    marker.parent.mkdir(parents=True, exist_ok=True)
    binding = dict(source_commit=commit, remote_ref=remote, inputs=INPUTS,
        sources={n: sha(ROOT/n) for n in SOURCES}, started_utc=datetime.now(timezone.utc).isoformat(),
        output=str(output.resolve().relative_to(ROOT)))
    with marker.open('xb') as stream:
        stream.write(encode(binding))
    output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    def timeout(*_):
        raise TimeoutError('120-second saved-data budget')
    old = signal.signal(signal.SIGALRM, timeout)
    signal.alarm(120)
    try:
        analysis = analyze(saved, plan, ancestor)
        value = dict(binding, analysis=analysis, elapsed_seconds=time.monotonic()-start)
        data = encode(value)
        with (output/'result.json').open('xb') as stream:
            stream.write(data)
    except BaseException as exc:
        with (output/'failure.json').open('xb') as stream:
            stream.write(encode(dict(binding, exception=type(exc).__name__, message=str(exc))))
        raise
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)
    return verify(output/'result.json')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--verify', type=Path)
    p.add_argument('--expected-sha256')
    p.add_argument('--output-dir', type=Path)
    p.add_argument('--source-commit')
    p.add_argument('--remote-ref')
    args = p.parse_args()
    if args.verify:
        if args.output_dir or args.source_commit or args.remote_ref:
            p.error('verification cannot also execute')
        if not args.expected_sha256:
            p.error('public verification requires the published receipt SHA-256')
        result = verify(args.verify, args.expected_sha256)
    elif args.output_dir:
        if not args.source_commit or not args.remote_ref:
            p.error('execution requires source commit and remote ref')
        result = execute(args.output_dir, args.source_commit, args.remote_ref)
    else:
        if args.source_commit or args.remote_ref or args.expected_sha256:
            p.error('source binding requires execution')
        load_inputs()
        result = dict(valid=True, new_integrations=0, directions=2, profiles=80)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
