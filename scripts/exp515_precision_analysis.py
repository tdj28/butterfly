"""Stored-polynomial event sensitivities; not validated ODE error enclosures."""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import math

from butterfly import decimal_grazing as numeric
from butterfly import polynomial_census as poly
from butterfly.decimal_taylor import exact
from scripts import exp500_census_analysis as census

SCALES = [15, 15, '.01']


def text_fraction(v):
    return str(D(v.numerator)/D(v.denominator))


def norm(v):
    return sum((D(x)/D(s))**2 for x, s in zip(v, SCALES, strict=True)).sqrt()


def state_view(raw):
    field = raw['field']
    return dict(raw, scales=SCALES,
        steps=[dict(r, coefficients=r['coefficients'][:3]) for r in raw['steps']],
        initial=raw['initial'][:3],
        field=dict(constant=field['constant'][:3],
            linear=[r for r in field['linear'] if r[0] < 3],
            quadratic=[r for r in field['quadratic'] if r[0] < 3]))


def event_measure(raw, event):
    """Exact rational polynomial evaluation and interval projection first."""
    segment = event['segments'][0]
    row = raw['steps'][segment]
    lo, hi = [F(v)-F(row['time']) for v in event['time_box']]
    if not 0 <= lo <= hi <= F(row['step']):
        raise ValueError('event box outside its archived segment')
    coefficients = [[F(v) for v in p] for p in row['coefficients']]
    q = [poly.evaluate(p, (lo+hi)/2) for p in coefficients]
    boxes = [poly.interval_value(p, lo, hi) for p in coefficients]
    field = state_view(dict(raw, steps=[]))['field']
    fbox = census.field_interval(boxes[:3], field)
    f = [r[0] for r in census.field_interval([(v, v) for v in q[:3]], field)]
    if fbox[1][0] <= 0 <= fbox[1][1]:
        return dict(qualified=False, reason='normal velocity interval includes zero')
    inverse = (1/fbox[1][1], 1/fbox[1][0])
    tau_box = poly.interval_product(boxes[4], inverse)
    tau = q[4]/f[1]
    corrected = [q[j+3]-f[j]*tau for j in range(3)]
    bounds = []
    for j in range(3):
        removed = poly.interval_product(fbox[j], tau_box)
        bounds.append((boxes[j+3][0]-removed[1], boxes[j+3][1]-removed[0]))
    # The normal component cancels identically; interval dependency is artificial.
    corrected[1], bounds[1] = F(0), (F(0), F(0))
    with localcontext() as ctx:
        ctx.prec = 70
        values = [text_fraction(v) for v in corrected]
        radius = norm([text_fraction(max(abs(a-v), abs(b-v)))
                       for v, (a, b) in zip(corrected, bounds, strict=True)])
        gain = norm(values)
        raw_gain = norm([text_fraction(v) for v in q[3:]])
        removed_gain = norm([text_fraction(v*tau) for v in f])
        return dict(qualified=True, time=event['time'], time_box=event['time_box'],
            state=[text_fraction(v) for v in q[:3]], raw_tangent=[text_fraction(v) for v in q[3:]],
            field=[text_fraction(v) for v in f], corrected=values,
            corrected_intervals=[[text_fraction(v) for v in r] for r in bounds],
            scaled_norm=str(gain), root_box_radius=str(radius),
            box_relative_radius=str(radius/gain) if gain else None,
            subtraction_condition=str((raw_gain+removed_gain)/gain) if gain else None,
            rigorous_ode_enclosure=False)


def analyze(raw, section, *, certificate=None, before_segment=None):
    report, proof = census.profile(state_view(raw), section,
        certificate=certificate, before_segment=before_segment)
    accepted = [e for e in report['events'] if e['accepted']]
    measures = [event_measure(raw, e) for e in accepted]
    return dict(configuration=raw['config']['name'], census=report, measures=measures,
                rigorous_ode_enclosure=False), proof


def vector_compare(a, b):
    with localcontext() as ctx:
        ctx.prec = 70
        na, nb = norm(a), norm(b)
        error = norm([D(v)-D(w) for v, w in zip(a, b, strict=True)])
        denominator = min(na, nb)
        return dict(absolute=str(error), relative=str(error/denominator) if denominator else None,
            within_one_percent=bool(denominator and error <= D('.01')*denominator))


def compare(profiles, historical):
    if [p['configuration'] for p in profiles] != [c['name'] for c in numeric.CONFIGS]:
        raise ValueError('complete ordered precision pair required')
    a, b = profiles
    events = [p['census']['events'] for p in profiles]
    paired = census.compare_events(*events, SCALES)
    keys = ('direction', 'half_plane', 'time_class', 'classification_qualified', 'accepted')
    categories = len(events[0]) == len(events[1]) and all(
        all(x[k] == y[k] for k in keys) for x, y in zip(*events, strict=True))
    sequence = all(p['census']['complete'] and len(p['measures']) == 3 for p in profiles) and paired['passed'] and categories
    comparisons = []
    for ordinal in range(min(len(a['measures']), len(b['measures']), 3)):
        x, y = a['measures'][ordinal], b['measures'][ordinal]
        if not x['qualified'] or not y['qualified']:
            comparisons.append(dict(ordinal=ordinal+1, resolved=False, reason='unqualified projection'))
            continue
        delta = vector_compare(x['corrected'], y['corrected'])
        boxes = all(v['box_relative_radius'] is not None and D(v['box_relative_radius']) <= D('.001') for v in (x, y))
        comparisons.append(dict(ordinal=ordinal+1, comparison=delta, boxes_resolve=boxes,
            resolved=bool(sequence and boxes and delta['within_one_percent']),
            below_historical_gain_threshold=[D(v['scaled_norm']) < D('1e-4') for v in (x, y)]))
    old = []
    if [h['method'] for h in historical] != ['DOP853', 'Radau']:
        raise ValueError('both historical methods required')
    for profile in profiles:
        for h in historical:
            parity = census.compare_events([dict(time=m['time'], state=m['state']) for m in profile['measures'] if m['qualified']],
                                          h['events'], SCALES)
            rows = [dict(ordinal=i+1, comparison=vector_compare(m['corrected'], e['tangent']))
                    for i, (m, e) in enumerate(zip(profile['measures'][:3], h['events'])) if m['qualified']]
            old.append(dict(configuration=profile['configuration'], method=h['method'], parity=parity,
                comparisons=rows, interpretable=sequence and parity['passed'] and parity['count_a'] == 3))
    return dict(precision_sequence_qualified=sequence, event_pair=paired, classifications_agree=categories,
        ordinals=comparisons, historical=old,
        all_three_resolved=bool(sequence and len(comparisons) == 3 and all(r['resolved'] for r in comparisons)),
        historical_decisions_changed=False, symbolic_chains_verified=False)


def selection(saved):
    from butterfly.models import RosslerParameters
    from butterfly.poincare import legacy_rossler_section
    rows = []
    for direction, family in enumerate(saved['result']['rows']):
        c = family['candidate']
        section = legacy_rossler_section(RosslerParameters(**c['parameters']))
        for node in (8, 9, 10):
            sample = family['samples'][node]
            histories = sample['profiles']
            reports = [h['report'] for h in histories]
            q, v = reports[0]['initial_state'], reports[0]['initial_tangent']
            if ([h['method'] for h in histories] != ['DOP853', 'Radau']
                    or any(r['initial_state'] != q or r['initial_tangent'] != v for r in reports)
                    or len(q) != 3 or len(v) != 3 or not all(math.isfinite(x) for x in q+v)):
                raise ValueError('historical initial/method identity differs')
            a, b, cpar = [str(exact(c['parameters'][k])) for k in ('a', 'b', 'c')]
            field = numeric.augment(dict(constant=[0, 0, b],
                linear=[[0, 1, -1], [0, 2, -1], [1, 0, 1], [1, 1, a], [2, 2, '-'+cpar]],
                quadratic=[[2, 0, 2, 1]]))
            historical = [dict(method=h['method'], events=[dict(time=e['time'], state=e['state'], tangent=e['tangent'])
                for e in h['measurement']['image']['events'][:3]]) for h in histories]
            if any(len(h['events']) != 3 for h in historical):
                raise ValueError('three historical comparators required')
            rows.append(dict(id=f'direction-{direction}--node-{node}', direction=direction, node=node,
                initial=[str(exact(x)) for x in q+v], field=field, horizon='18',
                section=dict(offset=str(exact(section.offset)), gate_upper=str(exact(section.gate_upper))),
                historical=historical))
    if len(rows) != 6 or math.ceil(max(e['time'] for r in rows for h in r['historical'] for e in h['events'])+1) != 18:
        raise ValueError('complete six-input horizon selection differs')
    return rows
