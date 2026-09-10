"""Prospective two-step transport of the EXP-517 four-curve matrix.

Pure controller/identity arithmetic only: no target integration or word input.
"""
from copy import deepcopy
import math

CASES=[(4,0),(4,1),(7,0),(7,1)]
METHODS=['DOP853','Radau']
SCALES=[15.,15.,.01]


def matrix(rows):
    if [(r['candidate']['history'],r['candidate']['direction']) for r in rows]!=CASES:
        raise ValueError('complete ordered four-history/direction matrix required')
    if len({r['candidate']['id'] for r in rows})!=4:
        raise ValueError('unique candidate identifiers required')
    parameters=rows[0]['candidate']['parameters']
    if any(r['candidate']['parameters']!=parameters for r in rows):
        raise ValueError('all representations must use the same parameter point')
    return parameters


def specifications(old_specs,start):
    if len(old_specs)!=4 or [s['id'] for s in old_specs]!=[f'substep-{i}' for i in range(1,5)]:
        raise ValueError('complete original four-substep design required')
    if old_specs[1]['parameters']!=start:
        raise ValueError('EXP-517 must start at the exact second parameter substep')
    previous=start
    for spec in old_specs[2:]:
        p=spec['parameters']
        if set(p)!={'a','b','c'} or not all(math.isfinite(v) for v in p.values()):
            raise ValueError('finite complete parameters required')
        if not p['b']==previous['b']==.2 or not p['c']<previous['c']:
            raise ValueError('fixed-b lower-c transport required')
        previous=p
    return deepcopy(old_specs[2:])


def states(rows):
    matrix(rows)
    values=[]
    for r in rows:
        if not r['assessment'] or not r['assessment']['qualified']:
            raise ValueError('qualified full-prefix fold required')
        if [p['method'] for p in r['folds']]!=METHODS:
            raise ValueError('both ordered solvers required')
        for p in r['folds']:
            q=p['qualification']
            if not q['qualified'] or len(q['observations'])!=3:
                raise ValueError('all prescribed local fold observations required')
            v=q['observations'][1]
            if any(len(v[k])!=3 or not all(math.isfinite(x) for x in v[k])
                   for k in ('image_state','next_state')):
                raise ValueError('finite complete full input/output state required')
            values.append(v)
    return values


def decision(previous,current,scales=SCALES):
    matrix(previous);matrix(current)
    if len(scales)!=3 or not all(math.isfinite(x) and x>0 for x in scales):
        raise ValueError('finite positive three-coordinate scales required')
    before=states(previous)
    qualified=all(r['assessment'] is not None and r['assessment']['qualified'] for r in current)
    result=dict(qualified=qualified,transport_qualified=False,cross_history_spread=None,
                adjacent_displacement=None,reason='fold-or-prefix-unqualified',
                original_eighth_return_restored=False,symbolic_chains_verified=False)
    if not qualified:
        return result
    after=states(current)
    spread=max((max(v[k][j] for v in after)-min(v[k][j] for v in after))/scales[j]
               for k in ('image_state','next_state') for j in range(3))
    change=max(abs(a[k][j]-b[k][j])/scales[j]
               for a,b in zip(before,after,strict=True)
               for k in ('image_state','next_state') for j in range(3))
    passed=spread<=1e-6 and change<=.01
    return dict(result,transport_qualified=passed,cross_history_spread=spread,
                adjacent_displacement=change,
                reason=None if passed else 'cross-history-or-adjacent-identity-failed')


def candidates(previous,spec,section_offset):
    if not decision(previous,previous)['transport_qualified']:
        raise ValueError('complete cross-qualified warm predecessor required')
    if not math.isfinite(section_offset):
        raise ValueError('finite section required')
    result=[]
    for row in previous:
        c=deepcopy(row['seeded_candidate'])
        roots=[p['shooting']['trace'][-1] for p in row['folds']]
        u,t=[math.fsum(r[k] for r in roots)/2 for k in ('u','time')]
        if not all(math.isfinite(v) for v in (u,t)) or t<=1:
            raise ValueError('finite qualified warm root required')
        c.update(id=f'exp518-{spec["id"]}-history-{c["history"]}-direction-{c["direction"]}',
                 family_id=f'exp518-history-{c["history"]}-direction-{c["direction"]}',
                 parent_id=row['candidate']['id'],parameters=deepcopy(spec['parameters']),
                 seed_u=u,seed_time=t,u_box=[u-.02,u+.02],time_box=[t-1,t+1],horizon=t+3)
        c['initial_state'][1]=section_offset
        result.append(c)
    return result


def follow(start,specs,offset,measure):
    if len(specs)!=2 or [s['id'] for s in specs]!=['substep-3','substep-4']:
        raise ValueError('exact two remaining stages required')
    previous=start
    rows=[]
    progress=[dict(id=s['id'],status='not-run',reason=None) for s in specs]
    for i,spec in enumerate(specs):
        proposed=candidates(previous,spec,offset(spec['parameters']))
        current=measure(spec,proposed)
        if [r['candidate'] for r in current]!=proposed:
            raise ValueError('measured complete candidate identity differs')
        check=decision(previous,current)
        rows.append(dict(spec=spec,rows=current,decision=check))
        progress[i]['status']='completed'
        if not check['transport_qualified']:
            for p in progress[i+1:]:p['reason']='predecessor-unqualified'
            break
        previous=current
    return dict(rows=rows,progress=progress,
                transport_completed=len(rows)==2 and rows[-1]['decision']['transport_qualified'],
                original_eighth_return_restored=False,symbolic_chains_verified=False)
