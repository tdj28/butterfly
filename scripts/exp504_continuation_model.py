"""Prospective bounded secant continuation; no ODE solves or target-word input."""
from copy import deepcopy
from decimal import Decimal as D, localcontext
import math

import numpy as np
from scripts import exp502_response as response


def values(vectors, keys):
    if len(keys) != 256 or len({tuple(k) for k in keys}) != 256 or [r['key'] for r in vectors] != keys:
        raise ValueError('complete ordered 256-variant matrix required')
    result = np.asarray([r['value'] for r in vectors], dtype=float)
    if result.shape != (256, 2) or not np.isfinite(result).all():
        raise ValueError('finite residual matrix required')
    return result


def displacement(before, after):
    return np.array([(after[k]-before[k])/h for k,h in zip(response.AXES,response.INCREMENTS,strict=True)])


def model_check(models, signs):
    models = np.asarray(models, dtype=float)
    if models.shape != (256,2,2) or len(signs) != 256 or not np.isfinite(models).all():
        return dict(passed=False, reason='missing or nonfinite model', rows=[])
    rows = []
    for matrix, sign in zip(list(models)+[np.mean(models,axis=0)],list(signs)+[signs[0]],strict=True):
        determinant = float(np.linalg.det(matrix))
        condition = float(np.linalg.cond(matrix))
        rows.append(dict(determinant=determinant,condition=condition if math.isfinite(condition) else None,
            passed=bool(sign in (-1,1) and np.sign(determinant) == sign and condition <= 1e4)))
    passed = len(set(signs)) == 1 and all(r['passed'] for r in rows)
    return dict(passed=passed,reason=None if passed else 'conditioning or orientation',rows=rows)


def update(models, step, change):
    models,step,change = map(np.asarray,(models,step,change))
    norm2 = float(step@step)
    if norm2 <= 0 or not np.isfinite(norm2):
        raise ValueError('nonzero finite realized displacement required')
    updated = models+((change-models@step)[...,None]*step)/norm2
    # Separately coded scalar arithmetic, avoiding NumPy matrix products/outer.
    scalar = []
    denominator = math.fsum(float(x)*float(x) for x in step)
    for matrix, delta in zip(models,change,strict=True):
        scalar.append([[float(matrix[i,j])+(float(delta[i])-math.fsum(float(matrix[i,k])*float(step[k])
            for k in range(2)))*float(step[j])/denominator for j in range(2)] for i in range(2)])
    if (not np.allclose(updated,scalar,rtol=1e-12,atol=1e-13)
            or not np.allclose(updated@step,change,rtol=1e-12,atol=1e-13)):
        raise ValueError('scalar Broyden update or secant identity differs')
    return updated


def initialize(numerical, receipt):
    keys = [v['key'] for v in numerical['base_vectors']]
    if [r['key'] for r in receipt['response']['matrices']] != keys:
        raise ValueError('initial response representation order')
    fine = np.array([r['matrices'][1] for r in receipt['response']['matrices']])
    signs = [int(np.sign(np.linalg.det(m))) for m in fine]
    if not model_check(fine,signs)['passed']:
        raise ValueError('initial measured models unqualified')
    start = receipt['proposal']
    step = displacement(numerical['anchor'],start['spec']['parameters'])
    change = values(start['vectors'],keys)-values(numerical['base_vectors'],keys)
    models = update(fine,step,change)
    return dict(keys=keys,signs=signs,fine=fine.tolist(),models=models.tolist(),
        initialization_step=step.tolist(),initialization_change=change.tolist(),
        check=model_check(models,signs))


def propose(models, signs, current, keys, origin, number):
    check = model_check(models,signs)
    if not check['passed']:
        return dict(qualified=False,reason='model unqualified',check=check,spec=None)
    matrices = np.asarray(models)
    residuals = values(current['vectors'],keys)
    mean = np.mean(matrices,axis=0)
    f = np.mean(residuals,axis=0)
    delta = np.linalg.solve(mean,-f)
    a,b,c,d = [math.fsum(float(m[i,j]) for m in matrices)/256 for i,j in ((0,0),(0,1),(1,0),(1,1))]
    x,y = [math.fsum(float(r[i]) for r in residuals)/256 for i in (0,1)]
    scalar = [(b*y-d*x)/(a*d-b*c),(c*x-a*y)/(a*d-b*c)]
    if not np.allclose(delta,scalar,rtol=1e-12,atol=1e-13):
        raise ValueError('scalar mean solve differs')
    if not np.isfinite(delta).all() or max(abs(delta)) == 0:
        return dict(qualified=False,reason='zero or nonfinite step',check=check,spec=None)
    factor = min(1.,10./max(abs(delta)))
    before = current['spec']['parameters']
    parameters = dict(before)
    for k,h,s in zip(response.AXES,response.INCREMENTS,delta*factor,strict=True):
        parameters[k] += h*float(s)
    good = (parameters['b'] == origin['b'] == .2 and parameters['c'] < before['c']
        and abs(parameters['a']-origin['a']) <= .002 and origin['c']-.2 <= parameters['c'] <= origin['c'])
    return dict(qualified=bool(good),reason=None if good else 'parameter domain or lower-c direction',check=check,
        spec=dict(id=f'step-{number:02d}',parameters=parameters),unclipped_step=delta.tolist(),
        clipping_factor=float(factor),realized_step=displacement(before,parameters).tolist())


def warm_plan(numerical, current):
    p = deepcopy(numerical)
    if not current['qualified'] or len(current['folds']) != 4 or len(current['boundaries']) != 8:
        raise ValueError('complete qualified warm predecessor required')
    p['cycle_seed'] = deepcopy(current['cycle']['profiles'][0]['correction'])
    p['reference_cycle'] = deepcopy(current['cycle'])
    for c,row in zip(p['fold_candidates'],current['folds'],strict=True):
        if c['id'] != row['id'] or len(row['solvers']) != 2:
            raise ValueError('warm fold identity')
        u,t = [float(np.mean([r['root'][k] for r in row['solvers']])) for k in ('u','time')]
        c.update(seed_u=u,seed_time=t,u_box=[u-.02,u+.02],time_box=[t-1,t+1],horizon=t+3)
    with localcontext() as context:
        context.prec = 70
        for c,row in zip(p['boundary_candidates'],current['boundaries'],strict=True):
            if c['id'] != row['id'] or len(row['profiles']) != 2:
                raise ValueError('warm boundary identity')
            u,t = [sum(D(r['shooting']['trace'][-1][k]) for r in row['profiles'])/2 for k in ('u','time')]
            c.update(seed_u=str(u),seed_time=str(t),u_box=[str(u-D('.02')),str(u+D('.02'))],
                time_box=[str(t-1),str(t+1)])
    return p


def decide(numerical, state, models, before, after, proposal):
    original = response.correspondence(after['cycle'],numerical['reference_cycle'])
    qualification = bool(after['qualified'] and original['passed'] and after['correspondence']['passed'])
    fold = bool(after['contact'] is not None and after['contact']['envelope']['pair_state_distance'][3] <= 1e-4)
    result = dict(accepted=False,original_correspondence=original,point_qualification=qualification,
        fold_proximity=fold,variant_predictions=[],updated_models=None,model_check=None)
    if not qualification:
        return dict(result,reason='point or correspondence qualification failed')
    old,new = [values(r['vectors'],state['keys']) for r in (before,after)]
    step = displacement(before['spec']['parameters'],after['spec']['parameters'])
    if after['spec'] != proposal['spec'] or not np.array_equal(step,proposal['realized_step']):
        raise ValueError('realized proposal identity differs')
    change = new-old
    prediction = np.asarray(models)@step
    errors = np.linalg.norm(change-prediction,axis=1)/np.maximum(np.linalg.norm(prediction,axis=1),1e-12)
    previous_norm,current_norm = [float(max(abs(np.mean(v,axis=0)))) for v in (old,new)]
    baseline = values(numerical['base_vectors'],state['keys'])+np.asarray(state['fine'])@displacement(
        numerical['anchor'],after['spec']['parameters'])
    result.update(previous_norm=previous_norm,current_norm=current_norm,mean=np.mean(new,axis=0).tolist(),
        frozen_linear_baseline_mean=np.mean(baseline,axis=0).tolist(),maximum_prediction_error=float(max(errors)),
        variant_predictions=[dict(key=key,predicted=p.tolist(),observed=o.tolist(),relative_error=float(e))
            for key,p,o,e in zip(state['keys'],prediction,change,errors,strict=True)])
    reasons = []
    if not fold:
        reasons.append('fold proximity failed')
    if not current_norm < previous_norm:
        reasons.append('residual norm did not decrease')
    if not np.all(errors <= .1):
        reasons.append('directional model prediction failed')
    if not reasons:
        updated = update(models,step,change)
        check = model_check(updated,state['signs'])
        result.update(updated_models=updated.tolist(),model_check=check)
        if not check['passed']:
            reasons.append('updated model unqualified')
    return dict(result,accepted=not reasons,reason='; '.join(reasons) if reasons else None)


def verdict(start, steps, reason):
    terminal = steps[-1] if steps else None
    accepted = terminal is not None and all(r['decision']['accepted'] for r in steps)
    norm0 = max(abs(np.mean([v['value'] for v in start['vectors']],axis=0)))
    reduction = (float(1-terminal['decision']['current_norm']/norm0)
        if accepted else None)
    joint = bool(accepted and terminal['point']['joint_proximity'])
    return dict(status='joint-proximity' if joint else reason,accepted_steps=sum(r['decision']['accepted'] for r in steps),
        joint_proximity=joint,residual_reduction=reduction,
        reduction_at_least_twenty_percent=bool(accepted and reduction >= .2),symbolic_chains_verified=False)


def follow(numerical, receipt, measure, progress, completed=lambda *_:None):
    state = initialize(numerical,receipt)
    models,current = state['models'],receipt['proposal']
    rows,reason = [],'eight-step-limit'
    for number in range(1,9):
        proposal = propose(models,state['signs'],current,state['keys'],numerical['anchor'],number)
        slot = progress[number-1]
        slot['proposal'] = proposal
        if not proposal['qualified']:
            reason = 'proposal-gate-failed'
            slot['reason'] = proposal['reason']
            break
        slot['status'] = 'started'
        point = measure(warm_plan(numerical,current),proposal['spec'])
        decision = decide(numerical,state,models,current,point,proposal)
        entry = dict(proposal=proposal,point=point,decision=decision)
        rows.append(entry)
        slot.update(status='completed',accepted=decision['accepted'])
        completed(entry)
        if not decision['accepted']:
            reason = 'measured-step-rejected'
            break
        models,current = decision['updated_models'],point
        if point['joint_proximity']:
            reason = 'joint-proximity'
            break
    for slot in progress:
        if slot['status'] == 'not-run' and slot['reason'] is None:
            slot['reason'] = reason
    return dict(initialization=state,steps=rows,analysis=verdict(receipt['proposal'],rows,reason))


def ledger():
    return [dict(number=i,status='not-run',proposal=None,reason=None) for i in range(1,9)]
