#!/usr/bin/env python3
"""Replay every fold, guard and branch-transport decision without new IVPs."""
import argparse
import json
import math
from pathlib import Path

from butterfly._paired_startup import inventory,sha256
from butterfly.bounded_json import directory_bytes,write_bounded_json
from scripts import run_exp510_fold_transport as run
from scripts import audit_exp502_joint_contact as point_audit


def scalar_assess(previous,current,scales):
    if not all(r['qualified_in_region'] for r in current):
        return None
    spread,change = 0.,0.
    for key in ('image_state','next_state'):
        a,b = [[v['observations'][1][key] for r in rows for v in r['solvers']] for rows in (previous,current)]
        for i,scale in enumerate(scales):
            spread = max(spread,max(q[i]/scale for q in b)-min(q[i]/scale for q in b))
            change = max(change,max(abs(x[i]/scale-y[i]/scale) for x,y in zip(a,b,strict=True)))
    return dict(spread=spread,change=change,passed=spread <= 1e-6 and change <= .01)


def audit(output,expected_sha):
    p = run.load()
    if sha256(output/'summary.json') != expected_sha:
        raise ValueError('summary identity differs')
    saved = json.loads((output/'summary.json').read_bytes())
    binding = json.loads((output/'binding.json').read_bytes())
    if (saved['experiment_id'] != 'EXP-510' or saved['status'] != 'completed' or saved['binding'] != binding
            or binding['sources'] != {n:sha256(run.ROOT/n) for n in p['source_paths']}
            or binding['inputs'] != run.INPUTS or binding['plan_sha256'] != sha256(run.PLAN)
            or binding['paid_review'] != p['paid_review'] or saved['symbolic_chains_verified'] is not False
            or binding['initial_free_bytes'] < p['limits']['initial_free_bytes']
            or saved['ledger'] != run.base.load()['ledger']
            or saved['files'] != inventory(output,omit=('summary.json',))
            or not binding['started_utc'] <= saved['completed_utc']
            or not 0 <= saved['elapsed_seconds'] <= p['limits']['wall_seconds']):
        raise ValueError('source/input/raw/resource/claim binding differs')
    marker = run.ROOT/'artifacts/EXP-510/target-once.json'
    if sha256(marker) != saved['marker_sha256'] or json.loads(marker.read_bytes()) != binding:
        raise ValueError('consumed marker differs')
    startup = json.loads((output/'startup.json').read_bytes())
    if (startup['passed'] is not True or startup['isolated'] is not True or startup['new_integrations'] != 0
            or startup['sources'] != {n:sha256(run.ROOT/n) for n in set(p['source_paths'])|set(run.INPUTS)}
            or json.loads(startup['stdout']) != dict(valid=True,new_integrations=0,maximum_substeps=4,folds_per_step=4)):
        raise ValueError('isolated startup differs')
    if run.prior.old.prior.prior.controls(run.ROOT/'artifacts/EXP-502/target-69efcd3',p) != json.loads((output/'control-replay.json').read_bytes()):
        raise ValueError('analytic controls differ')
    run.public.verify(run.ROOT/run.RECEIPT,run.INPUTS[run.RECEIPT])
    names = {'binding.json','startup.json','control-replay.json'}
    counts = []
    previous = run.prior.old.inputs()['folds']
    def measure(spec,candidates):
        nonlocal previous
        folder = output/spec['id']
        if json.loads((folder/'inputs.json').read_bytes()) != dict(spec=spec,candidates=candidates):
            raise ValueError('warm candidate identities differ')
        rows = []
        local_names = {'inputs.json','folds.json'}
        calls,products = 0,0
        for c in candidates:
            row,paths,count = point_audit.old.check_fold(folder,c,run.base.load()['fold'],binding,saved['completed_utc'])
            if row != json.loads((folder/(c['id']+'.json')).read_bytes()):
                raise ValueError('complete fold raw replay differs')
            local_names.update(paths)
            local_names.add(c['id']+'.json')
            calls += count
            products += count
            for method in p['solvers']:
                label = c['id']+'--'+method
                profile = json.loads((folder/(label+'.json')).read_bytes())
                for i,entry in enumerate(profile['censuses']):
                    name = label+f'--guard-{i}.npz'
                    point_audit.check_guard(point_audit.old.load_raw(folder/name),
                        point_audit.old.load_raw(folder/(label+f'--census-{i}.npz')),
                        entry['report'],run.base.load()['fold']['guard'])
                    local_names.add(name)
                    calls += 1
            rows.append(row)
        if json.loads((folder/'folds.json').read_bytes()) != rows or set(inventory(folder)) != local_names:
            raise ValueError('complete substep raw inventory differs')
        scalar = scalar_assess(previous,rows,run.base.load()['fold']['scales'])
        decision = run.model.assess(previous,rows,run.base.load()['fold']['scales'])
        if scalar is not None and (scalar['passed'] != decision['transport_qualified']
                or not math.isclose(scalar['spread'],decision['cross_history_spread'],rel_tol=1e-12,abs_tol=1e-13)
                or not math.isclose(scalar['change'],decision['adjacent_displacement'],rel_tol=1e-12,abs_tol=1e-13)):
            raise ValueError('separately coded scalar branch comparison differs')
        previous = rows
        counts.append(dict(id=spec['id'],target_ivps=calls,inherited_archive_products=products))
        names.update(spec['id']+'/'+n for n in local_names)
        print(json.dumps(dict(audited_substep=spec['id'],target_ivps=sum(c['target_ivps'] for c in counts))),flush=True)
        return rows
    result = run.model.follow(run.base.load(),run.prior.old.inputs(),run.inputs()['spec']['parameters'],run.offset,measure)
    endpoint = run.endpoint(result)
    calls = sum(c['target_ivps'] for c in counts)
    size = directory_bytes(output)
    if (result != saved['result'] or endpoint != saved['endpoint_comparison'] or names != set(saved['files'])
            or saved['stage_progress'] != [dict(id=r['spec']['id'],status='completed') for r in result['rows']]
            or calls != saved['target_ivps'] or calls > p['limits']['target_ivps'] or size > p['limits']['output_bytes']):
        raise ValueError('complete decision, IVP accounting or output quota differs')
    if endpoint is not None and not point_audit.old.periodic_audit.numeric_equal(
            point_audit.old.scalar_contact(result['rows'][-1]['folds'],run.inputs()['cycle']),endpoint['contact']):
        raise ValueError('separately coded scalar endpoint contact differs')
    return dict(experiment_id='EXP-510',passed=True,protocol_compliant=True,source_commit=binding['source_commit'],
        summary_sha256=expected_sha,plan_sha256=sha256(run.PLAN),inputs=run.INPUTS,result=result,
        endpoint_comparison=endpoint,counts=counts,target_ivps=calls,output_bytes_including_summary=size,
        output_limit_bytes=p['limits']['output_bytes'],ledger=saved['ledger'],new_integrations=0,
        symbolic_chains_verified=False,paid_review=p['paid_review'],
        scope='Full local shared-code fold/guard/census replay plus separately coded scalar comparisons; not independent-team replication. Endpoint cycle is reused explicitly, not a new intermediate or joint-point measurement.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--expected-sha256',required=True)
    parser.add_argument('--output',type=Path,required=True)
    a = parser.parse_args()
    result = audit(a.run,a.expected_sha256)
    write_bounded_json(a.output.parent,a.output,result,limit_bytes=directory_bytes(a.output.parent)+16*1024**2)
    print(json.dumps(dict(passed=True,target_ivps=result['target_ivps'],audit_sha256=sha256(a.output))))


if __name__ == '__main__':
    main()
