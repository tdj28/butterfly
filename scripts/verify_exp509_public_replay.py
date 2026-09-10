#!/usr/bin/env python3
"""Verify compact forensic evidence; this does not reopen the local raw archive."""
import argparse
import hashlib
import json
from pathlib import Path

from butterfly._paired_startup import sha256
from scripts import replay_exp509_failed_predictor as run
from scripts import verify_exp504_public_contact as compact

SOURCE = '808054ffb8ecda4c216faa655c734f57ef691a23'


def json_sha(value):
    return hashlib.sha256((json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()).hexdigest()


def verify(path, expected_sha):
    if sha256(path) != expected_sha:
        raise ValueError('public replay receipt byte identity differs')
    saved = json.loads(Path(path).read_bytes())
    p = run.load()
    b = saved['binding']
    original = saved['original_binding']
    failure = saved['original_failure']
    if (saved['experiment_id'] != 'EXP-509' or saved['raw_replay_passed'] is not True
            or saved['original_run_completed'] is not False or saved['new_integrations'] != 0
            or saved['symbolic_chains_verified'] is not False or b['source_commit'] != SOURCE
            or b['plan_sha256'] != sha256(run.PLAN) or b['paid_review'] != p['paid_review']
            or b['new_integrations'] != 0
            or b['sources'] != {n:sha256(run.ROOT/n) for n in p['source_paths']}
            or not b['started_utc'] <= saved['completed_utc']
            or not 0 <= saved['elapsed_seconds'] <= p['limits']['wall_seconds']
            or json_sha(b) != saved['replay_marker_sha256']
            or saved['original_point_sha256'] != run.POINT_SHA
            or saved['original_marker_sha256'] != run.MARKER_SHA
            or json_sha(failure) != run.FAILURE_SHA or json_sha(original) != run.MARKER_SHA
            or original['source_commit'] != run.SOURCE
            or original['plan_sha256'] != sha256(run.old.PLAN) or original['inputs'] != run.old.INPUTS
            or original['sources'] != {n:sha256(run.ROOT/n) for n in run.old.load()['source_paths']}
            or saved['original_ledger'] != run.old.base.load()['ledger']
            or saved['original_target_ivps'] != p['original_ivps']
            or type(saved['original_output_bytes']) is not int
            or not 0 < saved['original_output_bytes'] <= run.old.load()['limits']['output_bytes']):
        raise ValueError('forensic source, failure, claim or resource binding differs')
    run.old.public.verify(run.ROOT/run.old.RECEIPT,run.old.INPUTS[run.old.RECEIPT])
    entries = saved['reconstructed_result']['entries']
    counts = saved['counts']
    if len(entries) != 1 or len(counts) != 1 or counts[0]['target_ivps'] != p['original_ivps']:
        raise ValueError('only the original predictor may be replayed')
    seen = []
    def measure(numerical,spec):
        if seen or spec['id'] != 'predictor' or entries[0]['point']['spec'] != spec:
            raise ValueError('unexpected predictor or unauthorized corrector')
        point = entries[0]['point']
        compact.check_point(point,numerical,dict(counts[0],id='predictor',point_sha256=run.POINT_SHA))
        seen.append('predictor')
        return point
    progress = run.old.model.ledger()
    result = run.follow(run.old.base.load(),run.old.prior.prior.inputs(),run.old.prior.inputs(),
        run.old.inputs(),measure,progress)
    if (not compact.equal(result,saved['reconstructed_result']) or progress != saved['reconstructed_progress']
            or result['analysis']['accepted'] or result['analysis']['status'] != 'predictor-unqualified'):
        raise ValueError('reconstructed stopping decision differs')
    return dict(experiment_id='EXP-509',passed=True,original_run_completed=False,
        reconstructed_status=result['analysis']['status'],new_integrations=0,full_raw_audit_repeated=False,
        symbolic_chains_verified=False,
        scope='Public compact identities, comparisons and rejection replayed; original raw meshes and on-disk byte count are not independently checked here.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result',type=Path,required=True)
    parser.add_argument('--expected-sha256',required=True)
    a = parser.parse_args()
    print(json.dumps(verify(a.result,a.expected_sha256),sort_keys=True))


if __name__ == '__main__':
    main()
