"""Fixed candidate selection and qualification; no global-absence inference."""
from copy import deepcopy
import math
import numpy as np
from scripts import exp511_curve_coverage as curve


def selection(previous):
    chosen = []
    for direction,row in enumerate(previous['result']['rows']):
        for ordinal,indices in enumerate(row['analysis']['matched_candidate_brackets']):
            endpoints = [row['samples'][i] for i in indices]
            if not all(s['pair']['regular'] for s in endpoints):
                raise ValueError('regular endpoint pairs required')
            c = deepcopy(row['candidate'])
            c.pop('grid',None)
            c.update(id=f'exp513-direction-{direction}-candidate-{ordinal}',indices=indices,
                direction=direction,u_box=[s['u'] for s in endpoints],
                horizon=max(p['report']['horizon'] for s in endpoints for p in s['profiles']))
            c['seed_u']=math.fsum(c['u_box'])/2
            c['seed_time']=None
            c['time_box']=[1e-8,c['horizon']]
            if not c['u_box'][0]<c['seed_u']-c['epsilon']<c['seed_u']+c['epsilon']<c['u_box'][1]:
                raise ValueError('fixed perturbations must fit interval')
            chosen.append(c)
    if [(c['direction'],c['indices']) for c in chosen]!=[(0,[1,2]),(0,[15,16]),(0,[16,17]),(1,[17,18]),(1,[18,19])]:
        raise ValueError('complete five-candidate matrix required')
    return chosen


def seed(candidate,profiles,p):
    pair = curve.pair(profiles,p['scales'])
    if not pair['regular']:
        return None,pair
    times = [v['measurement']['image']['events'][-1]['time'] for v in profiles]
    c = dict(candidate,seed_time=math.fsum(times)/2)
    if not c['time_box'][0]<c['seed_time']<c['time_box'][1]:
        raise ValueError('midpoint return outside time box')
    return c,pair


def assessment(candidate,rows,comparison,targets,p,rhs,section):
    if [r['method'] for r in rows]!=p['solvers'] or len(targets)!=4:
        raise ValueError('complete solver/reference matrix required')
    prefix_pairs=[]
    if all(r['qualification']['qualified'] for r in rows):
        if any([v['offset'] for v in r['censuses']]!=[-candidate['epsilon'],0.,candidate['epsilon']] for r in rows):
            raise ValueError('complete prescribed census offsets required')
        for i in range(3):
            profiles=[dict(method=r['method'],status='completed',
                measurement=curve.observation(r['censuses'][i]['report'],candidate,rhs,section,p['thresholds'])) for r in rows]
            prefix_pairs.append(curve.pair(profiles,p['scales']))
    qualified=bool(comparison['qualified'] and len(prefix_pairs)==3 and all(v['regular'] for v in prefix_pairs))
    distances=[]
    if qualified:
        for row in rows:
            observation=row['qualification']['observations'][1]
            for target in targets:
                values={k:float(np.max(abs((np.asarray(observation[k])-target[k])/p['scales'])))
                    for k in ('image_state','next_state')}
                if not np.isfinite(list(values.values())).all():
                    raise ValueError('nonfinite reference distance')
                distances.append(dict(method=row['method'],target_id=target['id'],target_method=target['method'],**values))
    restored=bool(qualified and len(distances)==8 and all(max(v['image_state'],v['next_state'])<=1e-6 for v in distances))
    return dict(qualified=qualified,reference_restored=restored,prefix_pairs=prefix_pairs,reference_distances=distances,
        symbolic_chains_verified=False,global_root_absence_proved=False)


def follow(candidates,probe,shoot,assess):
    """Same fixed sequence in production and target-free controller tests."""
    results=[]
    for c in candidates:
        seeded,midpoints,pair=probe(c)
        if seeded is None:
            results.append(dict(candidate=c,midpoints=midpoints,midpoint_pair=pair,
                status='midpoint-unqualified',seeded_candidate=None,folds=None,assessment=None))
            continue
        folds=shoot(seeded)
        results.append(dict(candidate=c,midpoints=midpoints,midpoint_pair=pair,
            status='searched',seeded_candidate=seeded,folds=folds,assessment=assess(seeded,folds)))
    return results
