#!/usr/bin/env python3
"""Compact midpoint, qualification and reference replay; no raw files needed."""
import argparse
import json
from pathlib import Path
from butterfly._paired_startup import sha256
from scripts import run_exp513_candidate_folds as run
from scripts import audit_exp513_candidate_folds as audit

SOURCE='dcf9d2bdb437960498d461b6e03a9dc69d38112f'
equal=run.coverage.public.equal


def verify(path,expected_sha):
    path=Path(path)
    if sha256(path)!=expected_sha:
        raise ValueError('public receipt byte identity differs')
    saved=json.loads(path.read_bytes())
    p=run.load()
    if (saved['experiment_id']!='EXP-513' or saved['passed'] is not True or saved['protocol_compliant'] is not True
            or saved['source_commit']!=SOURCE or saved['inputs']!=run.INPUTS or saved['plan_sha256']!=sha256(run.PLAN)
            or saved['new_integrations']!=0 or saved['symbolic_chains_verified'] is not False
            or saved['paid_review']!=p['paid_review'] or type(saved['target_ivps']) is not int
            or not 0<saved['target_ivps']<=p['limits']['target_ivps']
            or type(saved['output_bytes_including_summary']) is not int
            or not 0<saved['output_bytes_including_summary']<=p['limits']['output_bytes']
            or saved['output_limit_bytes']!=p['limits']['output_bytes']
            or [r['candidate'] for r in saved['rows']]!=p['candidates']):
        raise ValueError('public source, matrix, resource or claim binding differs')
    calls=0
    for c,row in zip(p['candidates'],saved['rows'],strict=True):
        if [v['method'] for v in row['midpoints']]!=p['solvers']:
            raise ValueError('complete midpoint solver matrix required')
        profiles=[run.public.measurement(v,dict(candidate=c,u=c['seed_u']),p['numerical']) for v in row['midpoints']]
        calls+=sum(len(v['products']) for v in profiles)
        seeded,pair=run.model.seed(c,profiles,p['numerical'])
        if not equal(seeded,row['seeded_candidate']) or not equal(pair,row['midpoint_pair']):
            raise ValueError('public midpoint seed differs')
        if seeded is None:
            if row['status']!='midpoint-unqualified' or row['folds'] is not None or row['assessment'] is not None:
                raise ValueError('unqualified midpoint promoted to search')
            continue
        if row['status']!='searched' or [v['method'] for v in row['folds']]!=p['solvers']:
            raise ValueError('complete fold solver matrix required')
        rhs,_,section=run.coverage.fields(seeded)
        for profile in row['folds']:
            shooting=profile['shooting']
            trace=shooting['trace']
            if (not 1<=len(trace)<=p['numerical']['iterations']
                    or shooting['retained_labels']!=[f'newton-{i}' for i in range(len(trace))]
                    or trace[0]['u']!=seeded['seed_u'] or trace[0]['time']!=seeded['seed_time']):
                raise ValueError('public shooting inventory/seed differs')
            if shooting['reason']=='fixed search box exceeded':
                last=trace[-1]
                u,t=[last[k]-last['newton_step'][i] for i,k in enumerate(('u','time'))]
                if (seeded['u_box'][0]<=u<=seeded['u_box'][1]
                        and seeded['time_box'][0]<=t<=seeded['time_box'][1] and t>0):
                    raise ValueError('unfounded public search-box failure')
            expected_offsets=[]
            if shooting['converged']:
                u=trace[-1]['u']
                if seeded['u_box'][0]<=u-seeded['epsilon']<u+seeded['epsilon']<=seeded['u_box'][1]:
                    expected_offsets=[-seeded['epsilon'],0.,seeded['epsilon']]
            if [v['offset'] for v in profile['censuses']]!=expected_offsets:
                raise ValueError('prescribed census eligibility differs')
            for census in profile['censuses']:
                report=census['report']
                measurement=run.coverage.model.observation(report,seeded,rhs,section,p['numerical']['thresholds'])
                run.public.measurement(dict(method=profile['method'],status='completed',products=['guard','main'],
                    report=report,measurement=measurement),dict(candidate=seeded,u=trace[-1]['u']+census['offset']),p['numerical'])
            qualification=run.base.previous.folds_run.qualify(shooting,profile['censuses'],seeded,rhs,section,p['numerical'])
            if not equal(qualification,profile['qualification']):
                raise ValueError('public fold qualification differs')
            calls+=len(trace)+2*len(profile['censuses'])
        decision=run.assess(seeded,row['folds'],p)
        if not equal(decision,row['assessment']):
            raise ValueError('public prefix/reference assessment differs')
        audit.scalar_distances(row,p['targets'],p['numerical']['scales'])
    if calls!=saved['target_ivps']:
        raise ValueError('reported integration accounting differs')
    return dict(experiment_id='EXP-513',passed=True,candidates=len(saved['rows']),
        searched=sum(r['status']=='searched' for r in saved['rows']),
        qualified=sum(bool(r['assessment'] and r['assessment']['qualified']) for r in saved['rows']),
        reference_restored=sum(bool(r['assessment'] and r['assessment']['reference_restored']) for r in saved['rows']),
        full_raw_audit_repeated=False,new_integrations=0,symbolic_chains_verified=False,
        scope='Compact midpoint/event/qualification and full-state reference decisions replayed. Shooting meshes/algebra, raw census polynomials, control bundles and disk bytes are not independently audited here.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result',type=Path,required=True)
    p.add_argument('--expected-sha256',required=True)
    a=p.parse_args()
    print(json.dumps(verify(a.result,a.expected_sha256),sort_keys=True))
