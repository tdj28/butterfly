"""Prospective extension of all censored samples, with explicit historical reuse."""
from copy import deepcopy
import numpy as np
from scripts import exp511_curve_coverage as curve


def selection(previous):
    result = []
    for i,row in enumerate(previous['rows']):
        for j,sample in enumerate(row['samples']):
            missing = [p['status']=='completed' and p['measurement']['image']['status']!='returned'
                for p in sample['profiles']]
            if any(missing):
                if missing!=[True,True] or [p['method'] for p in sample['profiles']]!=['DOP853','Radau']:
                    raise ValueError('complete censored solver pair required')
                for p in sample['profiles']:
                    if sum(e['accepted'] for e in p['report']['reconstructed'])!=8 or p['report']['uncertain_extrema']:
                        raise ValueError('eight-return censored witness required')
                candidate = deepcopy(row['candidate'])
                candidate['horizon']+=15.
                result.append(dict(curve=i,node=j,u=sample['u'],candidate=candidate,
                    original_horizon=row['candidate']['horizon']))
    if [(s['curve'],s['node']) for s in result]!=[(0,1),(0,16),(0,17),(0,18),(0,19),(1,18),(1,19)]:
        raise ValueError('complete seven-sample censoring matrix differs')
    return result


def prefix(previous,current,thresholds):
    result = dict(passed=False,state_difference=None,time_difference=None,tangent_difference=None,
        reason='new profile failed or missing saved prefix')
    if current['status']!='completed':
        return result
    old = [e for e in previous['report']['reconstructed'] if e['accepted']]
    new = [e for e in current['report']['reconstructed'] if e['accepted'] and e['time']<=previous['report']['horizon']]
    if len(old)!=8 or len(new)!=8 or current['method']!=previous['method']:
        return result
    if any(e['time']<=previous['report']['horizon'] for e in current['report']['uncertain_extrema']):
        return dict(result,reason='uncertain historical prefix')
    metrics = []
    for a,b in zip(old,new,strict=True):
        values = [*a['state'],*b['state'],*a['raw_tangent'],*b['raw_tangent'],a['time'],b['time']]
        if not np.isfinite(values).all():
            raise ValueError('nonfinite prefix comparison')
        state = float(np.max(abs((np.asarray(a['state'])-b['state'])/[15.,15.,.01])))
        va,vb = [np.asarray(e['raw_tangent'])/[15.,15.,.01] for e in (a,b)]
        tangent = float(np.max(abs(va-vb))/max(1.,float(np.max(abs(va))),float(np.max(abs(vb)))))
        metrics.append((state,abs(a['time']-b['time']),tangent))
    state,time,tangent = np.max(metrics,axis=0).tolist()
    passed = state<=thresholds['state'] and time<=thresholds['time'] and tangent<=1e-6
    return dict(passed=passed,state_difference=state,time_difference=time,tangent_difference=tangent,
        reason=None if passed else 'historical prefix disagreement')


def assemble(previous,extensions,selection,targets,settings):
    if [(r['curve'],r['node']) for r in extensions]!=[(s['curve'],s['node']) for s in selection]:
        raise ValueError('complete fixed extension matrix required')
    rows = deepcopy(previous['rows'])
    for spec,row in zip(selection,extensions,strict=True):
        old = previous['rows'][spec['curve']]['samples'][spec['node']]
        if [p['method'] for p in row['profiles']]!=['DOP853','Radau']:
            raise ValueError('complete extension solver pair required')
        prefixes = [prefix(a,b,settings['thresholds']) for a,b in zip(old['profiles'],row['profiles'],strict=True)]
        if row['prefixes']!=prefixes:
            raise ValueError('prefix verdict differs')
        pair = curve.pair(row['profiles'],settings['scales'])
        if not all(p['passed'] for p in prefixes):
            pair.update(regular=False,reason='historical prefix disagreement')
        rows[spec['curve']]['samples'][spec['node']] = dict(u=spec['u'],profiles=row['profiles'],pair=pair)
    for row in rows:
        row['analysis'] = curve.analyze(row['candidate'],row['samples'],targets)
    return dict(rows=rows,reused_samples=33,extended_samples=7,
        all_prefixes_preserved=all(p['passed'] for r in extensions for p in r['prefixes']),
        all_ninth_returns_observed=all(p['status']=='completed' and p['measurement']['image']['status']=='returned'
            for r in extensions for p in r['profiles']),
        symbolic_chains_verified=False,scope='New mixed-provenance diagnostic grid: 33 unchanged EXP-511 samples and seven explicitly extended samples. No old result is relabeled; no continuous-u or symbolic proof.')
