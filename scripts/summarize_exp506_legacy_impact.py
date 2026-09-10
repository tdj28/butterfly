#!/usr/bin/env python3
"""Compact numerical result with an explicit full-directory quota deviation."""
import argparse
import json
from pathlib import Path

from butterfly._paired_startup import inventory,sha256
from butterfly.bounded_json import write_bounded_json
from scripts import run_exp506_legacy_continuation as run

AUDIT_SHA = 'a196976f7ef4d20df0e9e069067ff3b366b6cb8a735c43d41c72d964ec120988'


def summarize(audit_path,output):
    if sha256(audit_path) != AUDIT_SHA:
        raise ValueError('complete numerical audit hash differs')
    audit = json.loads(audit_path.read_bytes())
    p = run.load()
    if (audit['passed'] is not True or audit['plan_sha256'] != sha256(run.PLAN)
            or audit['symbolic_chains_verified'] is not False or audit['original_attempt_reset'] is not False
            or audit['original_failure_sha256'] != run.FAILURE_SHA):
        raise ValueError('numerical audit/claim binding differs')
    summary_path = output/'summary.json'
    if sha256(summary_path) != audit['summary_sha256']:
        raise ValueError('raw summary identity differs')
    saved = json.loads(summary_path.read_bytes())
    files = inventory(output)
    if saved['files'] != {k:v for k,v in files.items() if k != 'summary.json'}:
        raise ValueError('raw output inventory differs')
    total = sum(r['bytes'] for r in files.values())
    rows = []
    for row in audit['result']['rows']:
        modes = {}
        for name,mode in row['modes'].items():
            modes[name] = dict(robust=mode['robust'],words=mode['words'],branch_fit_count=len(mode['fits']),
                retained_root_occurrences=sum(len(f['geometry']['legacy']) for f in mode['fits'] if f['geometry'] is not None),
                pre_spline_failures=sum(f['geometry'] is None for f in mode['fits']))
        rows.append(dict(profile=row['profile'],coordinate=row['coordinate'],pair_count=row['pair_count'],
            pair_sha256=row['pair_sha256'],robust_unchanged=row['robust_unchanged'],words_unchanged=row['words_unchanged'],
            removed_root_occurrences=row['removed_root_occurrences'],modes=modes))
    limit = p['limits']['output_bytes']
    return dict(experiment_id='EXP-506',numerical_replay_passed=True,protocol_compliant=total <= limit,
        source_commit=audit['source_commit'],plan_sha256=audit['plan_sha256'],summary_sha256=audit['summary_sha256'],
        full_local_audit_sha256=AUDIT_SHA,full_local_audit_bytes=audit_path.stat().st_size,
        original_failure_sha256=run.FAILURE_SHA,rows=rows,
        analysis={k:v for k,v in audit['result'].items() if k not in ('rows','word_spline_fits')},
        reused_branch_fits=audit['reused_branch_fits'],new_branch_fits=audit['new_branch_fits'],
        audit_branch_fit_evaluations=audit['audit_branch_fit_evaluations'],audit_word_spline_evaluations=audit['audit_word_spline_evaluations'],
        resource=dict(output_bytes_including_summary=total,output_limit_bytes=limit,excess_bytes=max(0,total-limit),
            pre_summary_bytes=total-summary_path.stat().st_size,summary_bytes=summary_path.stat().st_size,
            compliant=total <= limit,reason='The frozen writer and auditor checked prior products but omitted the final duplicated summary from quota admission.'),
        public_scope='Compact comparison results only; full saved-data re-fit requires the hash-bound local EXP-186 arrays. This summary is not a new full audit.',
        target_integrations=0,paid_review=p['paid_review'],symbolic_chains_verified=False,
        original_attempt_reset=False,historical_receipts_modified=False,full_trajectory_audit_repeated=False,
        summarizer_sha256=sha256(Path(__file__)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit',type=Path,required=True)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    a = parser.parse_args()
    result = summarize(a.audit,a.run)
    print(json.dumps(write_bounded_json(a.output.parent,a.output,result,
        limit_bytes=1024**2,minimum_free_bytes=8*1024**3)))


if __name__ == '__main__':
    main()
