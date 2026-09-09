#!/usr/bin/env python3
"""Replay compact path evidence, explicitly without claiming a raw mesh audit."""
import argparse
import hashlib
import json
from pathlib import Path

from butterfly._paired_startup import sha256
from scripts import run_exp504_guarded_contact as run
from scripts import audit_exp504_guarded_contact as raw_audit

SOURCE = '0657f510e2ca07939237a2a70ca681278977e14a'
equal = run.public.numeric_equal


def check_point(row,numerical,count):
    encoded = (json.dumps(row,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    if (count['id'] != row['spec']['id'] or hashlib.sha256(encoded).hexdigest() != count['point_sha256']
            or type(count['target_ivps']) is not int or type(count['inherited_archive_products']) is not int
            or not 0 < count['inherited_archive_products'] <= count['target_ivps']
            or row['cycle']['spec'] != row['spec']):
        raise ValueError('compact point identity or counts differ')
    folds,boundaries,_,_ = run.base.point_inputs(numerical,row['spec'])
    if ([r['id'] for r in row['folds']] != [r['id'] for r in folds]
            or [r['id'] for r in row['boundaries']] != [r['id'] for r in boundaries]):
        raise ValueError('complete representation identities required')
    pair = run.base.previous.cycles_run.compare_profiles(row['cycle']['profiles'],numerical['periodic'])
    qualified = pair['passed'] and all(w['counts'] == dict(historical=6,barrio=8)
        for v in row['cycle']['profiles'] for w in v['metric']['windows'])
    if not equal(pair,row['cycle']['pair']) or row['cycle']['status'] != ('qualified' if qualified else 'unqualified'):
        raise ValueError('compact primitive-cycle qualification differs')
    for candidate,fold in zip(folds,row['folds'],strict=True):
        solvers = [dict(method=r['method'],qualification={k:v for k,v in r.items() if k != 'method'})
            for r in fold['solvers']]
        rebuilt = dict(run.base.compare(candidate,solvers,numerical['fold']),parent_id=candidate['parent_id'])
        if not equal(rebuilt,fold):
            raise ValueError('compact fold qualification differs')
    cycles = [dict(method=v['method'],phase=w['phase'],states=w['event_states']['historical'])
        for v in row['cycle']['profiles'] for w in v['metric']['windows']] if qualified else []
    for candidate,boundary in zip(boundaries,row['boundaries'],strict=True):
        if run.base.boundary_analysis.compare(boundary['profiles'],candidate,cycles) != boundary['comparison']:
            raise ValueError('compact boundary qualification differs')
    rebuilt = run.base.summarize(numerical,row['cycle'],row['folds'],row['boundaries'])
    if any(not equal(v,row[k]) for k,v in rebuilt.items()):
        raise ValueError('compact point residuals or gates differ')
    if row['contact'] is not None and not equal(raw_audit.point_audit.old.scalar_contact(row['folds'],row['cycle']),row['contact']):
        raise ValueError('separate scalar fold comparison differs')


def verify(path,expected_sha):
    path = Path(path)
    if sha256(path) != expected_sha:
        raise ValueError('public receipt hash differs')
    saved = json.loads(path.read_bytes())
    p,numerical,old = run.load(),run.base.load(),run.inputs()
    run.public.verify(run.ROOT/run.RECEIPT,run.INPUTS[run.RECEIPT])
    if (saved['experiment_id'] != 'EXP-504' or saved['passed'] is not True
            or saved['source_commit'] != SOURCE or saved['plan_sha256'] != sha256(run.PLAN)
            or saved['audit_source_sha256'] != sha256(Path(raw_audit.__file__))
            or saved['inputs'] != run.INPUTS or saved['ledger'] != numerical['ledger']
            or saved['symbolic_chains_verified'] is not False or saved['new_integrations'] != 0
            or saved['paid_review'] != p['paid_review']):
        raise ValueError('public experiment, source or claim binding differs')
    result = saved['result']
    state = run.model.initialize(numerical,old)
    if not equal(state,result['initialization']) or len(result['steps']) != len(saved['point_counts']):
        raise ValueError('initialization or complete count ledger differs')
    current,models = old['proposal'],state['models']
    progress = run.model.ledger()
    reason,index = 'eight-step-limit',0
    rebuilt_steps = []
    for number in range(1,9):
        proposal = run.model.propose(models,state['signs'],current,state['keys'],numerical['anchor'],number)
        slot = progress[number-1]
        slot['proposal'] = proposal
        if not proposal['qualified']:
            slot['reason'] = proposal['reason']
            reason = 'proposal-gate-failed'
            break
        if index >= len(result['steps']):
            raise ValueError('missing required path point')
        entry = result['steps'][index]
        # Compare the computed proposal numerically, but replay the actual saved
        # binary64 parameter displacement; never alter the measured point bytes.
        if not equal(proposal,entry['proposal']) or entry['point']['spec'] != entry['proposal']['spec']:
            raise ValueError('sole sequential proposal differs')
        point = entry['point']
        check_point(point,run.model.warm_plan(numerical,current),saved['point_counts'][index])
        decision = run.model.decide(numerical,state,models,current,point,entry['proposal'])
        if not equal(decision,entry['decision']):
            raise ValueError('compact model or acceptance decision differs')
        rebuilt_steps.append(dict(entry,decision=decision))
        slot.update(status='completed',accepted=decision['accepted'])
        index += 1
        if not decision['accepted']:
            reason = 'measured-step-rejected'
            break
        current,models = point,decision['updated_models']
        if point['joint_proximity']:
            reason = 'joint-proximity'
            break
    for slot in progress:
        if slot['status'] == 'not-run' and slot['reason'] is None:
            slot['reason'] = reason
    analysis = run.model.verdict(old['proposal'],rebuilt_steps,reason)
    calls = sum(r['target_ivps'] for r in saved['point_counts'])
    if (index != len(result['steps']) or not equal(progress,saved['progress'])
            or not equal(analysis,result['analysis']) or calls != saved['target_ivps']
            or not 0 <= calls <= p['limits']['target_ivps']):
        raise ValueError('path stopping, complete ledger or accounting differs')
    return dict(passed=True,experiment_id='EXP-504',points=index,target_ivps=calls,analysis=analysis,
        new_integrations=0,full_raw_audit_repeated=False,symbolic_chains_verified=False,
        floating_replay_tolerance=dict(rtol=1e-12,atol=1e-13,discrete_gates='exact'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result',type=Path,required=True)
    parser.add_argument('--expected-sha256',required=True)
    a = parser.parse_args()
    print(json.dumps(verify(a.result,a.expected_sha256),sort_keys=True))


if __name__ == '__main__':
    main()
