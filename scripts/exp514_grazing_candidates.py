"""Outcome-informed nomination of section tangencies, never projected folds."""
from copy import deepcopy
import math
from butterfly import event_boundary_shooting as boundary


def selection(old, new):
    chosen = []
    for row in new['rows']:
        c = deepcopy(row['candidate'])
        ends = [old['result']['rows'][c['direction']]['samples'][i] for i in c['indices']]
        mid = dict(u=c['seed_u'], profiles=row['midpoints'], pair=row['midpoint_pair'])
        points = [ends[0], mid, ends[1]]
        if not all(v['pair']['regular'] for v in points):
            raise ValueError('three regular paired observations required')
        halves = []
        for method in range(2):
            slopes = [v['profiles'][method]['measurement']['observation']['x_graph_slope'] for v in points]
            halves.append([i for i in (0, 1) if slopes[i]*slopes[i+1] < 0])
        if len(halves[0]) != 1 or halves[0] != halves[1]:
            raise ValueError('unique paired slope-sign half required')
        half = halves[0][0]
        left, right = points[half:half+2]
        reports = [v['profiles'][m]['report'] for v in (left, right) for m in range(2)]
        if len({len(r['extrema']) for r in reports}) != 1:
            raise ValueError('extremum ordinal alignment unavailable')
        flips = [[i for i, (a, b) in enumerate(zip(reports[m]['extrema'], reports[m+2]['extrema'], strict=True))
                  if a['plane_value']*b['plane_value'] < 0] for m in range(2)]
        if len(flips[0]) != 1 or flips[0] != flips[1]:
            raise ValueError('unique paired extremum sign change required')
        index = flips[0][0]
        extrema = [r['extrema'][index] for r in reports]
        prefixes = [sum(e['accepted'] and e['time'] < g['time']-.5 for e in r['reconstructed'])
                    for r, g in zip(reports, extrema, strict=True)]
        if len(set(prefixes)) != 1:
            raise ValueError('preceding accepted prefix differs')
        width = right['u']-left['u']
        c.update(id=c['id'].replace('exp513', 'exp514'), source_candidate_id=c['id'],
                 original_u_box=c['u_box'], half=half, extremum_index=index,
                 accepted_prefix=prefixes[0], u_box=[left['u'], right['u']],
                 seed_u=math.fsum([left['u'], right['u']])/2,
                 seed_time=math.fsum(v['time'] for v in extrema)/4,
                 time_box=[min(v['time'] for v in extrema)-.25, max(v['time'] for v in extrema)+.25],
                 doses=[-width/1000, -width/10000, width/10000, width/1000],
                 endpoint_extrema=extrema)
        chosen.append(c)
    if [(c['direction'], c['indices']) for c in chosen] != [(0,[1,2]), (0,[15,16]), (0,[16,17]), (1,[17,18]), (1,[18,19])]:
        raise ValueError('all five original intervals required')
    return chosen


def decision(c, roots, sides, p):
    """Numerical grazing and two-sided event mechanism, not chain verification."""
    pair = boundary.root_pair(roots, c, p)
    if pair['eligible']:
        if ([s['dose'] for s in sides] != c['doses']
                or any([v['method'] for v in s['profiles']] != p['solvers'] for s in sides)
                or any(s['u'] != pair['common_center_u']+s['dose'] for s in sides)):
            raise ValueError('complete prescribed common-input side matrix required')
    elif sides:
        raise ValueError('ineligible root pair has side products')
    failed = any(v['status'] != 'completed' for s in sides for v in s['profiles'])
    if failed:
        return dict(qualified=False, reason='side integration failed', analysis=None,
                    projected_fold_qualified=False, symbolic_chains_verified=False)
    compact = [dict(dose=s['dose'], u=s['u'], reports=[v['report'] for v in s['profiles']]) for s in sides]
    analysis = boundary.assess(roots, compact, c, p)
    return dict(qualified=analysis['qualified'], reason=analysis['reason'], analysis=analysis,
                projected_fold_qualified=False, symbolic_chains_verified=False)


def run_candidate(c, p, shoot, observe):
    """All roots then all four common-input sides; failures do not select doses."""
    roots = [dict(method=m, shooting=shoot(c, m)) for m in p['solvers']]
    pair = boundary.root_pair(roots, c, p)
    sides = []
    if pair['eligible']:
        for i, dose in enumerate(c['doses']):
            u = pair['common_center_u']+dose
            sides.append(dict(dose=dose, u=u, profiles=[observe(c, i, u, m) for m in p['solvers']]))
    return dict(candidate=c, roots=roots, sides=sides,
                skipped_doses=[] if pair['eligible'] else c['doses'],
                decision=decision(c, roots, sides, p))
