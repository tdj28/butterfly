#!/usr/bin/env python3
"""Verify the access-controlled partial-audit receipt and scalar claims."""
import argparse
import json
from pathlib import Path
from scripts import audit_exp524_partial_calibration as audit

RECEIPT = 'artifacts/EXP-524/result-01/audit.json'
SHA = '70de09bcaefbbc3c47199905848a92f9031284df596187cd5ac2659266378014'
SOURCE = 'da58089507c29b9299aa6b75e23723d037576e06'
PLAN_SHA = 'dced8cf33804ec30380efe273aff6d3df82a0a2a3af6369bc052b3f4e53527eb'


def verify(path=None):
    path = audit.ROOT/RECEIPT if path is None else Path(path)
    if audit.sha256(path) != SHA:
        raise ValueError('fixed completed audit receipt differs')
    r = audit.read(path); result = r['result']; binding = r['binding']
    if (r['experiment_id'] != 'EXP-524' or r['passed'] is not True
            or binding['source_commit'] != SOURCE or binding['plan_sha256'] != PLAN_SHA
            or audit.sha256(audit.ROOT/audit.PLAN) != PLAN_SHA
            or binding['recovery_cycle_sha256'] != audit.CYCLE_SHA
            or r['complete_points_audited'] != audit.IDS
            or result['audited_ivps'] != 864 or result['census_segments'] != 667500
            or r['original_failure_sha256'] != audit.preservation.EXPECTED['failure.json']
            or r['original_source_commit'] != audit.preservation.COMMIT
            or r['original_status'] != 'incomplete-timeout'
            or not 0 <= r['elapsed_seconds'] <= 43200
            or any(r[k] for k in ('new_integrations', 'paid_api_calls', 'complete_exp523_audit',
                                 'symbolic_chains_verified', 'D_identified', 'exact_critical_locus_proved'))):
        raise ValueError('completed partial-audit semantics differ')
    sources = binding['handshake']['sources']
    if (set(sources) != set(audit.read(audit.ROOT/audit.PLAN)['source_paths'])
            or any(audit.sha256(audit.ROOT/n) != h for n,h in sources.items())):
        raise ValueError('frozen audit closure differs')
    partial = r['incomplete_predictor']
    if (partial['scientifically_audited'] or partial['used_as_measurement']
            or partial['file_count'] != 16 or len(partial['files']) != 16
            or partial['bytes'] != 12648023 or sum(x['bytes'] for x in partial['files'].values()) != partial['bytes']):
        raise ValueError('incomplete predictor was promoted or changed')
    with audit.forbid_integrations():
        response = audit.response_audit(audit.parent.inputs(), result['points'])
    if not audit.parent.prior.coverage.public.equal(response, result['response']):
        raise ValueError('separate scalar response reconstruction differs')
    qualified = all(p['qualified'] for p in result['points']) and response['qualified']
    if result['calibration_qualified'] != qualified:
        raise ValueError('calibration qualification differs')
    return dict(experiment_id='EXP-524', receipt_sha256=SHA, audit_passed=True,
        calibration_qualified=qualified, complete_points=8, audited_ivps=864, census_segments=667500,
        maximum_a_full_response_error=max(x['full_relative_error'] for x in response['a']['variants']),
        maximum_c_full_response_error=max(x['relative_error'] for x in response['c']['folds']),
        maximum_fold_curvature_error=max(response['curvature']['fold_errors']),
        maximum_gap_curvature_error=max(response['curvature']['gap_errors']),
        new_integrations=0, incomplete_predictor_scientifically_audited=False,
        symbolic_chains_verified=False,
        scope='Receipt/source authentication and scalar rederivation; this command does not repeat the prax raw audit.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=Path)
    print(json.dumps(verify(parser.parse_args().receipt), indent=2))
