#!/usr/bin/env python3
"""Full raw replay and complete-directory quota audit; no new integrations."""
import argparse
import json
from pathlib import Path
from butterfly._paired_startup import inventory, sha256
from butterfly.bounded_json import directory_bytes, write_bounded_json
from scripts import run_exp507_fold_restoration as run
from scripts import audit_exp502_joint_contact as point_audit


def audit(output,original,expected_sha):
    p = run.load()
    if sha256(output/'summary.json') != expected_sha:
        raise ValueError('summary identity differs')
    saved = json.loads((output/'summary.json').read_bytes())
    binding = json.loads((output/'binding.json').read_bytes())
    if (saved['experiment_id'] != 'EXP-507' or saved['status'] != 'completed' or saved['binding'] != binding
            or binding['plan_sha256'] != sha256(run.PLAN) or binding['inputs'] != run.INPUTS
            or binding['sources'] != {n:sha256(run.ROOT/n) for n in p['source_paths']}
            or saved['files'] != inventory(output,omit=('summary.json',))
            or saved['ledger'] != run.prior.base.load()['ledger'] or saved['symbolic_chains_verified'] is not False
            or binding['paid_review'] != p['paid_review'] or binding['initial_free_bytes'] < p['limits']['initial_free_bytes']
            or not binding['started_utc'] <= saved['completed_utc']
            or not 0 <= saved['elapsed_seconds'] <= p['limits']['wall_seconds']):
        raise ValueError('source, inputs, complete inventory, time or claim binding differs')
    marker = run.ROOT/'artifacts/EXP-507/target-once.json'
    if sha256(marker) != saved['marker_sha256'] or json.loads(marker.read_bytes()) != binding:
        raise ValueError('consumed attempt marker differs')
    startup = json.loads((output/'startup.json').read_bytes())
    if (startup['passed'] is not True or startup['isolated'] is not True or startup['target_integrations'] != 0
            or startup['sources'] != {n:sha256(run.ROOT/n) for n in set(p['source_paths'])|set(run.INPUTS)}
            or json.loads(startup['stdout']) != dict(valid=True,target_integrations=0,points=1,variants=256)):
        raise ValueError('authentic isolated startup differs')
    if run.prior.controls(original,p) != json.loads((output/'control-replay.json').read_bytes()):
        raise ValueError('original analytic controls differ')
    run.validate()
    if saved['point_path'] != 'fold-restoration/point.json' or sha256(output/saved['point_path']) != saved['point_sha256']:
        raise ValueError('unique raw point identity differs')
    point = json.loads((output/saved['point_path']).read_bytes())
    numerical = run.prior.model.warm_plan(run.prior.base.load(),run.inputs())
    if point['spec'] != p['proposal']['spec']:
        raise ValueError('frozen proposal differs')
    paths,calls,products = point_audit.check_point(output/'fold-restoration',point,numerical,binding,saved['completed_utc'])
    decision = run.model.decide(run.prior.base.load(),run.inputs(),point,p['proposal'])
    names = {'binding.json','startup.json','control-replay.json','decision.json'}|{'fold-restoration/'+n for n in paths}
    size = directory_bytes(output)  # Includes the final summary, unlike EXP-506.
    if (decision != saved['decision'] or json.loads((output/'decision.json').read_bytes()) != decision
            or set(saved['files']) != names or calls != saved['target_ivps']
            or not 0 < calls <= p['limits']['target_ivps'] or size > p['limits']['output_bytes']):
        raise ValueError('decision, integration accounting or complete output quota differs')
    return dict(experiment_id='EXP-507',passed=True,protocol_compliant=True,source_commit=binding['source_commit'],
        plan_sha256=sha256(run.PLAN),summary_sha256=expected_sha,audit_source_sha256=sha256(Path(__file__)),
        inputs=run.INPUTS,proposal=p['proposal'],point=point,decision=decision,ledger=saved['ledger'],
        target_ivps=calls,inherited_archive_products=products,point_sha256=saved['point_sha256'],
        output_bytes_including_summary=size,output_limit_bytes=p['limits']['output_bytes'],
        new_integrations=0,paid_review=p['paid_review'],symbolic_chains_verified=False,
        raw_replay_scope='All meshes, guards, Decimal Taylor coefficients, Newton traces, complete prefix census and full-state cycle comparisons; local shared-code audit, not independent-team proof.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--original-run',type=Path,required=True)
    parser.add_argument('--expected-sha256',required=True)
    parser.add_argument('--output',type=Path,required=True)
    a = parser.parse_args()
    result = audit(a.run,a.original_run,a.expected_sha256)
    write_bounded_json(a.output.parent,a.output,result,limit_bytes=directory_bytes(a.output.parent)+16*1024**2)
    print(json.dumps(dict(passed=True,target_ivps=result['target_ivps'],audit_sha256=sha256(a.output))))


if __name__ == '__main__':
    main()
