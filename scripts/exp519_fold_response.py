"""Fixed-c fresh response and one correction; no integrations or word labels."""
import math
import numpy as np
from scripts import exp518_fold_transport as folds

H = 1e-5
PHASES = [.25, 1.25]
KEYS = [[h, d, method, phase] for h, d in folds.CASES
        for method in folds.METHODS for phase in PHASES]


def stencil(anchor):
    if set(anchor) != {'a', 'b', 'c'} or not all(math.isfinite(v) for v in anchor.values()):
        raise ValueError('finite complete anchor required')
    return [dict(id=f'{scale}-{sign:+d}', scale=scale, sign=sign,
                 parameters=dict(anchor, a=anchor['a']+sign*h))
            for scale, h in [('coarse', H), ('fine', H/2)] for sign in [-1, 1]]


def candidates(anchor_rows, spec, offset):
    rows = folds.candidates(anchor_rows, spec, offset)
    for c in rows:
        c['id'] = f'exp519-{spec["id"]}-history-{c["history"]}-direction-{c["direction"]}'
        c['family_id'] = f'exp519-history-{c["history"]}-direction-{c["direction"]}'
    return rows


def vectors(contact):
    if len(contact['rows']) != 4:
        raise ValueError('all four contact constructions required')
    result = []
    for row, (h, d) in zip(contact['rows'], folds.CASES, strict=True):
        if row['family_id'] != f'exp519-history-{h}-direction-{d}':
            raise ValueError('new family identity required')
        if [(v['method'], v['phase']) for v in row['variants']] != [(m, p) for m in folds.METHODS for p in PHASES]:
            raise ValueError('complete paired contact variants required')
        for v in row['variants']:
            states = np.asarray(v['cycle_events'], dtype=float)
            q = np.asarray([v['fold_input'], v['fold_output']], dtype=float)
            if states.shape != (6, 3) or q.shape != (2, 3) or not np.isfinite(states).all() or not np.isfinite(q).all():
                raise ValueError('finite full six-return contact state required')
            values = ((states[[3, 4]]-q)/folds.SCALES).ravel().tolist()
            if not math.isclose(values[0], v['signed_residual'], rel_tol=1e-12, abs_tol=1e-15):
                raise ValueError('signed x and full-state residual disagree')
            result.append(dict(key=[h, d, v['method'], v['phase']], residual=values))
    return result


def values(rows):
    if [r['key'] for r in rows] != KEYS:
        raise ValueError('complete ordered sixteen-variant identity required')
    v = np.asarray([r['residual'] for r in rows], dtype=float)
    if v.shape != (16, 6) or not np.isfinite(v).all():
        raise ValueError('finite full-state residual matrix required')
    return v


def response(points, anchor):
    specs = stencil(anchor)
    if len(points) != 4 or [p['spec'] for p in points] != specs:
        raise ValueError('complete fixed stencil required')
    if not all(p['qualified'] for p in points):
        return dict(qualified=False, reason='stencil-point-unqualified', variants=[])
    slopes = []
    for lo, hi in [(0, 1), (2, 3)]:
        width = specs[hi]['parameters']['a']-specs[lo]['parameters']['a']
        if not width > 0:
            raise ValueError('resolved realized parameter separation required')
        slopes.append((values(points[hi]['vectors'])-values(points[lo]['vectors']))*H/width)
    rows = []
    for key, coarse, fine in zip(KEYS, *slopes, strict=True):
        sx = float(fine[0]); norm = float(np.linalg.norm(fine))
        x_error = float(abs(coarse[0]-sx)/max(abs(sx), 1e-30))
        full_error = float(np.linalg.norm(coarse-fine)/max(norm, 1e-30))
        good = abs(sx) > 1e-8 and x_error <= .05 and full_error <= .05
        rows.append(dict(key=key, coarse=coarse.tolist(), fine=fine.tolist(),
                         x_relative_error=x_error, full_relative_error=full_error, qualified=bool(good)))
    oriented = all(r['fine'][0] > 0 for r in rows) or all(r['fine'][0] < 0 for r in rows)
    good = oriented and all(r['qualified'] for r in rows)
    return dict(qualified=bool(good), reason=None if good else 'unresolved-or-inconsistent-fresh-response',
                consistent_orientation=oriented, variants=rows)


def proposal(anchor, anchor_vectors, fresh):
    if not fresh['qualified']:
        return None
    if [r['key'] for r in fresh['variants']] != KEYS:
        raise ValueError('fresh slope identities differ')
    f = values(anchor_vectors)
    j = np.asarray([r['fine'] for r in fresh['variants']], dtype=float)
    if j.shape != (16, 6) or not np.isfinite(j).all():
        raise ValueError('finite fresh response required')
    mean_f = math.fsum(f[:, 0])/16
    mean_j = math.fsum(j[:, 0])/16
    if abs(mean_j) <= 1e-8:
        raise ValueError('unresolved fresh scalar response')
    requested = max(-1., min(1., -mean_f/mean_j))
    a = anchor['a']+H*requested
    realized = (a-anchor['a'])/H
    if not math.isfinite(realized) or abs(realized) > 1.+1e-10:
        raise ValueError('bounded realized correction required')
    if realized == 0:
        return None
    return dict(spec=dict(id='correction', parameters=dict(anchor, a=a)),
                mean_signed_x=mean_f, mean_normalized_slope=mean_j,
                requested_normalized_step=requested, realized_normalized_step=realized,
                predicted_vectors=[dict(key=k, residual=v.tolist())
                                   for k, v in zip(KEYS, f+j*realized, strict=True)])


def verdict(point, anchor_vectors, proposed):
    if not point['qualified']:
        return dict(qualified_contact=False, full_state_contact=False, prediction_qualified=False,
                    reason='correction-point-unqualified', variants=[])
    actual, before, predicted = [values(v) for v in (point['vectors'], anchor_vectors, proposed['predicted_vectors'])]
    rows = []
    for key, a, b, pred in zip(KEYS, actual, before, predicted, strict=True):
        distance = float(np.max(np.abs(a)))
        prediction_error = float(np.linalg.norm(a-pred)/max(float(np.linalg.norm(pred-b)), 1e-12))
        rows.append(dict(key=key, full_state_distance=distance, signed_x=float(a[0]),
                         prediction_error=prediction_error, contact=distance <= 1e-4,
                         prediction_qualified=prediction_error <= .1))
    contact = all(r['contact'] for r in rows)
    prediction = all(r['prediction_qualified'] for r in rows)
    good = contact and prediction
    return dict(qualified_contact=good, full_state_contact=contact, prediction_qualified=prediction,
                reason=None if good else 'full-state-contact-or-prediction-failed', variants=rows)


def follow(anchor, anchor_vectors, measure):
    points = [measure(spec) for spec in stencil(anchor)]
    fresh = response(points, anchor)
    proposed = proposal(anchor, anchor_vectors, fresh)
    point = None if proposed is None else measure(proposed['spec'])
    if point is not None and point['spec'] != proposed['spec']:
        raise ValueError('measured correction is not the prescribed point')
    decision = None if point is None else verdict(point, anchor_vectors, proposed)
    return dict(points=points, response=fresh, proposal=proposed, correction=point, decision=decision,
                correction_not_run_reason=None if point is not None else (
                    'response-unqualified' if not fresh['qualified'] else 'scalar-floor-full-state-mismatch'),
                exact_contact_verified=False, symbolic_chains_verified=False)
