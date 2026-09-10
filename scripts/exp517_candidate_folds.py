"""Two new event sheets, both initial directions; no relabeling of old depth 8."""
from copy import deepcopy
import math

from scripts.exp513_candidate_folds import seed, assessment, follow  # same qualification/controller


def selection(data):
    screen, old, grazing = [data[k] for k in ('screen', 'coverage', 'grazing')]
    if not grazing['passed'] or not grazing['protocol_compliant'] or len(grazing['rows']) != 5:
        raise ValueError('complete audited grazing input required')
    ledger, unclassified = [], []
    for row in screen['analysis']['rows']:
        for ordinal in row['ordinals']:
            for cell in ordinal['cells']:
                if not cell['endpoint_candidate']:
                    continue
                cuts = [r['candidate']['id'] for r in grazing['rows']
                    if r['decision']['qualified'] and r['candidate']['direction'] == row['direction']
                    and r['candidate']['indices'] == cell['nodes']
                    and r['candidate']['accepted_prefix'] <= ordinal['ordinal']]
                item = dict(direction=row['direction'], history=ordinal['ordinal'],
                            source_nodes=cell['nodes'], known_prefix_grazing_ids=cuts)
                ledger.append(item)
                if not cuts:
                    unclassified.append(item)
    if len(ledger) != 11 or [(r['direction'], r['history'], r['source_nodes']) for r in unclassified] != [(0, 4, [17, 18]), (0, 7, [18, 19])]:
        raise ValueError('complete eleven-cell/two-unclassified nomination ledger required')
    source = old['result']['rows'][0]
    candidates = []
    for item in unclassified:
        bounds = [source['samples'][i]['u'] for i in item['source_nodes']]
        for direction, row in enumerate(old['result']['rows']):
            parent = row['candidate']
            x0, tx0 = source['candidate']['initial_state'][0], source['candidate']['initial_tangent'][0]
            x1, tx1 = parent['initial_state'][0], parent['initial_tangent'][0]
            box = bounds if direction == 0 else [(x0+u*tx0-x1)/tx1 for u in bounds]
            ident = f'exp517-history-{item["history"]}-direction-{direction}'
            keys = ['case', 'region', 'initial_state', 'initial_tangent', 'parameters', 'old_x_interval']
            c = {k: deepcopy(parent[k]) for k in keys}
            c.update(id=ident, family_id=ident, parent_id=parent['id'],
                parent_family_id=parent['family_id'], direction=direction, history=item['history'],
                count=item['history']+1, source_direction=0, source_nodes=item['source_nodes'],
                source_u_box=bounds, u_box=box, seed_u=math.fsum(box)/2, seed_time=None,
                time_box=[1e-8, source['candidate']['horizon']], horizon=source['candidate']['horizon'],
                epsilon=1e-6, mapping='identity' if direction == 0 else 'match original direction-0 initial x endpoints')
            if not box[0] < c['seed_u']-c['epsilon'] < c['seed_u']+c['epsilon'] < box[1]:
                raise ValueError('interior midpoint census offsets required')
            if any(abs((x1+v*tx1)-(x0+u*tx0)) > 1e-12 for u, v in zip(bounds, box, strict=True)):
                raise ValueError('realized mapped initial x mismatch')
            candidates.append(c)
    if [(c['history'], c['direction']) for c in candidates] != [(4, 0), (4, 1), (7, 0), (7, 1)]:
        raise ValueError('both histories and initial directions required')
    return dict(nomination_ledger=ledger, candidates=candidates)


def cross_representation(rows, scales):
    if [(r['candidate']['history'], r['candidate']['direction']) for r in rows] != [(4, 0), (4, 1), (7, 0), (7, 1)]:
        raise ValueError('complete four-representation result required')
    if len(scales)!=3 or not all(math.isfinite(s) and s>0 for s in scales):
        raise ValueError('finite positive three-coordinate scales required')
    qualified = all(r['assessment'] is not None and r['assessment']['qualified'] for r in rows)
    spread = None
    if qualified:
        if any([p['method'] for p in r['folds']]!=['DOP853','Radau'] for r in rows):
            raise ValueError('complete ordered solver matrix required')
        values = [p['qualification']['observations'][1] for r in rows for p in r['folds']]
        if any(len(v[k])!=3 or not all(math.isfinite(x) for x in v[k])
               for v in values for k in ('image_state','next_state')):
            raise ValueError('complete finite full-state observations required')
        spread = max((max(v[k][j] for v in values)-min(v[k][j] for v in values))/scales[j]
                     for k in ('image_state', 'next_state') for j in range(3))
    restored = qualified and spread <= 1e-6 and all(r['assessment']['reference_restored'] for r in rows)
    return dict(all_representations_qualified=qualified, full_state_spread=spread,
        all_references_restored=bool(restored), history_returns=[4, 7],
        original_eighth_return_restored=False, symbolic_chains_verified=False)
