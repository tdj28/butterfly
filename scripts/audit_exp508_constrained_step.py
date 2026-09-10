#!/usr/bin/env python3
"""Replay both sequential stages from retained raw data; never repeat an IVP."""
import argparse
import json
from pathlib import Path
from butterfly._paired_startup import inventory,sha256
from butterfly.bounded_json import directory_bytes,write_bounded_json
from scripts import run_exp508_constrained_step as run
from scripts import audit_exp502_joint_contact as point_audit


def audit(output,original,expected_sha):
    p = run.load()
    if sha256(output/'summary.json') != expected_sha:
        raise ValueError('summary identity differs')
    saved = json.loads((output/'summary.json').read_bytes())
    binding = json.loads((output/'binding.json').read_bytes())
    if (saved['experiment_id'] != 'EXP-508' or saved['status'] != 'completed' or saved['binding'] != binding
            or binding['plan_sha256'] != sha256(run.PLAN) or binding['inputs'] != run.INPUTS
            or binding['sources'] != {n:sha256(run.ROOT/n) for n in p['source_paths']}
            or saved['files'] != inventory(output,omit=('summary.json',)) or saved['ledger'] != run.base.load()['ledger']
            or saved['symbolic_chains_verified'] is not False or binding['paid_review'] != p['paid_review']
            or binding['initial_free_bytes'] < p['limits']['initial_free_bytes']
            or not binding['started_utc'] <= saved['completed_utc']
            or not 0 <= saved['elapsed_seconds'] <= p['limits']['wall_seconds']):
        raise ValueError('source, inputs, complete inventory, time or claim binding differs')
    marker = run.ROOT/'artifacts/EXP-508/target-once.json'
    if sha256(marker) != saved['marker_sha256'] or json.loads(marker.read_bytes()) != binding:
        raise ValueError('consumed attempt marker differs')
    startup = json.loads((output/'startup.json').read_bytes())
    if (startup['passed'] is not True or startup['isolated'] is not True or startup['target_integrations'] != 0
            or startup['sources'] != {n:sha256(run.ROOT/n) for n in set(p['source_paths'])|set(run.INPUTS)}
            or json.loads(startup['stdout']) != dict(valid=True,target_integrations=0,maximum_points=2,variants=256)):
        raise ValueError('authentic isolated startup differs')
    if run.prior.prior.controls(original,p) != json.loads((output/'control-replay.json').read_bytes()):
        raise ValueError('analytic controls differ')
    run.validate()
    names = {'binding.json','startup.json','control-replay.json'}
    counts = []
    def measure(numerical,spec):
        i = len(counts)
        item = saved['result']['points'][i]
        if item['id'] != spec['id'] or item['path'] != spec['id']+'/point.json' or sha256(output/item['path']) != item['sha256']:
            raise ValueError('sequential point reference differs')
        row = json.loads((output/item['path']).read_bytes())
        if row['spec'] != spec:
            raise ValueError('sequential proposal parameters differ')
        paths,calls,products = point_audit.check_point(output/spec['id'],row,numerical,binding,saved['completed_utc'])
        names.update(spec['id']+'/'+n for n in paths)
        counts.append(dict(id=spec['id'],target_ivps=calls,inherited_archive_products=products,point_sha256=item['sha256']))
        print(json.dumps(dict(audited_stage=spec['id'],audited_ivps=sum(c['target_ivps'] for c in counts))),flush=True)
        return row
    def completed(entry):
        name = entry['point']['spec']['id']+'-comparison.json'
        if json.loads((output/name).read_bytes()) != {k:v for k,v in entry.items() if k != 'point'}:
            raise ValueError('saved point comparison differs')
        names.add(name)
    progress = run.model.ledger()
    result = run.model.follow(run.base.load(),run.prior.prior.inputs(),run.prior.inputs(),run.inputs(),measure,progress,completed)
    calls = sum(c['target_ivps'] for c in counts)
    size = directory_bytes(output)
    if (len(counts) != len(saved['result']['points']) or result['analysis'] != saved['result']['analysis']
            or result['initialization'] != saved['result']['initialization'] or progress != saved['progress']
            or names != set(saved['files']) or calls != saved['target_ivps'] or calls > p['limits']['target_ivps']
            or size > p['limits']['output_bytes']):
        raise ValueError('complete stages, comparisons, counts or output quota differ')
    return dict(experiment_id='EXP-508',passed=True,protocol_compliant=True,source_commit=binding['source_commit'],
        plan_sha256=sha256(run.PLAN),summary_sha256=expected_sha,audit_source_sha256=sha256(Path(__file__)),
        inputs=run.INPUTS,result=result,progress=progress,ledger=saved['ledger'],point_counts=counts,target_ivps=calls,
        output_bytes_including_summary=size,output_limit_bytes=p['limits']['output_bytes'],
        new_integrations=0,paid_review=p['paid_review'],symbolic_chains_verified=False,
        raw_replay_scope='Every completed predictor/corrector: meshes, guards, Decimal coefficients, Newton traces, full prefix census and scalar/full-state comparisons. Local shared-code audit, not independent-team proof.')


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
