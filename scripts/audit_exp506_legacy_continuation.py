#!/usr/bin/env python3
"""Hash-first replay including independent re-fitting of the reused prefix."""
import argparse
import json
from pathlib import Path
from butterfly._paired_startup import inventory,sha256,write_json
from scripts import run_exp506_legacy_continuation as run


def audit(output,expected_sha):
    p = run.load()
    if sha256(output/'summary.json') != expected_sha:
        raise ValueError('continuation summary identity differs')
    saved = json.loads((output/'summary.json').read_bytes())
    binding = json.loads((output/'binding.json').read_bytes())
    if (saved['experiment_id'] != 'EXP-506' or saved['status'] != 'completed' or saved['binding'] != binding
            or binding['plan_sha256'] != sha256(run.PLAN) or binding['inputs'] != p['inputs']
            or binding['sources'] != {n:sha256(run.ROOT/n) for n in p['source_paths']}
            or saved['files'] != inventory(output,omit=('summary.json',))
            or saved['target_integrations'] != 0 or saved['symbolic_chains_verified'] is not False
            or saved['original_attempt_reset'] is not False or saved['original_failure_sha256'] != run.FAILURE_SHA
            or saved['paid_review'] != p['paid_review'] or not 0 <= saved['elapsed_seconds'] <= p['limits']['wall_seconds']
            or not binding['started_utc'] <= saved['completed_utc']
            or sum(r['bytes'] for r in saved['files'].values()) > p['limits']['output_bytes']):
        raise ValueError('continuation source/raw/claim binding differs')
    marker = run.ROOT/'artifacts/EXP-506/target-once.json'
    if sha256(marker) != saved['marker_sha256'] or json.loads(marker.read_bytes()) != binding:
        raise ValueError('continuation attempt marker differs')
    startup = json.loads((output/'startup.json').read_bytes())
    preflight = run.preflight()
    if (startup['passed'] is not True or startup['isolated'] is not True or startup['new_branch_fits'] != 0
            or startup['new_word_spline_fits'] != 0 or startup['target_integrations'] != 0
            or startup['sources'] != {n:sha256(run.ROOT/n) for n in set(p['source_paths'])|set(p['inputs'])|set(run.old.shared.INPUTS)}
            or json.loads(startup['stdout']) != preflight
            or json.loads((output/'preflight.json').read_bytes()) != preflight):
        raise ValueError('authentic startup or original-prefix/schema replay differs')
    names = {'binding.json','startup.json','preflight.json'}
    def emit(name,entry):
        name += '.json'
        if not run.old.equal(json.loads((output/name).read_bytes()),entry):
            raise ValueError('all retained fit records differ')
        names.add(name)
    result = run.analyze(False,emit)
    if (not run.old.equal(result,saved['result']) or names != set(saved['files'])
            or saved['reused_branch_fits'] != 255 or saved['new_branch_fits'] != result['fit_calls']-255):
        raise ValueError('full fit replay or provenance accounting differs')
    return dict(experiment_id='EXP-506',passed=True,source_commit=binding['source_commit'],plan_sha256=sha256(run.PLAN),
        summary_sha256=expected_sha,audit_source_sha256=sha256(Path(__file__)),inputs=p['inputs'],result=result,
        original_failure_sha256=run.FAILURE_SHA,reused_branch_fits=255,new_branch_fits=saved['new_branch_fits'],
        audit_branch_fit_evaluations=result['fit_calls'],audit_word_spline_evaluations=result['word_spline_fit_count'],
        target_integrations=0,paid_review=p['paid_review'],symbolic_chains_verified=False,original_attempt_reset=False,
        historical_receipts_modified=False,full_trajectory_audit_repeated=False,
        scope='Complete saved-data turning-filter sensitivity for EXP-186, not archive-wide clearance or new flow-chain evidence.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--expected-sha256',required=True)
    parser.add_argument('--output',type=Path,required=True)
    a = parser.parse_args()
    write_json(a.output,audit(a.run,a.expected_sha256))


if __name__ == '__main__':
    main()
