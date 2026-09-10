#!/usr/bin/env python3
"""Hash all raw evidence, then replay every warm point and path decision."""
import argparse
import json
from pathlib import Path

from butterfly._paired_startup import inventory,sha256,write_json
from scripts import run_exp504_guarded_contact as run
from scripts import audit_exp502_joint_contact as point_audit


def audit(output,original,expected_sha):
    p = run.load()
    if sha256(output/'summary.json') != expected_sha:
        raise ValueError('summary byte identity differs')
    saved = json.loads((output/'summary.json').read_bytes())
    binding = json.loads((output/'binding.json').read_bytes())
    if (saved['experiment_id'] != 'EXP-504' or saved['status'] != 'completed'
            or saved['binding'] != binding or binding['plan_sha256'] != sha256(run.PLAN)
            or binding['sources'] != {n:sha256(run.ROOT/n) for n in p['source_paths']}
            or binding['inputs'] != run.INPUTS or saved['ledger'] != run.base.load()['ledger']
            or saved['symbolic_chains_verified'] is not False or binding['paid_review'] != p['paid_review']
            or saved['files'] != inventory(output,omit=('summary.json',))
            or not binding['started_utc'] <= saved['completed_utc']
            or binding['initial_free_bytes'] < p['limits']['initial_free_bytes']
            or not 0 <= saved['elapsed_seconds'] <= p['limits']['wall_seconds']):
        raise ValueError('source, input, raw inventory or claim binding differs')
    marker = run.ROOT/'artifacts/EXP-504/target-once.json'
    if sha256(marker) != saved['marker_sha256'] or json.loads(marker.read_bytes()) != binding:
        raise ValueError('exclusive attempt marker differs')
    startup = json.loads((output/'startup.json').read_bytes())
    if (startup['passed'] is not True or startup['isolated'] is not True or startup['target_integrations'] != 0
            or startup['sources'] != {n:sha256(run.ROOT/n) for n in set(p['source_paths'])|set(run.INPUTS)}
            or json.loads(startup['stdout']) != dict(valid=True,target_integrations=0,steps=8,variants=256)):
        raise ValueError('isolated copied source differs')
    if run.controls(original,p) != json.loads((output/'control-replay.json').read_bytes()):
        raise ValueError('analytic control replay differs')
    run.validate()
    names = {'binding.json','startup.json','control-replay.json'}
    counts = []
    def measure(numerical,spec):
        index = len(counts)
        row = saved['result']['steps'][index]['point']
        if row['spec'] != spec:
            raise ValueError('unique sequential proposal differs')
        paths,calls,products = point_audit.check_point(output/spec['id'],row,numerical,binding,saved['completed_utc'])
        names.update(spec['id']+'/'+n for n in paths)
        counts.append(dict(id=spec['id'],target_ivps=calls,inherited_archive_products=products,
            point_sha256=sha256(output/spec['id']/'point.json')))
        print(json.dumps(dict(audited_point=spec['id'],completed_ivps=sum(r['target_ivps'] for r in counts))),flush=True)
        return row
    def completed(entry):
        name = entry['point']['spec']['id']+'-decision.json'
        if json.loads((output/name).read_bytes()) != entry['decision']:
            raise ValueError('saved decision differs')
        names.add(name)
    progress = run.model.ledger()
    result = run.model.follow(run.base.load(),run.inputs(),measure,progress,completed)
    calls = sum(r['target_ivps'] for r in counts)
    if (result != saved['result'] or progress != saved['progress'] or names != set(saved['files'])
            or calls != saved['target_ivps'] or calls > p['limits']['target_ivps']
            or sum(v['bytes'] for v in saved['files'].values()) > p['limits']['output_bytes']):
        raise ValueError('complete path, decision, raw names or integration accounting differs')
    return dict(experiment_id='EXP-504',passed=True,source_commit=binding['source_commit'],
        plan_sha256=sha256(run.PLAN),summary_sha256=expected_sha,audit_source_sha256=sha256(Path(__file__)),
        inputs=run.INPUTS,result=result,progress=progress,ledger=saved['ledger'],point_counts=counts,
        target_ivps=calls,new_integrations=0,paid_review=p['paid_review'],symbolic_chains_verified=False,
        raw_replay_scope='All completed warm points: meshes, guards, Decimal Taylor recurrence, Newton traces, full prefix census, cycle identity, scalar contact and model checks. Local shared-code audit, not independent-team proof.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--original-run',type=Path,required=True)
    parser.add_argument('--expected-sha256',required=True)
    parser.add_argument('--output',type=Path,required=True)
    a = parser.parse_args()
    write_json(a.output,audit(a.run,a.original_run,a.expected_sha256))


if __name__ == '__main__':
    main()
