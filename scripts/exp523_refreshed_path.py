"""Two bounded continuation steps with freshly measured a/c response at each."""
from copy import deepcopy
import math
import numpy as np
from scripts import exp521_critical_response as local
from scripts import exp522_nonlinear_refinement as normal

MAX_STEPS = 2
CONTACT = 1e-7


def recenter(source, point):
    """Advance geometry and root identities only from a qualified actual point."""
    if not point['qualified']:
        raise ValueError('cannot recenter on unqualified geometry')
    identity = local.match(source['census'], point['census'])
    if not identity['qualified'] or identity['gaps'] != point['gaps']:
        raise ValueError('physical root identities differ at recenter')
    # Canonicalize only the copied reference, never the measured census or
    # its certificates. Native phase order can rotate across a cycle origin.
    reference = deepcopy(point['census'])
    windows = [w for p in reference['profiles'] for w in p['windows']]
    for context, window in zip(identity['contexts'], windows, strict=True):
        shift = context['matches'][0]['shift']
        window['events'] = window['events'][shift:]+window['events'][:shift]
    if local.match(reference, reference)['gaps'] != point['gaps']:
        raise ValueError('canonical reference loses physical root identities')
    return dict(source, anchor=point['spec']['parameters'], vectors=point['vectors'],
        gaps=point['gaps'], rows=point['fold_point']['rows'], cycle=point['fold_point']['cycle'],
        census=reference)


def stencil(anchor, step, coordinate):
    fn = local.fold.stencil if coordinate == 'a' else local.stencil
    if coordinate not in ('a', 'c') or step not in range(MAX_STEPS):
        raise ValueError('bounded step and coordinate required')
    return [dict(s, id=f'step-{step}-{coordinate}-{i}') for i, s in enumerate(fn(anchor))]


def response(source, apoints, cpoints, step):
    anchor = source['anchor']
    for coordinate, points in [('a', apoints), ('c', cpoints)]:
        if [p['spec'] for p in points] != stencil(anchor, step, coordinate):
            raise ValueError('complete prescribed response stencil required')
    aa = [dict(p, spec=s) for p, s in zip(apoints, local.fold.stencil(anchor), strict=True)]
    cc = [dict(p, spec=s) for p, s in zip(cpoints, local.stencil(anchor), strict=True)]
    a = local.fold.response(aa, anchor)
    ag = local.gap_response(aa, 'a', local.HA)
    c = local.response(cc, anchor)
    out = dict(qualified=False, center=anchor, a=a, a_gaps=ag, c=c, curvature=None)
    if not all(r['qualified'] for r in (a, ag, c)):
        return out
    f0, g0 = local.fold.values(source['vectors']), local.gvalues(source['gaps'])
    fs, gs = [], []
    for lo, hi in [(0, 1), (2, 3)]:
        half = (cc[hi]['spec']['parameters']['c']-cc[lo]['spec']['parameters']['c'])/2
        factor = (local.HC/half)**2
        fs.append(((local.fold.values(cc[hi]['vectors'])+local.fold.values(cc[lo]['vectors']))/2-f0)*factor)
        gs.append(((local.gvalues(cc[hi]['gaps'])+local.gvalues(cc[lo]['gaps']))/2-g0)*factor)
    fe = [float(np.linalg.norm(x-y)/max(float(np.linalg.norm(y)), 1e-8)) for x, y in zip(*fs, strict=True)]
    ge = [float(abs(x-y)/max(abs(y), 1e-8)) for x, y in zip(*gs, strict=True)]
    out['curvature'] = dict(fold_coarse=fs[0].tolist(), fold_fine=fs[1].tolist(),
        gap_coarse=gs[0].tolist(), gap_fine=gs[1].tolist(), fold_errors=fe, gap_errors=ge,
        qualified=all(e <= .05 for e in fe+ge))
    out['qualified'] = out['curvature']['qualified']
    return out


def proposal(source, fresh, step):
    if not fresh['qualified']:
        return None
    if fresh['center'] != source['anchor']:
        raise ValueError('fresh derivatives must share the current complete parameter center')
    seed = local.proposal(source['anchor'], source['vectors'], source['gaps'], fresh['a'],
        fresh['a_gaps'], source['anchor']['a'], fresh['c'])
    if seed is None:
        return None
    ja = np.asarray([r['fine'] for r in fresh['a']['variants']])
    jc = np.asarray([r['fine'] for r in fresh['c']['folds']])
    ga = np.asarray([r['fine'] for r in fresh['a_gaps']['variants']])
    gc = np.asarray([r['fine'] for r in fresh['c']['gaps']['variants']])
    qf, qg = (np.asarray(fresh['curvature'][n]) for n in ('fold_fine', 'gap_fine'))
    dc = seed['normalized_c_step']
    correction = math.fsum(qf[:, 0])/math.fsum(ja[:, 0])*dc*dc
    a = seed['spec']['parameters']['a']-local.HA*correction
    da = (a-source['anchor']['a'])/local.HA
    if not math.isfinite(da) or abs(da) > 1:
        return None
    f = local.fold.values(source['vectors'])+ja*da+jc*dc+qf*dc*dc
    g = local.gvalues(source['gaps'])+ga*da+gc*dc+qg*dc*dc
    if not np.isfinite(f).all() or not np.isfinite(g).all():
        raise ValueError('finite complete quadratic predictions required')
    if not all(abs(x) < abs(y) for x, y in zip(g[::2], local.gvalues(source['gaps'])[::2], strict=True)):
        return None
    return dict(spec=dict(id=f'step-{step}-predictor', parameters=dict(seed['spec']['parameters'], a=a)),
        derivative_center=source['anchor'], linear_seed=seed, normalized_a_step=da, normalized_c_step=dc,
        predicted_vectors=[dict(key=k, residual=v.tolist()) for k, v in zip(local.fold.KEYS, f, strict=True)],
        predicted_gaps=[dict(key=k, residual=float(v)) for k, v in zip(local.GKEYS, g, strict=True)])


def tight(point):
    return bool(point['qualified'] and np.max(np.abs(local.fold.values(point['vectors']))) <= CONTACT)


def follow(source, measure):
    """No retries; preserve failed predictors and refresh all eight samples per step."""
    current = deepcopy(source); steps = []; accepted = []
    for step in range(MAX_STEPS):
        row = dict(index=step, anchor=current['anchor'])
        def take(spec, origin=current):
            point = measure(spec, origin)
            if point['spec'] != spec:
                raise ValueError('measurement differs from prescribed point')
            return point
        aa = [take(s) for s in stencil(current['anchor'], step, 'a')]
        cc = [take(s) for s in stencil(current['anchor'], step, 'c')]
        fresh = response(current, aa, cc, step); proposed = proposal(current, fresh, step)
        row.update(a_points=aa, c_points=cc, response=fresh, proposal=proposed,
            predictor=None, predictor_decision=None, refinement_source=None, refinement_proposal=None,
            refinement=None, refinement_decision=None, accepted=None, stop_reason=None)
        steps.append(row)
        if proposed is None:
            row['stop_reason'] = 'no-qualified-bounded-predictor'; break
        trial = take(proposed['spec']); verdict = local.verdict(trial, current['vectors'], current['gaps'], proposed)
        row.update(predictor=trial, predictor_decision=verdict)
        if verdict['qualified'] and tight(trial):
            endpoint = trial
        else:
            # A failed fold prediction is preserved. Only qualified actual
            # geometry, all gap predictions and net progress permit one normal
            # correction. Its complete predictions face separate fresh data.
            permitted = (trial['qualified'] and all(r['qualified'] for r in verdict['gaps'])
                and all(r['improved'] for r in verdict['gaps'][::2])
                and max(r['distance'] for r in verdict['folds']) <= 1e-4)
            if not permitted:
                row['stop_reason'] = 'predictor-geometry-gap-or-progress-failed'; break
            origin = dict(recenter(current, trial), a_response=fresh['a'], a_gaps=fresh['a_gaps'],
                a_center=current['anchor']['a'], a_derivative_center=current['anchor'],
                progress_anchor=current['anchor'], progress_gaps=current['gaps'])
            correction = normal.proposal(origin)
            # Retain only explicit reference metadata; reconstruct geometry in audit.
            row['refinement_source'] = dict(prediction_center=origin['anchor'],
                derivative_center=current['anchor'], progress_center=current['anchor'])
            if correction is None:
                row['stop_reason'] = 'no-bounded-normal-correction'; break
            correction['spec']['id'] = f'step-{step}-refinement'
            refined = take(correction['spec'], origin)
            decision = normal.verdict(refined, origin, correction)
            row.update(refinement_proposal=correction, refinement=refined, refinement_decision=decision)
            if not decision['qualified'] or not tight(refined):
                row['stop_reason'] = 'normal-correction-failed'; break
            endpoint = refined
        row['accepted'] = endpoint['spec']; accepted.append(endpoint['spec'])
        current = recenter(current, endpoint)
    return dict(steps=steps, accepted=accepted, completed_steps=len(accepted),
        qualified=len(accepted) == MAX_STEPS, symbolic_chains_verified=False,
        D_identified=False, exact_critical_locus_proved=False)
