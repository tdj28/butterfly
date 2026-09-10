#!/usr/bin/env python3
"""Replay every coefficient, root certificate and EXP-515 decision without IVPs."""
import argparse
from decimal import Decimal as D, localcontext
import json
from pathlib import Path

from butterfly.decimal_taylor import exact, load_stream
from butterfly._paired_startup import inventory, sha256
from butterfly.bounded_json import directory_bytes
from scripts import run_exp515_third_return_precision as run


def check_raw(raw, case, config):
    if (raw['initial'] != case['initial'] or raw['field'] != case['field']
            or raw['horizon'] != case['horizon'] or raw['config'] != config
            or raw['rigorous_enclosure'] is not False):
        raise ValueError('raw input/configuration binding differs')
    field = case['field']
    with localcontext() as ctx:
        ctx.prec = config['digits']+16
        eps = D(10)**(-config['digits']+8)
        def close(a, b):
            return a.is_finite() and b.is_finite() and abs(a-b) <= eps*max(D(1), abs(a), abs(b))
        previous, t, end = list(map(D, case['initial'])), D(0), D(case['horizon'])
        maxima = [D(0), D(0)]
        for row in raw['steps']:
            q = [list(map(D, p)) for p in row['coefficients']]
            h = D(row['step'])
            if (len(q) != 6 or any(len(p) != config['order']+1 for p in q)
                    or not all(v.is_finite() for p in q for v in p)
                    or not close(D(row['time']), t) or not close(h, min(D(config['step']), end-t))
                    or h <= 0 or not all(close(p[0], v) for p, v in zip(q, previous, strict=True))):
                raise ValueError('raw coefficient mesh/continuity differs')
            for n in range(config['order']):
                for axis in range(6):
                    terms = [exact(field['constant'][axis]) if n == 0 else D(0)]
                    terms += [exact(v)*q[j][n] for i, j, v in field['linear'] if i == axis]
                    for i, j, k, v in field['quadratic']:
                        if i == axis:
                            terms.extend(exact(v)*q[j][r]*q[k][n-r] for r in range(n+1))
                    if not close(q[axis][n+1]*(n+1), sum(terms)):
                        raise ValueError('independent scalar coefficient recurrence differs')
            powers = [h**n for n in range(config['order']+1)]
            previous = [sum(v*w for v, w in zip(p, powers, strict=True)) for p in q]
            if any(abs(v) > (D('1e4') if i < 3 else D('1e12')) for i, v in enumerate(previous)):
                raise ValueError('raw state/tangent magnitude guard')
            for block, cap in enumerate((D('1e-20'), D('1e-16'))):
                tail = max(sum(abs(q[i][n]*powers[n]) for n in range(config['order']-2, config['order']+1))
                           /exact(run.numeric.SCALES[i % 3]) for i in range(3*block, 3*block+3))
                if tail > cap:
                    raise ValueError('raw tail guard failed')
                maxima[block] = max(maxima[block], tail)
            t = D(row['time'])+h
        if (not raw['steps'] or not close(t, end)
                or not all(close(a, D(b)) for a, b in zip(previous, raw['final'], strict=True))
                or not all(close(a, D(b)) for a, b in zip(maxima, raw['maximum_tails'], strict=True))):
            raise ValueError('raw endpoint/tail completion differs')


def profile(output, case, config, saved):
    label = case['id']+'--'+config['name']
    if saved['raw_path'] != label+'.json.gz' or saved['certificate_path'] != label+'-certificates.json':
        raise ValueError('raw/certificate identity differs')
    header, raw = load_stream(output/saved['raw_path'])
    if header != dict(initial=case['initial'], field=case['field'], horizon=case['horizon'], config=config):
        raise ValueError('archive header differs')
    check_raw(raw, case, config)
    certificates = json.loads((output/saved['certificate_path']).read_bytes())
    rebuilt, _ = run.model.analyze(raw, case['section'], certificate=certificates)
    rebuilt.update(raw_path=saved['raw_path'], certificate_path=saved['certificate_path'])
    if rebuilt != saved or json.loads((output/(label+'-result.json')).read_bytes()) != saved:
        raise ValueError('full polynomial certificate/measurement replay differs')
    # Separate determinant-form event correction; do not reuse v-f*tau here.
    with localcontext() as ctx:
        ctx.prec = 70
        for m in saved['measures']:
            if not m['qualified']:
                continue
            f, w = [list(map(D, m[k])) for k in ('field', 'raw_tangent')]
            reference = [(w[j]*f[1]-f[j]*w[1])/f[1] for j in range(3)]
            if any(abs(a-D(b)) > D('1e-60')*max(D(1), abs(a))
                   for a, b in zip(reference, m['corrected'], strict=True)):
                raise ValueError('independent determinant projection differs')
    start = json.loads((output/(label+'-started.json')).read_bytes())
    if start['id'] != case['id'] or start['configuration'] != config['name']:
        raise ValueError('profile start identity differs')
    return [label+s for s in ('.json.gz', '-certificates.json', '-result.json', '-started.json')]


def check_controls(output, saved, p):
    if (saved['passed'] is not True or saved['control_ivps'] != 12 or len(saved['rows']) != 12
            or saved['files'] != inventory(output, omit=('controls.json',))
            or json.loads((output/'controls.json').read_bytes()) != saved
            or directory_bytes(output) > p['controls']['output_bytes']):
        raise ValueError('complete analytic controls/inventory required')
    expected = [(k, c) for k in run.KINDS for c in p['configurations']]
    names = set()
    for row, (kind, config) in zip(saved['rows'], expected, strict=True):
        if row['kind'] != kind:
            raise ValueError('analytic case order differs')
        case = run.control_case(kind)
        names.update(profile(output, case, config, row['profile']))
        if run.control_identity(case, row['profile']) != row['identity']:
            raise ValueError('analytic identity receipt differs')
    if names != set(saved['files']):
        raise ValueError('unexpected or omitted control artifacts')


def audit(output, expected_sha):
    p = run.load()
    output = Path(output)
    if sha256(output/'summary.json') != expected_sha:
        raise ValueError('summary digest differs')
    saved = json.loads((output/'summary.json').read_bytes())
    b = saved['binding']
    if (saved['experiment_id'] != 'EXP-515' or saved['status'] != 'completed'
            or saved['files'] != inventory(output, omit=('summary.json',))
            or b['plan_sha256'] != sha256(run.PLAN) or b['inputs'] != run.INPUTS
            or b['sources'] != {n: sha256(run.ROOT/n) for n in p['source_paths']}
            or b['paid_review'] != p['paid_review']
            or b['initial_free_bytes'] < p['limits']['initial_free_bytes']
            or json.loads((output/'binding.json').read_bytes()) != b
            or saved['target_ivps'] != 12 or len(saved['rows']) != 6
            or not 0 < saved['elapsed_seconds'] <= p['limits']['wall_seconds']
            or directory_bytes(output) > p['limits']['output_bytes']
            or saved['symbolic_chains_verified'] is not False
            or saved['historical_decisions_changed'] is not False):
        raise ValueError('complete source/input/resource/claim binding differs')
    marker = run.ROOT/'artifacts/EXP-515/target-once.json'
    if sha256(marker) != saved['marker_sha256'] or json.loads(marker.read_bytes()) != b:
        raise ValueError('consumed attempt marker differs')
    isolated = json.loads((output/'startup.json').read_bytes())
    if (isolated['passed'] is not True or isolated['isolated'] is not True or isolated['new_integrations'] != 0
            or isolated['sources'] != dict(b['sources'], **run.INPUTS)):
        raise ValueError('isolated startup binding differs')
    control = json.loads((output/'controls.json').read_bytes())
    check_controls(run.ROOT/'artifacts/EXP-515'/('execution-controls-'+b['source_commit'][:7]), control, p)
    names, progress = {'binding.json', 'startup.json', 'controls.json'}, []
    for case, row in zip(p['cases'], saved['rows'], strict=True):
        if row['id'] != case['id'] or len(row['profiles']) != 2:
            raise ValueError('complete target case matrix required')
        for config, result in zip(p['configurations'], row['profiles'], strict=True):
            products = profile(output, case, config, result)
            names.update(products)
            start = json.loads((output/products[-1]).read_bytes())
            if not b['started_utc'] <= start['utc'] <= saved['completed_utc']:
                raise ValueError('target timing outside bound execution')
            progress.append(dict(id=case['id'], configuration=config['name'], status='completed'))
        if (run.model.compare(row['profiles'], case['historical']) != row['comparison']
                or json.loads((output/(case['id']+'.json')).read_bytes()) != row):
            raise ValueError('complete target comparison differs')
        names.add(case['id']+'.json')
    if names != set(saved['files']) or progress != saved['progress']:
        raise ValueError('full target artifact/progress matrix differs')
    return dict(experiment_id='EXP-515', passed=True, protocol_compliant=True,
        source_commit=b['source_commit'], plan_sha256=b['plan_sha256'], inputs=run.INPUTS,
        summary_sha256=expected_sha, target_ivps=12, control_ivps=12, rows=saved['rows'],
        controls=control['rows'], output_bytes_including_summary=directory_bytes(output),
        full_local_raw_audit=True, independent_team_replication=False,
        symbolic_chains_verified=False, historical_decisions_changed=False, new_integrations=0,
        paid_review=p['paid_review'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    result = audit(a.output_dir, a.expected_sha256)
    run.write(a.output.parent, a.output, result,
        dict(output_bytes=directory_bytes(a.output.parent)+16*1024**2, minimum_free_bytes=8*1024**3, failure_reserve_bytes=0))
    print(json.dumps(dict(passed=True, target_ivps=12, sha256=sha256(a.output))))
