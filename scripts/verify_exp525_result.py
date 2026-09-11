#!/usr/bin/env python3
"""Post-run authentication of private EXP-525 evidence; never executes new IVPs."""
import argparse
import json
from pathlib import Path

from butterfly._paired_startup import inventory, safe_file, sha256
from scripts import run_exp525_recovered_step as run

SOURCE = '3612d6d58fda19e632243c968d42da603a59f851'
PLAN_SHA = 'a9f293bca4ba5d4b02c769a7709dcb3653fbc0559ccdce4266fabe222bc7f52a'
AUDIT_SHA = '8b740b0c77c66b100a7ec8b08c74ea2c7b5b9b679f3f2ce11c8029ff4b29862d'
SUMMARY_SHA = '88b2c8d73bd6cb776d606cdff22f1cc1079d88e006c48ea842bff18273547111'
BINDING_SHA = 'aa221b1e45c3becddb8272613bde2db6a5fdeb3bc450c638c839d3646a74fdc6'
DEFAULT = run.ROOT/'artifacts/EXP-525/result-01'


def verify(directory=DEFAULT, calibration=None, *, replay_raw=False):
    directory = Path(directory)
    if (directory/'failure.json').exists():
        raise ValueError('failure record blocks successful-result interpretation')
    for name, expected in [('audit.json', AUDIT_SHA), ('summary.json', SUMMARY_SHA),
                           ('binding.json', BINDING_SHA)]:
        if sha256(safe_file(directory, name)) != expected:
            raise ValueError('fixed completed evidence differs: '+name)
    audit = run.old.read(directory/'audit.json')
    summary = run.old.read(directory/'summary.json')
    binding = run.old.read(directory/'binding.json')
    plan = run.load()
    if (audit['experiment_id'] != 'EXP-525' or audit['passed'] is not True
            or audit['source_commit'] != SOURCE or audit['plan_sha256'] != PLAN_SHA
            or sha256(run.ROOT/run.PLAN) != PLAN_SHA
            or audit['summary_sha256'] != SUMMARY_SHA
            or summary['status'] != 'collection-completed'
            or summary['experiment_id'] != 'EXP-525'
            or summary['binding'] != binding or binding['source_commit'] != SOURCE
            or binding['plan_sha256'] != PLAN_SHA or binding['runtime'] != plan['runtime']
            or audit['historical_calibration_sha256'] != run.calibrated.SHA
            or binding['historical_calibration_sha256'] != run.calibrated.SHA
            or audit['new_audit_integrations'] != 0 or audit['reused_ivps_not_new'] != 864
            or not 0 <= summary['elapsed_seconds'] <= audit['elapsed_seconds'] <= 21600
            or any(audit[k] is not False for k in ('symbolic_chains_verified',
                'D_identified', 'exact_critical_locus_proved'))):
        raise ValueError('completed evidence semantics differ')
    if (set(binding['sources']) != set(plan['source_paths'])
            or any(sha256(safe_file(run.ROOT, name)) != digest
                   for name, digest in binding['sources'].items())):
        raise ValueError('frozen scientific source differs')
    actual = inventory(directory, omit=('audit.json', 'summary.json'))
    if actual != summary['files']:
        raise ValueError('retained raw inventory differs')
    if (audit['result'] != summary['result']
            or audit['target_ivps'] != summary['target_ivps']
            or audit['segments'] != summary['segments']
            or not 0 < audit['target_ivps'] <= plan['limits']['target_ivps']
            or not 0 < audit['segments'] <= plan['limits']['maximum_segments']):
        raise ValueError('audit and collection accounting differ')
    calibration = run.ROOT/run.calibrated.RECEIPT if calibration is None else Path(calibration)
    with run.calibrated.audit.forbid_integrations():
        source, historic = run.inputs(calibration)
        run.model.scalar_check(audit['result'], source, historic)
        if replay_raw:
            replay = run.raw_audit(directory, summary, source, historic, plan, binding)
            if any(replay[key] != audit[key] for key in replay):
                raise ValueError('repeated frozen raw audit differs')
    if inventory(directory, omit=('audit.json', 'summary.json')) != actual:
        raise ValueError('raw evidence changed during verification')
    row = audit['result']['step']
    return dict(experiment_id='EXP-525', authenticated=True,
        receipt_sha256=AUDIT_SHA, raw_files=len(actual),
        raw_bytes=sum(x['bytes'] for x in actual.values()),
        target_ivps=audit['target_ivps'], segments=audit['segments'],
        elapsed_seconds=audit['elapsed_seconds'], raw_audit_repeated=replay_raw,
        step_qualified=audit['result']['qualified'], accepted=row['accepted'],
        stop_reason=row['stop_reason'], new_integrations=0,
        symbolic_chains_verified=False, D_identified=False,
        scope='Post-run byte authentication and scalar replay; optional raw replay repeats the same frozen implementation, not independent-team replication.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=DEFAULT)
    parser.add_argument('--calibration', type=Path)
    parser.add_argument('--replay-raw', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify(args.directory, args.calibration, replay_raw=args.replay_raw), indent=2))
