#!/usr/bin/env python3
"""Hash-first complete saved-data replay of the bounded legacy sensitivity."""
import argparse
import json
from pathlib import Path
from butterfly._paired_startup import inventory,sha256,write_json
from scripts import run_exp505_legacy_impact as run


def audit(output,expected_sha):
    p = run.load()
    if sha256(output/'summary.json') != expected_sha:
        raise ValueError('summary identity differs')
    saved = json.loads((output/'summary.json').read_bytes())
    binding = json.loads((output/'binding.json').read_bytes())
    if (saved['experiment_id'] != 'EXP-505' or saved['status'] != 'completed' or saved['binding'] != binding
            or binding['plan_sha256'] != sha256(run.PLAN) or binding['inputs'] != run.INPUTS
            or binding['sources'] != {n:sha256(run.ROOT/n) for n in p['source_paths']}
            or saved['files'] != inventory(output,omit=('summary.json',))
            or saved['target_integrations'] != 0 or saved['symbolic_chains_verified'] is not False
            or saved['paid_review'] != p['paid_review'] or not 0 <= saved['elapsed_seconds'] <= 600
            or not binding['started_utc'] <= saved['completed_utc']):
        raise ValueError('raw/source/scope binding differs')
    marker = run.ROOT/'artifacts/EXP-505/target-once.json'
    if sha256(marker) != saved['marker_sha256'] or json.loads(marker.read_bytes()) != binding:
        raise ValueError('exclusive marker differs')
    startup = json.loads((output/'startup.json').read_bytes())
    if (startup['passed'] is not True or startup['isolated'] is not True or startup['target_fits'] != 0
            or startup['target_integrations'] != 0
            or startup['sources'] != {n:sha256(run.ROOT/n) for n in set(p['source_paths'])|set(run.INPUTS)|set(run.shared.INPUTS)}
            or json.loads(startup['stdout']) != dict(valid=True,target_integrations=0,target_fits=0)
            or json.loads((output/'controls.json').read_bytes()) != run.geometry.controls()):
        raise ValueError('authentic startup or controls differ')
    names = {'binding.json','startup.json','controls.json'}
    def emit(name,entry):
        name += '.json'
        if not run.equal(json.loads((output/name).read_bytes()),entry):
            raise ValueError('saved complete fit population differs')
        names.add(name)
    result = run.analyze(emit)
    if not run.equal(result,saved['result']) or names != set(saved['files']):
        raise ValueError('complete retrospective replay differs')
    return dict(experiment_id='EXP-505',passed=True,source_commit=binding['source_commit'],plan_sha256=sha256(run.PLAN),
        summary_sha256=expected_sha,audit_source_sha256=sha256(Path(__file__)),inputs=run.INPUTS,result=result,
        target_integrations=0,paid_review=p['paid_review'],symbolic_chains_verified=False,
        historical_receipts_modified=False,full_trajectory_audit_repeated=False,
        scope='Independent pair construction and scalar geometry checks within a shared-code saved-data sensitivity replay.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--expected-sha256',required=True)
    parser.add_argument('--output',type=Path,required=True)
    a = parser.parse_args()
    write_json(a.output,audit(a.run,a.expected_sha256))


if __name__ == '__main__':
    main()
