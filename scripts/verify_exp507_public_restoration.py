#!/usr/bin/env python3
"""Public comparison replay; full retained meshes remain a separate local audit."""
import argparse
import json
from pathlib import Path

from butterfly._paired_startup import sha256
from scripts import run_exp507_fold_restoration as run
from scripts import audit_exp507_fold_restoration as raw

SOURCE = 'dd1d18eb96f8fabdaff4bb44e9fc9f6a68b6ca49'
equal = run.public.equal


def verify(path, expected_sha):
    if sha256(path) != expected_sha:
        raise ValueError('public receipt byte identity differs')
    saved = json.loads(Path(path).read_bytes())
    p,numerical,before = run.load(),run.prior.base.load(),run.inputs()
    run.public.verify(run.ROOT/run.RECEIPT,run.INPUTS[run.RECEIPT])
    if (saved['experiment_id'] != 'EXP-507' or saved['passed'] is not True
            or saved['protocol_compliant'] is not True or saved['source_commit'] != SOURCE
            or saved['plan_sha256'] != sha256(run.PLAN) or saved['audit_source_sha256'] != sha256(Path(raw.__file__))
            or saved['inputs'] != run.INPUTS or saved['ledger'] != numerical['ledger']
            or saved['paid_review'] != p['paid_review'] or saved['symbolic_chains_verified'] is not False
            or saved['new_integrations'] != 0 or not equal(saved['proposal'],p['proposal'])
            or type(saved['output_bytes_including_summary']) is not int
            or not 0 < saved['output_bytes_including_summary'] <= p['limits']['output_bytes']
            or saved['output_limit_bytes'] != p['limits']['output_bytes']):
        raise ValueError('public study, source, resource or claim binding differs')
    point = saved['point']
    if point['spec'] != saved['proposal']['spec']:
        raise ValueError('sole frozen parameter proposal differs')
    count = dict(id=point['spec']['id'],point_sha256=saved['point_sha256'],
        target_ivps=saved['target_ivps'],inherited_archive_products=saved['inherited_archive_products'])
    run.public.check_point(point,run.prior.model.warm_plan(numerical,before),count)
    decision = run.model.decide(numerical,before,point,saved['proposal'])
    if not equal(decision,saved['decision']) or not 0 < saved['target_ivps'] <= p['limits']['target_ivps']:
        raise ValueError('public decision or IVP count differs')
    return dict(experiment_id='EXP-507',passed=True,decision=decision,target_ivps=saved['target_ivps'],
        full_raw_audit_repeated=False,new_integrations=0,symbolic_chains_verified=False,
        scope='Compact comparisons replayed; raw hashes, meshes and total on-disk bytes are not independently remeasured here.',
        floating_replay_tolerance=dict(rtol=1e-12,atol=1e-13,discrete_gates='exact'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result',type=Path,required=True)
    parser.add_argument('--expected-sha256',required=True)
    a = parser.parse_args()
    result = verify(a.result,a.expected_sha256)
    result['decision'] = {k:v for k,v in result['decision'].items()
        if k not in ('variant_changes','original_correspondence')}
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__':
    main()
