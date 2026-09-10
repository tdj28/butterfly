#!/usr/bin/env python3
"""Public prefix/coverage replay with explicit reuse; no raw-artifact dependency."""
import argparse
import json
from pathlib import Path
import numpy as np
from butterfly._paired_startup import sha256
from scripts import run_exp512_censored_returns as run

SOURCE = '1e602474ffc17f2fc15298d3fdae1663e851c47f'


def measurement(profile,spec,settings):
    c,u = spec['candidate'],spec['u']
    if profile['status']=='integration-failed':
        products = {'guard integration failed':['guard'],'census integration failed':['guard','main']}
        if profile.get('reason') not in products or profile['products']!=products[profile['reason']]:
            raise ValueError('public failed extension accounting differs')
        return profile
    if profile['status']!='completed' or profile['products']!=['guard','main']:
        raise ValueError('unknown or incomplete public extension')
    rhs,_,section = run.prior.fields(c)
    r = profile['report']
    initial = (np.asarray(c['initial_state'])+u*np.asarray(c['initial_tangent'])).tolist()
    if (r['initial_state']!=initial or r['initial_tangent']!=c['initial_tangent'] or r['method']!=profile['method']
            or r['horizon']!=c['horizon'] or r['numerical_all_root_proof'] is not False
            or any(r[k]!=settings[k] for k in ('rtol','atol','max_step','guard'))):
        raise ValueError('public extension configuration differs')
    knots = np.unique([settings['guard'],*[e['time'] for e in r['extrema']],c['horizon']]).tolist()
    values = r['knot_values']
    if (r['knots']!=knots or len(values)!=len(knots) or not np.isfinite(values).all()
            or [e['bracket'] for e in r['reconstructed']]!=[[a,b] for a,b,x,y in zip(knots[:-1],knots[1:],values[:-1],values[1:],strict=True) if x*y<0]
            or r['uncertain_extrema']!=[dict(time=e['time'],plane_value=e['plane_value'],state=e['state'])
                for e in r['extrema'] if abs(e['plane_value'])<=settings['extremum_margin']]):
        raise ValueError('public extension event partition differs')
    for event in r['reconstructed']:
        if not np.isfinite([event['time'],*event['state'],*event['raw_tangent'],event['angle'],event['residual']]).all():
            raise ValueError('nonfinite public extension event')
        field = rhs(event['time'],np.asarray(event['state']))
        velocity = float(np.asarray(section.normal)@field)
        angle = abs(velocity)/(np.linalg.norm(section.normal)*np.linalg.norm(field))
        if (event['accepted']!=bool(section.accepts(event['state']) and section.direction*velocity>0)
                or abs(event['residual']-section.value(event['state']))>1e-12
                or abs(event['normal_velocity']-velocity)>1e-12 or abs(event['angle']-angle)>1e-12
                or not event['bracket'][0]<event['time']<event['bracket'][1]):
            raise ValueError('public extension event algebra differs')
    measured = run.prior.model.observation(r,c,rhs,section,settings['thresholds'])
    if not run.prior.public.equal(measured,profile['measurement']):
        raise ValueError('public extension measurement differs')
    return dict(profile,measurement=measured)


def verify(path,expected_sha):
    path = Path(path)
    if sha256(path)!=expected_sha:
        raise ValueError('public extension receipt byte identity differs')
    saved = json.loads(path.read_bytes())
    p,previous = run.load(),run.inputs()
    if (saved['experiment_id']!='EXP-512' or saved['passed'] is not True or saved['protocol_compliant'] is not True
            or saved['source_commit']!=SOURCE or saved['plan_sha256']!=sha256(run.PLAN) or saved['inputs']!=run.INPUTS
            or saved['paid_review']!=p['paid_review'] or saved['new_integrations']!=0 or saved['symbolic_chains_verified'] is not False
            or type(saved['target_ivps']) is not int or not 0<saved['target_ivps']<=p['limits']['target_ivps']
            or saved['reused_target_ivps']!=160 or saved['controls']!=previous['controls']
            or type(saved['output_bytes_including_summary']) is not int
            or not 0<saved['output_bytes_including_summary']<=p['limits']['output_bytes']
            or saved['output_limit_bytes']!=p['limits']['output_bytes']):
        raise ValueError('public extension source/resource/claim binding differs')
    if [(r['curve'],r['node']) for r in saved['extensions']]!=[(s['curve'],s['node']) for s in p['selection']]:
        raise ValueError('complete public extension matrix required')
    extensions,calls = [],0
    for spec,row in zip(p['selection'],saved['extensions'],strict=True):
        if [v['method'] for v in row['profiles']]!=p['solvers']:
            raise ValueError('complete public extension solver pair required')
        profiles = [measurement(profile,spec,p['numerical']) for profile in row['profiles']]
        calls+=sum(len(v['products']) for v in profiles)
        old = previous['rows'][spec['curve']]['samples'][spec['node']]
        prefixes = [run.model.prefix(a,b,p['numerical']['thresholds']) for a,b in zip(old['profiles'],profiles,strict=True)]
        if not run.prior.public.equal(prefixes,row['prefixes']):
            raise ValueError('public historical prefix check differs')
        extensions.append(dict(curve=spec['curve'],node=spec['node'],profiles=profiles,prefixes=prefixes))
    result = run.model.assemble(previous,extensions,p['selection'],run.prior.load()['selection']['targets'],p['numerical'])
    for row in result['rows']:
        run.previous_audit.scalar_check(row['candidate'],row['samples'],run.prior.load()['selection']['targets'],row['analysis'])
    if calls!=saved['target_ivps'] or not run.prior.public.equal(result,saved['result']):
        raise ValueError('public complete-grid reuse/decision/accounting differs')
    return dict(experiment_id='EXP-512',passed=True,all_prefixes_preserved=result['all_prefixes_preserved'],
        all_ninth_returns_observed=result['all_ninth_returns_observed'],
        analyses=[r['analysis'] for r in result['rows']],full_raw_audit_repeated=False,new_integrations=0,
        symbolic_chains_verified=False,scope='Compact new-event/prefix and mixed-provenance grid replay. Neither new nor old dense raw-data audit is repeated here.')


if __name__=='__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result',type=Path,required=True)
    p.add_argument('--expected-sha256',required=True)
    a = p.parse_args()
    r = verify(a.result,a.expected_sha256)
    print(json.dumps(dict(r,analyses=[dict(family_id=v['family_id'],regular_samples=v['regular_samples'],
        matched_candidate_brackets=v['matched_candidate_brackets']) for v in r['analyses']]),sort_keys=True))
