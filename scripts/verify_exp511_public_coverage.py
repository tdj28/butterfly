#!/usr/bin/env python3
"""Replay public curve measurements and comparisons, not unavailable raw data."""
import argparse
import json
from pathlib import Path
import numpy as np
from butterfly._paired_startup import sha256
from scripts import run_exp511_curve_coverage as run
from scripts import audit_exp511_curve_coverage as audit

SOURCE = '273e5f5ba6819478ad7d2372fcfdcb1423be9f53'


def verify(path,expected_sha):
    path = Path(path)
    if sha256(path)!=expected_sha:
        raise ValueError('public coverage receipt byte identity differs')
    saved = json.loads(path.read_bytes())
    p = run.load()
    if (saved['experiment_id']!='EXP-511' or saved['passed'] is not True or saved['protocol_compliant'] is not True
            or saved['source_commit']!=SOURCE or saved['plan_sha256']!=sha256(run.PLAN) or saved['inputs']!=run.INPUTS
            or saved['new_integrations']!=0 or saved['symbolic_chains_verified'] is not False
            or saved['paid_review']!=p['paid_review'] or type(saved['target_ivps']) is not int
            or not 0<saved['target_ivps']<=p['limits']['target_ivps']
            or type(saved['output_bytes_including_summary']) is not int
            or not 0<saved['output_bytes_including_summary']<=p['limits']['output_bytes']
            or saved['output_limit_bytes']!=p['limits']['output_bytes']):
        raise ValueError('public source/resource/claim binding differs')
    control = saved['controls']
    if (control['passed'] is not True or control['control_ivps']!=12 or control['new_integrations']!=0
            or control['source_hashes']!={n:sha256(run.ROOT/n) for n in p['source_paths']}
            or control['full_dense_replay'] is not True
            or [(r['kind'],r['method']) for r in control['rows']]!=[(k,m) for k in p['controls']['kinds'] for m in p['solvers']]):
        raise ValueError('public control identity differs')
    for row in control['rows']:
        verdict = row['verdict']
        if (verdict['passed'] is not True or verdict['regular']!=(row['kind']!='projection-degenerate')
                or len(verdict['errors'])!=3 or not np.isfinite(verdict['errors']).all()
                or min(verdict['errors'])<0 or max(verdict['errors'])>1e-8):
            raise ValueError('public analytic control verdict differs')
    if len(saved['rows'])!=2:
        raise ValueError('complete two-curve matrix required')
    calls,analyses = 0,[]
    for c,row in zip(p['selection']['curves'],saved['rows'],strict=True):
        if row['candidate']!=c or [s['u'] for s in row['samples']]!=c['grid']:
            raise ValueError('complete fixed curve/grid identity differs')
        rhs,_,section = run.fields(c)
        samples = []
        for sample in row['samples']:
            if [v['method'] for v in sample['profiles']]!=p['solvers']:
                raise ValueError('complete solver pair required')
            profiles = []
            for profile in sample['profiles']:
                if profile['status']=='completed':
                    report = profile['report']
                    initial = (np.asarray(c['initial_state'])+sample['u']*np.asarray(c['initial_tangent'])).tolist()
                    if (profile['products']!=['guard','main'] or report['method']!=profile['method']
                            or report['initial_state']!=initial or report['initial_tangent']!=c['initial_tangent']
                            or report['horizon']!=c['horizon'] or report['numerical_all_root_proof'] is not False
                            or any(report[k]!=p['numerical'][k] for k in ('rtol','atol','max_step','guard'))):
                        raise ValueError('public profile configuration differs')
                    knots = np.unique([p['numerical']['guard'],*[e['time'] for e in report['extrema']],c['horizon']]).tolist()
                    values = report['knot_values']
                    if (report['knots']!=knots or len(values)!=len(knots) or not np.isfinite(values).all()
                            or [e['bracket'] for e in report['reconstructed']]!=[[a,b] for a,b,x,y in zip(knots[:-1],knots[1:],values[:-1],values[1:],strict=True) if x*y<0]
                            or report['uncertain_extrema']!=[dict(time=e['time'],plane_value=e['plane_value'],state=e['state'])
                                for e in report['extrema'] if abs(e['plane_value'])<=p['numerical']['extremum_margin']]):
                        raise ValueError('public event partition differs')
                    for event in report['reconstructed']:
                        if not np.isfinite([event['time'],*event['state'],*event['raw_tangent'],event['angle'],event['residual']]).all():
                            raise ValueError('nonfinite public event')
                        field = rhs(event['time'],np.asarray(event['state']))
                        velocity = float(np.asarray(section.normal)@field)
                        angle = abs(velocity)/(np.linalg.norm(section.normal)*np.linalg.norm(field))
                        accepted = bool(section.accepts(event['state']) and section.direction*velocity>0)
                        if (event['accepted']!=accepted or abs(event['residual']-section.value(event['state']))>1e-12
                                or abs(event['normal_velocity']-velocity)>1e-12
                                or abs(event['angle']-angle)>1e-12
                                or not event['bracket'][0]<event['time']<event['bracket'][1]):
                            raise ValueError('public event algebra differs')
                    measurement = run.model.observation(report,c,rhs,section,p['numerical']['thresholds'])
                    if not run.public.equal(measurement,profile['measurement']):
                        raise ValueError('public measurement differs')
                    profile = dict(profile,measurement=measurement)
                elif profile['status']=='integration-failed':
                    products = {'guard integration failed':['guard'],'census integration failed':['guard','main']}
                    if profile.get('reason') not in products or profile['products']!=products[profile['reason']]:
                        raise ValueError('public failed-profile accounting differs')
                else:
                    raise ValueError('unknown public profile status')
                calls+=len(profile['products'])
                profiles.append(profile)
            pair = run.model.pair(profiles,p['numerical']['scales'])
            if not run.public.equal(pair,sample['pair']):
                raise ValueError('public solver agreement differs')
            samples.append(dict(u=sample['u'],profiles=profiles,pair=pair))
        analysis = run.model.analyze(c,samples,p['selection']['targets'])
        audit.scalar_check(c,samples,p['selection']['targets'],analysis)
        if not run.public.equal(analysis,row['analysis']):
            raise ValueError('public curve analysis differs')
        analyses.append(analysis)
    if calls!=saved['target_ivps']:
        raise ValueError('complete public IVP accounting differs')
    return dict(experiment_id='EXP-511',passed=True,analyses=analyses,
        full_raw_audit_repeated=False,new_integrations=0,symbolic_chains_verified=False,
        scope='Compact event-to-curve and bracket/state comparisons replayed. Dense meshes, IVP execution and on-disk bytes are not independently remeasured here.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result',type=Path,required=True)
    parser.add_argument('--expected-sha256',required=True)
    a = parser.parse_args()
    result = verify(a.result,a.expected_sha256)
    print(json.dumps(dict(result,analyses=[dict(family_id=r['family_id'],regular_samples=r['regular_samples'],
        matched_candidate_brackets=r['matched_candidate_brackets']) for r in result['analyses']]),sort_keys=True))


if __name__=='__main__':
    main()
