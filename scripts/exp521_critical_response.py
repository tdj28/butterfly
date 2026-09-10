"""Fresh c response and one tested critical-contact predictor; no IVPs here."""
import math

import numpy as np
from scripts import exp519_fold_response as fold

HA, HC = 1e-5, .005
OBJECTS = [5, 13]
GKEYS = [[m, w, i] for m in ('DOP853', 'Radau') for w in (.25, 1.25) for i in OBJECTS]
MATCH_SCALES = np.array([15., 15., 20.])


def contexts(point):
    if [p['method'] for p in point['profiles']] != ['DOP853', 'Radau']:
        raise ValueError('complete census solver pair required')
    result = []
    for p in point['profiles']:
        if [w['phase'] for w in p['windows']] != [.25, 1.25]:
            raise ValueError('both census windows required')
        for w in p['windows']:
            for e in w['events']:
                if (np.asarray(e['state']).shape != (3,) or not np.isfinite(e['state']).all()
                        or not math.isfinite(e['cycle_phase']) or not 0 <= e['cycle_phase'] < 1
                        or not math.isfinite(e['signed_gap'])):
                    raise ValueError('finite full-state stationary event required')
            result.append((p['method'], w['phase'], w['events']))
    return result


def match(anchor, current):
    """Unique cyclic correspondence requires phase, full state and curvature."""
    rows, gaps = [], []
    qualified = all(p['qualified'] for p in anchor['profiles']+current['profiles'])
    for (method, phase, before), (m, w, after) in zip(contexts(anchor), contexts(current), strict=True):
        if (m, w) != (method, phase) or len(before) != 16:
            raise ValueError('fixed sixteen-root anchor required')
        candidates = []
        if len(after) == 16:
            for shift in range(16):
                shifted = after[shift:]+after[:shift]
                dp = max(abs((b['cycle_phase']-a['cycle_phase']+.5) % 1-.5) for a, b in zip(before, shifted, strict=True))
                dq = max(float(np.max(np.abs((np.asarray(b['state'])-a['state'])/MATCH_SCALES))) for a, b in zip(before, shifted, strict=True))
                curve = all(a['curvature_sign'] == b['curvature_sign'] != 0 for a, b in zip(before, shifted, strict=True))
                if curve and dp <= .01 and dq <= .05:
                    candidates.append(dict(shift=shift, maximum_phase_displacement=dp, maximum_state_displacement=dq))
        good = len(candidates) == 1
        rows.append(dict(method=method, phase=phase, matches=candidates, qualified=good))
        qualified = qualified and good
        if good:
            shift = candidates[0]['shift']; shifted = after[shift:]+after[:shift]
            for index in OBJECTS:
                e = shifted[index]
                gaps.append(dict(key=[method, phase, index], residual=e['signed_gap']/15., event=e))
    return dict(qualified=bool(qualified), contexts=rows, gaps=gaps if qualified else None)


def gvalues(rows):
    if [r['key'] for r in rows] != GKEYS:
        raise ValueError('both inner objects in every context required')
    value = np.asarray([r['residual'] for r in rows], dtype=float)
    if value.shape != (8,) or not np.isfinite(value).all():
        raise ValueError('finite complete gap vector required')
    return value


def stencil(anchor):
    if set(anchor) != {'a', 'b', 'c'} or not all(math.isfinite(x) for x in anchor.values()):
        raise ValueError('finite complete parameters required')
    return [dict(id=f'c-{scale}-{sign:+d}', scale=scale, sign=sign,
        parameters=dict(anchor, c=anchor['c']+sign*h))
        for scale, h in [('coarse', HC), ('fine', HC/2)] for sign in (-1, 1)]


def gap_response(points, coordinate, scale):
    if len(points) != 4 or coordinate not in ('a', 'c') or scale <= 0 or not math.isfinite(scale):
        raise ValueError('complete finite gap stencil required')
    if not all(p['qualified'] for p in points):
        return dict(qualified=False, variants=[])
    slopes = []
    for lo, hi in ((0, 1), (2, 3)):
        width = points[hi]['spec']['parameters'][coordinate]-points[lo]['spec']['parameters'][coordinate]
        if not width > 0: raise ValueError('positive realized stencil separation required')
        slopes.append((gvalues(points[hi]['gaps'])-gvalues(points[lo]['gaps']))*scale/width)
    rows = []
    for key, c, f in zip(GKEYS, *slopes, strict=True):
        error = float(abs(c-f)/max(abs(f), 1e-8))
        rows.append(dict(key=key, coarse=float(c), fine=float(f), relative_error=error, qualified=error <= .05))
    return dict(qualified=all(r['qualified'] for r in rows), variants=rows)


def response(points, anchor):
    if len(points) != 4 or [p['spec'] for p in points] != stencil(anchor):
        raise ValueError('complete fixed c stencil required')
    if not all(p['qualified'] for p in points):
        return dict(qualified=False, reason='stencil-point-unqualified', folds=[], gaps=None)
    slopes = []
    for lo, hi in ((0, 1), (2, 3)):
        width = points[hi]['spec']['parameters']['c']-points[lo]['spec']['parameters']['c']
        slopes.append((fold.values(points[hi]['vectors'])-fold.values(points[lo]['vectors']))*HC/width)
    rows = []
    for key, coarse, fine in zip(fold.KEYS, *slopes, strict=True):
        error = float(np.linalg.norm(coarse-fine)/max(float(np.linalg.norm(fine)), 1e-8))
        xerror = float(abs(coarse[0]-fine[0])/max(abs(float(fine[0])), 1e-8))
        rows.append(dict(key=key, coarse=coarse.tolist(), fine=fine.tolist(), relative_error=error,
                         x_relative_error=xerror, qualified=error <= .05 and xerror <= .05))
    gaps = gap_response(points, 'c', HC)
    good = all(r['qualified'] for r in rows) and gaps['qualified']
    return dict(qualified=good, reason=None if good else 'c-response-inconsistent', folds=rows, gaps=gaps)


def proposal(anchor, vectors, gaps, a_response, a_gaps, a_center, fresh):
    if not (a_response['qualified'] and a_gaps['qualified'] and fresh['qualified']):
        return None
    if [r['key'] for r in a_response['variants']] != fold.KEYS or [r['key'] for r in fresh['folds']] != fold.KEYS:
        raise ValueError('complete fold derivative identities required')
    if [r['key'] for r in a_gaps['variants']] != GKEYS or [r['key'] for r in fresh['gaps']['variants']] != GKEYS:
        raise ValueError('complete gap derivative identities required')
    f, g = fold.values(vectors), gvalues(gaps)
    ja = np.asarray([r['fine'] for r in a_response['variants']]); jc = np.asarray([r['fine'] for r in fresh['folds']])
    ga = np.asarray([r['fine'] for r in a_gaps['variants']]); gc = np.asarray([r['fine'] for r in fresh['gaps']['variants']])
    if (ja.shape != (16, 6) or jc.shape != (16, 6) or ga.shape != (8,) or gc.shape != (8,)
            or not math.isfinite(a_center) or not all(np.isfinite(x).all() for x in (ja, jc, ga, gc))):
        raise ValueError('finite response required')
    af, cf, f0 = (math.fsum(x)/16 for x in (ja[:, 0], jc[:, 0], f[:, 0]))
    if abs(af) <= 1e-8: raise ValueError('a response cannot restore scalar fold contact')
    intercept, tangent = -f0/af, -cf/af
    lower = max(-1., (a_center-HA-anchor['a'])/HA)
    upper = min(1., (a_center+HA-anchor['a'])/HA)
    c_lower, c_upper = -1., 1.
    if tangent == 0:
        if not lower <= intercept <= upper: return None
    else:
        limits = sorted(((lower-intercept)/tangent, (upper-intercept)/tangent))
        c_lower, c_upper = max(c_lower, limits[0]), min(c_upper, limits[1])
    if c_lower > c_upper: return None
    # The first identified inner maximum is the fixed progress target; the
    # second remains in the prediction and identity gates, even if it worsens.
    g0, ag, cg = (math.fsum(x[::2])/4 for x in (g, ga, gc))
    slope = cg+ag*tangent
    if abs(slope) <= 1e-8: return None
    requested_c = max(c_lower, min(c_upper, -(g0+ag*intercept)/slope))
    a = anchor['a']+HA*(intercept+tangent*requested_c)
    c = anchor['c']+HC*requested_c
    da, dc = (a-anchor['a'])/HA, (c-anchor['c'])/HC
    if not lower-1e-10 <= da <= upper+1e-10 or abs(dc) > 1+1e-10:
        raise ValueError('realized predictor leaves bounded response domain')
    predicted_f, predicted_g = f+ja*da+jc*dc, g+ga*da+gc*dc
    if abs(dc) <= 1e-6 or not all(abs(y) < abs(x) for x, y in zip(g[::2], predicted_g[::2], strict=True)):
        return None
    return dict(spec=dict(id='critical-step', parameters=dict(anchor, a=a, c=c)),
        a_response_center=a_center, c_response_center=anchor,
        derivative_centers_identical=a_center == anchor['a'],
        normalized_a_step=da, normalized_c_step=dc, c_interval=[c_lower, c_upper],
        critical_a_intercept=intercept, critical_a_tangent=tangent,
        target_gap_tangent=slope,
        predicted_vectors=[dict(key=k, residual=v.tolist()) for k, v in zip(fold.KEYS, predicted_f, strict=True)],
        predicted_gaps=[dict(key=k, residual=float(v)) for k, v in zip(GKEYS, predicted_g, strict=True)])


def verdict(point, vectors, gaps, proposed):
    if not point['qualified']:
        return dict(qualified=False, reason='critical-point-unqualified', folds=[], gaps=[])
    actual, initial, predicted = [fold.values(v) for v in (point['vectors'], vectors, proposed['predicted_vectors'])]
    frows = []
    for key, q, old, pred in zip(fold.KEYS, actual, initial, predicted, strict=True):
        distance = float(np.max(np.abs(q)))
        error = float(np.linalg.norm(q-pred)/max(float(np.linalg.norm(pred-old)), 1e-12))
        frows.append(dict(key=key, distance=distance, prediction_error=error, qualified=distance <= 1e-4 and error <= .1))
    grows = []
    for key, q, old, pred in zip(GKEYS, gvalues(point['gaps']), gvalues(gaps), gvalues(proposed['predicted_gaps']), strict=True):
        error = float(abs(q-pred)/max(abs(pred-old), 1e-8))
        grows.append(dict(key=key, before=float(old), actual=float(q), predicted=float(pred),
                         prediction_error=error, qualified=error <= .1, improved=bool(abs(q) < abs(old))))
    good = all(r['qualified'] for r in frows+grows) and all(r['improved'] for r in grows[::2])
    return dict(qualified=good, reason=None if good else 'contact-prediction-or-progress-failed', folds=frows, gaps=grows)


def follow(source, measure):
    points = [measure(s) for s in stencil(source['anchor'])]
    fresh = response(points, source['anchor'])
    proposed = proposal(source['anchor'], source['vectors'], source['gaps'], source['a_response'],
                        source['a_gaps'], source['a_center'], fresh)
    corrected = None if proposed is None else measure(proposed['spec'])
    if corrected is not None and corrected['spec'] != proposed['spec']:
        raise ValueError('measured point differs from prescribed critical step')
    decision = None if corrected is None else verdict(corrected, source['vectors'], source['gaps'], proposed)
    return dict(points=points, response=fresh, proposal=proposed, correction=corrected, decision=decision,
                correction_not_run_reason=(None if proposed is not None else
                    ('unqualified-response' if not fresh['qualified'] or not source['a_gaps']['qualified'] else 'no-bounded-improving-predictor')),
                symbolic_chains_verified=False, D_identified=False, exact_critical_locus_proved=False)
