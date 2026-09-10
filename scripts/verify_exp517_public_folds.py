#!/usr/bin/env python3
"""Compact midpoint, qualification and reference replay; no raw files needed."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from butterfly._paired_startup import sha256
from scripts import run_exp517_candidate_folds as run
from scripts import audit_exp517_candidate_folds as audit
from scripts.audit_exp490_direct_folds import separate_algebra

SOURCE='147964cb89c5ac2611b8b2ab5aa24640ad9f85ea'
CONTROL_SHA='364823e4ddb92e98b05d3bea2cd3f184e49b0f0e0c8efd71bb79d056b2d8a6ce'
equal=run.coverage.public.equal


def finite_packet(value):
    if isinstance(value,float) and not math.isfinite(value):
        raise ValueError('nonfinite public packet value')
    if isinstance(value,dict):
        for child in value.values(): finite_packet(child)
    elif isinstance(value,list):
        for child in value: finite_packet(child)


def compact_trace(shooting,candidate,settings):
    """Replay saved scalar shooting algebra, but not the missing ODE meshes."""
    np=run.base.np
    parameters=run.base.RosslerParameters(**candidate['parameters'])
    _,_,section=run.coverage.fields(candidate)
    u,t=candidate['seed_u'],candidate['seed_time']
    for i,row in enumerate(shooting['trace']):
        if (row['iteration']!=i or row['u']!=u or row['time']!=t
                or not candidate['u_box'][0]<=u<=candidate['u_box'][1]
                or not candidate['time_box'][0]<=t<=candidate['time_box'][1]):
            raise ValueError('public Newton update or search box differs')
        if row.get('integration_failed'):
            if i!=len(shooting['trace'])-1 or shooting['converged'] or shooting['reason']!='integration failed':
                raise ValueError('invalid compact integration failure')
            return
        residual,matrix,scale=separate_algebra(row,parameters,section.offset)
        if (not np.isfinite(residual).all() or not np.isfinite(matrix).all()
                or not np.allclose(residual,row['residual'],rtol=1e-12,atol=1e-12)
                or not np.allclose(matrix,row['jacobian'],rtol=1e-12,atol=1e-10)
                or abs(row['determinant_scale']-scale)>1e-12*scale):
            raise ValueError('public separately evaluated shooting equations differ')
        f=run.base.rossler_rhs(t,np.asarray(row['state']),parameters)
        if abs(row['angle']-abs(f[1])/np.linalg.norm(f))>1e-12:
            raise ValueError('public root angle differs')
        if 'event_second_derivative' in row:
            first=np.asarray(row['first'])
            tau=-first[1]/f[1]
            moving=first+f*tau
            dvelocity=moving[0]+parameters.a*moving[1]
            curvature=(matrix[1,0]+matrix[1,1]*tau)/f[1]-residual[1]*dvelocity/f[1]**2
            if abs(curvature-row['event_second_derivative'])>1e-10*max(1.,abs(curvature)):
                raise ValueError('public event-curvature algebra differs')
        if 'newton_step' in row:
            step=np.linalg.solve(matrix,residual)
            if not np.allclose(step,row['newton_step'],rtol=1e-10,atol=1e-12):
                raise ValueError('public Newton step arithmetic differs')
            u,t=[float(row[k]-row['newton_step'][j]) for j,k in enumerate(('u','time'))]
    last=shooting['trace'][-1]
    converged=abs(last['residual'][0])<=settings['root_plane'] and abs(last['residual'][1])/last['determinant_scale']<=settings['root_determinant']
    if shooting['converged']!=converged:
        raise ValueError('public equation convergence label differs')


def verify(path,expected_sha):
    path=Path(path)
    if sha256(path)!=expected_sha:
        raise ValueError('public receipt byte identity differs')
    saved=json.loads(path.read_bytes())
    finite_packet(saved)
    p=run.load()
    if (saved['experiment_id']!='EXP-517' or saved['passed'] is not True or saved['protocol_compliant'] is not True
            or saved['source_commit']!=SOURCE or saved['inputs']!=run.INPUTS or saved['plan_sha256']!=sha256(run.PLAN)
            or saved['new_integrations']!=0 or saved['symbolic_chains_verified'] is not False
            or saved['paid_review']!=p['paid_review'] or type(saved['target_ivps']) is not int
            or not 0<saved['target_ivps']<=p['limits']['target_ivps']
            or type(saved['output_bytes_including_summary']) is not int
            or not 0<saved['output_bytes_including_summary']<=p['limits']['output_bytes']
            or saved['output_limit_bytes']!=p['limits']['output_bytes']
            or [r['candidate'] for r in saved['rows']]!=p['candidates']):
        raise ValueError('public source, matrix, resource or claim binding differs')
    control_bytes=(json.dumps(saved['controls'],sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    if hashlib.sha256(control_bytes).hexdigest()!=CONTROL_SHA:
        raise ValueError('reused compact control summary differs from the pre-target audit')
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
            compact_trace(shooting,seeded,p['numerical'])
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
    cross=run.model.cross_representation(saved['rows'],p['numerical']['scales'])
    if cross!=saved['cross_representation']:
        raise ValueError('complete cross-history/direction decision differs')
    if calls!=saved['target_ivps']:
        raise ValueError('reported integration accounting differs')
    return dict(experiment_id='EXP-517',passed=True,candidates=len(saved['rows']),
        cross_representation=cross, searched=sum(r['status']=='searched' for r in saved['rows']),
        qualified=sum(bool(r['assessment'] and r['assessment']['qualified']) for r in saved['rows']),
        reference_restored=sum(bool(r['assessment'] and r['assessment']['reference_restored']) for r in saved['rows']),
        full_raw_audit_repeated=False,new_integrations=0,symbolic_chains_verified=False,
        scope='Compact shooting algebra, midpoint/events, qualification and full-state reference decisions replayed. Raw shooting meshes, raw census polynomials, raw control bundles and disk bytes are not independently audited here.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result',type=Path,required=True)
    p.add_argument('--expected-sha256',required=True)
    a=p.parse_args()
    print(json.dumps(verify(a.result,a.expected_sha256),sort_keys=True))
