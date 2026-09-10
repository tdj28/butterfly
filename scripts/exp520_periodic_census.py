"""Exact roots on saved binary64 dense polynomials, not exact-flow enclosures.

Only the successor uses this module. Historical observers remain immutable.
All polynomial arithmetic before reporting uses exact rational coefficients.
"""
from fractions import Fraction as F
from math import comb

import numpy as np
from butterfly import polynomial_census as roots

SCALES = (15., 15., .01)
TIME_WIDTH = F('1e-15')
STATE_TOL = 1e-6
PHASE_TOL = 1e-7
JOIN_TOL = F('1e-10')
GAP_SEPARATION = 1e-7


def exact(x):
    return F.from_float(float(x))


def powers(old, coefficients, method, *, auditor=False):
    """Producer recurrence versus independently expanded dense-output basis."""
    old, coefficients = np.asarray(old), np.asarray(coefficients)
    shape = (7, 3) if method == 'DOP853' else (3, 3)
    if method not in ('DOP853', 'Radau') or old.shape != (3,) or coefficients.shape != shape:
        raise ValueError('complete supported dense coefficient matrix required')
    if not np.isfinite(old).all() or not np.isfinite(coefficients).all():
        raise ValueError('finite dense coefficients required')
    answer = []
    for axis in range(3):
        if method == 'Radau':
            p = [exact(old[axis])]+[exact(v) for v in coefficients[axis]]
        elif auditor:
            # F_j multiplies x**(j//2+1)*(1-x)**((j+1)//2).
            p = [exact(old[axis])]+[F(0)]*7
            for j in range(7):
                degree, back = j//2+1, (j+1)//2
                for k in range(back+1):
                    p[degree+k] += exact(coefficients[j, axis])*comb(back, k)*(-1)**k
        else:
            p = [F(0)]
            for j, f in enumerate(coefficients[::-1, axis]):
                p[0] += exact(f)
                if j % 2 == 0:
                    p = [F(0)]+p
                else:
                    p = [p[0]]+[p[k]-p[k-1] for k in range(1, len(p))]+[-p[-1]]
            p[0] += exact(old[axis])
        answer.append(p)
    return answer


def stationarity(poly, a):
    return roots.integers([x+exact(a)*y for x, y in zip(poly[0], poly[1], strict=True)])


def classify(poly, time, width, box, parameters, origin):
    lo, hi = map(F, box)
    bounds = [roots.interval_value(p, lo, hi) for p in poly]
    mid = (lo+hi)/2
    q = [roots.evaluate(p, mid) for p in poly]
    a, b, c = (exact(parameters[k]) for k in ('a', 'b', 'c'))
    velocity = [-q[1]-q[2], q[0]+a*q[1], b+q[2]*(q[0]-c)]
    acceleration = velocity[0]+a*velocity[1]
    stored_dy = roots.evaluate([i*v for i, v in enumerate(poly[1])][1:], mid)/width
    gap = q[1]-exact(origin[1])
    derivative_bounds = roots.interval_value([i*v for i, v in enumerate(poly[1])][1:], lo, hi)
    acceleration_bounds = (-bounds[1][1]-bounds[2][1]+a*(bounds[0][0]+a*bounds[1][0]),
                           -bounds[1][0]-bounds[2][0]+a*(bounds[0][1]+a*bounds[1][1]))
    curvature_sign = 1 if acceleration_bounds[0] > 0 else (-1 if acceleration_bounds[1] < 0 else 0)
    return dict(time=float(time+width*mid), time_box=[str(time+width*v) for v in (lo, hi)],
        state=[float(v) for v in q], state_box=[[str(v) for v in interval] for interval in bounds],
        signed_gap=float(gap), normalized_gap=float(gap/15),
        gap_box=[str(bounds[1][i]-exact(origin[1])) for i in (0, 1)],
        z_separation=float(q[2]-exact(origin[2])), speed=float(np.linalg.norm(list(map(float, velocity)))),
        acceleration=float(acceleration), curvature_sign=curvature_sign,
        field_stationarity_residual=float(velocity[1]), stored_y_derivative=float(stored_dy),
        stored_y_derivative_box=[str(v/width) for v in derivative_bounds],
        numerical_field_consistency=abs(float(stored_dy-velocity[1]))/15 <= 1e-7,
        state_interval_scaled_width=max(float(hi-lo)/s for (lo, hi), s in zip(bounds, SCALES, strict=True)))


def profile(raw, method, parameters, origin, period, *, certificate=None, tick=lambda: None):
    times, states = raw['times'], raw['states']
    old, coefficients = raw['dense_old'], raw['dense_coefficients']
    count = len(times)-1
    if (count < 1 or times.shape != (count+1,) or states.shape != (count+1, 3)
            or old.shape != (count, 3) or len(coefficients) != count
            or not all(np.isfinite(v).all() for v in (times, states, old, coefficients))
            or times[0] != 0 or np.any(np.diff(times) <= 0)
            or period <= 0 or abs(times[-1]-2.5*period) > 1e-10):
        raise ValueError('complete finite ordered retained trajectory required')
    if certificate is not None and len(certificate) != count:
        raise ValueError('one certificate per segment required')
    events, proofs, unresolved, joins = [], [], [], []
    previous, previous_stationarity = None, None
    largest_jump = F(0)
    for index in range(count):
        tick()
        poly = powers(old[index], coefficients[index], method, auditor=certificate is not None)
        time, width = exact(times[index]), exact(times[index+1])-exact(times[index])
        power = stationarity(poly, parameters['a'])
        at_left = [p[0] for p in poly]
        at_right = [sum(p) for p in poly]
        endpoint_error = max(abs(q-exact(v))/exact(s) for q, v, s in zip(at_right, states[index+1], SCALES, strict=True))
        initial_error = max(abs(q-exact(v))/exact(s) for q, v, s in zip(at_left, states[index], SCALES, strict=True))
        if max(endpoint_error, initial_error) > JOIN_TOL:
            joins.append(dict(segment=index, kind='mesh-polynomial-disagreement', scaled_error=float(max(endpoint_error, initial_error))))
        if previous is not None:
            jump = max(abs(x-y)/exact(s) for x, y, s in zip(previous, at_left, SCALES, strict=True))
            largest_jump = max(largest_jump, jump)
            left, right = previous_stationarity, at_left[0]+exact(parameters['a'])*at_left[1]
            compatible = left*right > 0 or left == right == 0
            if jump > JOIN_TOL or not compatible:
                joins.append(dict(segment=index, kind='join', scaled_jump=float(jump), stationarity_sign_compatible=compatible))
        previous = at_right
        previous_stationarity = at_right[0]+exact(parameters['a'])*at_right[1]
        proof = roots.isolate(power, width, time_width=TIME_WIDTH) if certificate is None else certificate[index]
        if certificate is None:
            boxes = [r['root'] for r in proof['leaves'] if r['kind'] == 'single']+[[v, v] for v in proof['points']]
            missing = [list(map(str, roots.path_interval(r['path']))) for r in proof['leaves'] if r['kind'] == 'unresolved']
        else:
            checked = roots.verify(power, width, proof, time_width=TIME_WIDTH)
            boxes, missing = checked['roots'], checked['unresolved']
        proofs.append(proof)
        unresolved.extend(dict(segment=index, interval=[str(time+width*F(v)) for v in box]) for box in missing)
        for box in sorted(boxes, key=lambda row: F(row[0])):
            event = classify(poly, time, width, box, parameters, origin)
            event['segments'] = [index]
            # Shared endpoints have both witnesses, with explicit single ownership.
            if (events and event['time_box'][0] == event['time_box'][1]
                    == events[-1]['time_box'][0] == events[-1]['time_box'][1]):
                previous_event = events[-1]
                difference = max(abs(a-b)/s for a, b, s in zip(event['state'], previous_event['state'], SCALES, strict=True))
                if difference > float(JOIN_TOL) or event['curvature_sign'] != previous_event['curvature_sign']:
                    joins.append(dict(segment=index, kind='shared-root-disagreement'))
                previous_event['segments'].append(index)
                previous_event.setdefault('join_witnesses', []).append(event)
            else:
                events.append(event)
    complete = not unresolved and not joins
    callback_times, callback_states = raw['historical_extrema_times'], raw['historical_extrema_states']
    callbacks = compare_rows(events, [dict(time=float(t), state=q.tolist()) for t, q in zip(callback_times, callback_states, strict=True)], period)
    windows = []
    for phase in (.25, 1.25):
        start, end = phase*period, (phase+1)*period
        selected = [dict(e, cycle_phase=(e['time']-start)/period) for e in events if start <= e['time'] < end]
        boundary_clear = all(min(abs(e['time']-start), abs(e['time']-end))/period > PHASE_TOL for e in events)
        regular = all(e['curvature_sign'] != 0 and e['numerical_field_consistency'] and e['state_interval_scaled_width'] <= 1e-9 for e in selected)
        windows.append(dict(phase=phase, events=selected, count=len(selected), boundary_clear=boundary_clear,
                            qualified=complete and boundary_clear and regular and bool(selected)))
    repeat = compare_rows(windows[0]['events'], windows[1]['events'], period, shift=period)
    return dict(method=method, segments=count, events=events, windows=windows, repeat=repeat,
        callback_comparison=callbacks, unresolved=unresolved, join_failures=joins,
        maximum_scaled_join_jump=float(largest_jump), polynomial_census_complete=complete,
        qualified=complete and repeat['passed'] and callbacks['passed'] and all(w['qualified'] for w in windows),
        exact_flow_completeness=False), proofs


def compare_rows(a, b, period, shift=0):
    rows = []
    if len(a) == len(b):
        for index, (x, y) in enumerate(zip(a, b, strict=True)):
            phase_error = abs(x['time']-(y['time']-shift))/period
            state_error = max(abs(v-w)/s for v, w, s in zip(x['state'], y['state'], SCALES, strict=True))
            rows.append(dict(index=index, phase_error=phase_error, scaled_state_error=state_error,
                             passed=phase_error <= PHASE_TOL and state_error <= STATE_TOL))
    return dict(count_a=len(a), count_b=len(b), comparisons=rows,
                passed=len(a) == len(b) and all(r['passed'] for r in rows))


def point_comparison(profiles, periods):
    if [p['method'] for p in profiles] != ['DOP853', 'Radau']:
        raise ValueError('ordered complete solver pair required')
    pairs = []
    for window in range(2):
        a, b = (p['windows'][window]['events'] for p in profiles)
        # Compare phase-aligned states, not arbitrary absolute solver clocks.
        aa = [dict(e, time=e['cycle_phase']) for e in a]
        bb = [dict(e, time=e['cycle_phase']) for e in b]
        pairs.append(compare_rows(aa, bb, 1.))
    contexts = [w['events'] for p in profiles for w in p['windows']]
    qualified = all(p['qualified'] for p in profiles) and all(p['passed'] for p in pairs)
    nominees = []
    for events in contexts:
        order = sorted(range(len(events)), key=lambda i: abs(events[i]['normalized_gap']))
        separation = (abs(events[order[1]]['normalized_gap'])-abs(events[order[0]]['normalized_gap'])) if len(order) > 1 else None
        nominees.append(dict(index=order[0] if order else None, separation=separation,
                             unambiguous=len(order) > 1 and separation > GAP_SEPARATION))
    same = qualified and all(n['unambiguous'] for n in nominees) and len({n['index'] for n in nominees}) == 1
    nominee = nominees[0]['index'] if same else None
    return dict(paired_windows=pairs, qualified=qualified, nominations=nominees,
        consistent_nearest=same, nearest_index=nominee,
        nearest=[events[nominee] for events in contexts] if same else [],
        periods=periods, symbolic_chains_verified=False, D_identified=False)
