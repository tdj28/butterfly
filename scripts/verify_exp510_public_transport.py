#!/usr/bin/env python3
"""Public fold-transport comparison replay, without the local raw meshes."""
import argparse
import json
from pathlib import Path
from butterfly._paired_startup import sha256
from scripts import run_exp510_fold_transport as run
from scripts import audit_exp510_fold_transport as raw

SOURCE = '0e11f95e352364afcb0be43a2e39a1d12ffaf9b5'
equal = run.public.compact.equal


def verify(path,expected_sha):
    if sha256(path) != expected_sha:
        raise ValueError('public transport receipt byte identity differs')
    saved = json.loads(Path(path).read_bytes())
    p = run.load()
    if (saved['experiment_id'] != 'EXP-510' or saved['passed'] is not True
            or saved['protocol_compliant'] is not True or saved['source_commit'] != SOURCE
            or saved['plan_sha256'] != sha256(run.PLAN) or saved['inputs'] != run.INPUTS
            or saved['paid_review'] != p['paid_review'] or saved['new_integrations'] != 0
            or saved['symbolic_chains_verified'] is not False or saved['ledger'] != run.base.load()['ledger']
            or type(saved['target_ivps']) is not int or not 0 < saved['target_ivps'] <= p['limits']['target_ivps']
            or type(saved['output_bytes_including_summary']) is not int
            or not 0 < saved['output_bytes_including_summary'] <= p['limits']['output_bytes']
            or saved['output_limit_bytes'] != p['limits']['output_bytes']):
        raise ValueError('public study, source, resource or claim binding differs')
    run.public.verify(run.ROOT/run.RECEIPT,run.INPUTS[run.RECEIPT])
    seen = []
    previous = run.prior.old.inputs()['folds']
    def measure(spec,candidates):
        nonlocal previous
        i = len(seen)
        if i >= len(saved['result']['rows']):
            raise ValueError('required substep missing')
        item = saved['result']['rows'][i]
        rows = item['folds']
        if item['spec'] != spec or len(rows) != 4:
            raise ValueError('complete fixed substep matrix required')
        for candidate,row in zip(candidates,rows,strict=True):
            profiles = [dict(method=v['method'],qualification={k:x for k,x in v.items() if k != 'method'})
                for v in row['solvers']]
            rebuilt = dict(run.base.compare(candidate,profiles,run.base.load()['fold']),parent_id=candidate['parent_id'])
            if not equal(row,rebuilt):
                raise ValueError('public fold qualification differs')
        scalar = raw.scalar_assess(previous,rows,run.base.load()['fold']['scales'])
        if scalar is not None and scalar['passed'] != item['decision']['transport_qualified']:
            raise ValueError('scalar branch identity decision differs')
        previous = rows
        seen.append(spec['id'])
        return rows
    result = run.model.follow(run.base.load(),run.prior.old.inputs(),run.inputs()['spec']['parameters'],run.offset,measure)
    endpoint = run.endpoint(result)
    counts = saved['counts']
    if (not equal(result,saved['result']) or not equal(endpoint,saved['endpoint_comparison'])
            or len(seen) != len(saved['result']['rows']) or [c['id'] for c in counts] != seen
            or any(type(c['target_ivps']) is not int or type(c['inherited_archive_products']) is not int
                or not 0 < c['inherited_archive_products'] <= c['target_ivps'] for c in counts)
            or sum(c['target_ivps'] for c in counts) != saved['target_ivps']):
        raise ValueError('complete transport, endpoint or counts differ')
    if endpoint is not None and not equal(raw.point_audit.old.scalar_contact(result['rows'][-1]['folds'],run.inputs()['cycle']),endpoint['contact']):
        raise ValueError('scalar endpoint distances differ')
    return dict(experiment_id='EXP-510',passed=True,transport_completed=result['transport_completed'],
        executed_substeps=len(seen),endpoint_fold_proximity=None if endpoint is None else endpoint['fold_proximity'],
        full_raw_audit_repeated=False,new_integrations=0,symbolic_chains_verified=False,
        scope='Compact fold/branch/endpoint comparisons replayed; raw meshes, IVP count and on-disk bytes are not independently remeasured here.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result',type=Path,required=True)
    parser.add_argument('--expected-sha256',required=True)
    a = parser.parse_args()
    print(json.dumps(verify(a.result,a.expected_sha256),sort_keys=True))


if __name__ == '__main__':
    main()
