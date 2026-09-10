"""One prospective fixed-c Newton-style parameter correction, no IVPs here."""
import math
import numpy as np
from scripts import exp521_critical_response as prior


def proposal(source):
    if not source['a_response']['qualified'] or not source['a_gaps']['qualified']:
        return None
    f = prior.fold.values(source['vectors']); g = prior.gvalues(source['gaps'])
    arows, grows = source['a_response']['variants'], source['a_gaps']['variants']
    if [r['key'] for r in arows] != prior.fold.KEYS or [r['key'] for r in grows] != prior.GKEYS:
        raise ValueError('complete derivative identities required')
    j = np.asarray([r['fine'] for r in arows]); gj = np.asarray([r['fine'] for r in grows])
    if j.shape != (16, 6) or gj.shape != (8,) or not np.isfinite(j).all() or not np.isfinite(gj).all():
        raise ValueError('finite complete derivatives required')
    mean_f = math.fsum(f[:, 0])/16; mean_j = math.fsum(j[:, 0])/16
    if abs(mean_j) <= 1e-8: return None
    anchor = source['anchor']; center = source['a_center']
    low = max(anchor['a']-prior.HA, center-prior.HA)
    high = min(anchor['a']+prior.HA, center+prior.HA)
    if low > high: return None
    a = max(low, min(high, anchor['a']-prior.HA*mean_f/mean_j))
    da = (a-anchor['a'])/prior.HA
    if not math.isfinite(da) or abs(da) > 1+1e-10: raise ValueError('bounded realized step required')
    if da == 0: return None
    return dict(spec=dict(id='nonlinear-refinement', parameters=dict(anchor, a=a)),
        mean_signed_x=mean_f, mean_normalized_slope=mean_j, normalized_a_step=da,
        response_center=source['a_derivative_center'], prediction_center=anchor,
        progress_reference=source['progress_anchor'],
        predicted_vectors=[dict(key=k, residual=v.tolist()) for k, v in zip(prior.fold.KEYS, f+j*da, strict=True)],
        predicted_gaps=[dict(key=k, residual=float(v)) for k, v in zip(prior.GKEYS, g+gj*da, strict=True)])


def verdict(point, source, proposed):
    # Retain the unchanged full-state and prediction checks. The progress
    # reference below is the original c-step anchor, not its imperfect trial.
    local = prior.verdict(point, source['vectors'], source['gaps'], proposed)
    if not point['qualified']:
        return dict(qualified=False, reason='refinement-point-unqualified', local=local,
            reduction=[], net_progress=[])
    before, after = [prior.fold.values(v) for v in (source['vectors'], point['vectors'])]
    reduction = []
    for key, b, a in zip(prior.fold.KEYS, before, after, strict=True):
        old = float(np.max(np.abs(b))); new = float(np.max(np.abs(a)))
        reduction.append(dict(key=key, before=old, actual=new, qualified=new <= .1*old))
    progress = []
    for key, old, new in zip(prior.GKEYS, prior.gvalues(source['progress_gaps']), prior.gvalues(point['gaps']), strict=True):
        progress.append(dict(key=key, before=float(old), actual=float(new), improved=bool(abs(new) < abs(old))))
    good = (all(r['qualified'] for r in local['folds']+local['gaps']+reduction)
        and all(r['improved'] for r in progress[::2]))
    return dict(qualified=bool(good), reason=None if good else 'prediction-refinement-or-net-progress-failed',
        local=local, reduction=reduction, net_progress=progress)


def follow(source, measure):
    proposed = proposal(source)
    point = None if proposed is None else measure(proposed['spec'])
    if point is not None and point['spec'] != proposed['spec']:
        raise ValueError('measured point differs from prescribed refinement')
    decision = None if point is None else verdict(point, source, proposed)
    return dict(proposal=proposed, correction=point, decision=decision,
        not_run_reason='no-qualified-bounded-parameter-correction' if proposed is None else None,
        parent_predictor_qualified=False, symbolic_chains_verified=False,
        D_identified=False, exact_critical_locus_proved=False)
