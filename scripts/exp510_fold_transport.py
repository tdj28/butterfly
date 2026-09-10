"""Four fixed substeps, with every fold representation retained at each step."""
from copy import deepcopy
import math
import numpy as np


def specifications(start, finish):
    if start['b'] != finish['b'] or start['b'] != .2 or not finish['c'] < start['c']:
        raise ValueError('fixed-b lower-c endpoint required')
    return [dict(id=f'substep-{i}',parameters=(dict(finish) if i == 4 else
        {k:math.fsum([start[k],(finish[k]-start[k])*i/4]) for k in ('a','b','c')})) for i in range(1,5)]


def candidates(numerical, previous, spec, section_offset):
    rows = deepcopy(numerical['fold_candidates'])
    if len(previous) != 4 or not all(r['qualified_in_region'] for r in previous):
        raise ValueError('all four qualified predecessor folds required')
    for c,r in zip(rows,previous,strict=True):
        if c['id'] != r['id'] or [v['method'] for v in r['solvers']] != ['DOP853','Radau']:
            raise ValueError('complete fold identity/method matrix required')
        u,t = [math.fsum(v['root'][k] for v in r['solvers'])/2 for k in ('u','time')]
        c.update(parameters=spec['parameters'],seed_u=u,seed_time=t,
            u_box=[u-.02,u+.02],time_box=[t-1,t+1],horizon=t+3)
        c['initial_state'][1] = section_offset
    return rows


def assess(previous, current, scales):
    if len(current) != 4 or [r['id'] for r in current] != [r['id'] for r in previous]:
        raise ValueError('complete ordered four-fold matrix required')
    qualified = all(r['qualified_in_region'] for r in current)
    result = dict(qualified=bool(qualified),transport_qualified=False,
        cross_history_spread=None,adjacent_displacement=None,reason='fold-unqualified')
    if not qualified:
        return result
    def states(rows,key):
        return np.asarray([v['observations'][1][key] for r in rows for v in r['solvers']])/scales
    spread = max(float(np.max(np.ptp(states(current,k),axis=0))) for k in ('image_state','next_state'))
    change = max(float(np.max(abs(states(current,k)-states(previous,k)))) for k in ('image_state','next_state'))
    if not math.isfinite(spread) or not math.isfinite(change):
        raise ValueError('nonfinite branch identity metric')
    passed = spread <= 1e-6 and change <= .01
    return dict(result,transport_qualified=passed,cross_history_spread=spread,
        adjacent_displacement=change,reason=None if passed else 'cross-history or adjacent identity failed')


def follow(numerical, start, finish, offset, measure):
    previous = start['folds']
    rows = []
    progress = [dict(id=f'substep-{i}',status='not-run',reason=None) for i in range(1,5)]
    for i,spec in enumerate(specifications(start['spec']['parameters'],finish)):
        proposed = candidates(numerical,previous,spec,offset(spec['parameters']))
        progress[i]['status'] = 'started'
        measured = measure(spec,proposed)
        decision = assess(previous,measured,numerical['fold']['scales'])
        rows.append(dict(spec=spec,folds=measured,decision=decision))
        progress[i]['status'] = 'completed'
        if not decision['transport_qualified']:
            for item in progress[i+1:]:
                item['reason'] = 'predecessor-unqualified'
            break
        previous = measured
    return dict(rows=rows,progress=progress,transport_completed=bool(len(rows)==4 and rows[-1]['decision']['transport_qualified']),
        symbolic_chains_verified=False,scope='Finite four-substep fold transport only; not exact contact, a generating partition or a symbolic chain.')
