"""One predictor/corrector pair with explicit fold and boundary decisions."""
from decimal import Decimal as D
import math
import numpy as np
from scripts import exp504_continuation_model as old


def mean_component(vectors, index):
    return math.fsum(float(v[index]) for v in vectors)/len(vectors)


def initialize(numerical, first, rejected, restored):
    state = old.initialize(numerical,first)
    keys = state['keys']
    step = old.displacement(rejected['spec']['parameters'],restored['spec']['parameters'])
    if step[1] != 0 or step[0] == 0 or not all(v['qualified'] for v in (rejected,restored)):
        raise ValueError('qualified fixed-c historical secant required')
    delta = old.values(restored['vectors'],keys)-old.values(rejected['vectors'],keys)
    fine = np.asarray(state['fine'])
    models = fine.copy()
    models[:,:,0] = delta/step[0]
    errors = np.linalg.norm(models[:,:,0]-fine[:,:,0],axis=1)/np.linalg.norm(fine[:,:,0],axis=1)
    check = old.model_check(models,state['signs'])
    if (not check['passed'] or not np.all(models[:,0,0] > 1e-8) or not np.all(errors <= .1)):
        raise ValueError('historical a-secant qualification failed')
    # Separate scalar arithmetic verifies the measured column; c column is unchanged.
    scalar = [[(b['value'][i]-a['value'][i])/float(step[0]) for i in (0,1)]
        for a,b in zip(rejected['vectors'],restored['vectors'],strict=True)]
    if not np.allclose(models[:,:,0],scalar,rtol=1e-12,atol=1e-13):
        raise ValueError('scalar a secant differs')
    return dict(keys=keys,models=models.tolist(),check=check,historical_step=step.tolist(),
        a_column_relative_errors=errors.tolist(),maximum_a_column_relative_error=float(max(errors)),
        provenance='a column: EXP-504 to EXP-507 measured secant; c column: original EXP-502/503 fine stencil; not a newly measured full Jacobian')


def qualification(numerical,start,point):
    original = old.response.correspondence(point['cycle'],numerical['reference_cycle'])
    anchor = old.response.correspondence(point['cycle'],start['cycle'])
    qualified = bool(point['qualified'] and point['correspondence']['passed'] and original['passed'] and anchor['passed'])
    distance = point['contact']['envelope']['pair_state_distance'][3] if point['contact'] is not None else None
    return dict(qualified=qualified,original_correspondence=original,start_correspondence=anchor,
        fold_proximity=bool(qualified and distance is not None and distance <= 1e-4),worst_fold_distance=distance)


def proposal(state,current,origin,kind):
    if kind not in ('predictor','corrector'):
        raise ValueError('fixed two-stage proposal required')
    values = old.values(current['vectors'],state['keys'])
    models = np.asarray(state['models'])
    parameters = dict(current['spec']['parameters'])
    if kind == 'predictor':
        parameters['c'] -= .02
    dc = (parameters['c']-current['spec']['parameters']['c'])/.002
    j11,j12 = [math.fsum(float(m[0,k]) for m in models)/256 for k in (0,1)]
    f = mean_component(values,0)
    raw = -(f+j12*dc)/j11
    da = raw if kind == 'predictor' else max(-.1,min(.1,raw))
    parameters['a'] += .0001*da
    step = old.displacement(current['spec']['parameters'],parameters)
    valid = (parameters['b'] == origin['b'] == .2 and abs(da) <= .1 and abs(step[0]) <= .1+1e-12
        and abs(parameters['a']-origin['a']) <= .002 and origin['c']-.2 <= parameters['c'] <= origin['c']
        and (step[1] < 0 if kind == 'predictor' else step[1] == 0 and step[0] != 0))
    predictions = [[math.fsum(float(matrix[i,k])*float(step[k]) for k in (0,1)) for i in (0,1)] for matrix in models]
    if not np.allclose(predictions,models@step,rtol=1e-12,atol=1e-13):
        raise ValueError('scalar prediction arithmetic differs')
    return dict(qualified=bool(valid),reason=None if valid else 'proposal domain or step bound',
        spec=dict(id=kind,parameters=parameters),mean_signed_fold=f,unclipped_a_step=float(raw),
        realized_step=step.tolist(),predictions=[dict(key=k,change=v)
            for k,v in zip(state['keys'],predictions,strict=True)])


def point_changes(state,before,after,proposed):
    old_values,new_values = [old.values(p['vectors'],state['keys']) for p in (before,after)]
    changes = new_values-old_values
    return [dict(key=k,predicted=p['change'],observed=v.tolist())
        for k,p,v in zip(state['keys'],proposed['predictions'],changes,strict=True)]


def endpoint(numerical,start,point,check,keys):
    result = dict(accepted=False,qualified=check['qualified'],fold_proximity=check['fold_proximity'],
        worst_fold_distance=check['worst_fold_distance'],boundary_improved=False,all_variant_boundary_improvement=False,
        start_boundary_distance=start['boundary_analysis']['cycle_indices'][1]['maximum_distance'],
        terminal_boundary_distance=None,boundary_reduction=None,joint_proximity=False,symbolic_chains_verified=False)
    if not check['qualified']:
        return result
    before,after = [old.values(p['vectors'],keys) for p in (start,point)]
    initial = D(result['start_boundary_distance'])
    final = D(point['boundary_analysis']['cycle_indices'][1]['maximum_distance'])
    all_variants = bool(np.all(abs(after[:,1]) < abs(before[:,1])))
    accepted = bool(check['fold_proximity'] and final < initial and all_variants)
    result.update(accepted=accepted,boundary_improved=final < initial,all_variant_boundary_improvement=all_variants,
        terminal_boundary_distance=str(final),boundary_reduction=1-float(final)/float(initial),
        joint_proximity=bool(accepted and point['joint_proximity']))
    return result


def ledger():
    return [dict(id=k,status='not-run',reason=None) for k in ('predictor','corrector')]


def follow(numerical,first,rejected,start,measure,progress,completed=lambda *_:None):
    state = initialize(numerical,first,rejected,start)
    entries = []
    current = start
    reason = 'two-stage-limit'
    baseline = None
    correction_waived = False
    for i,kind in enumerate(('predictor','corrector')):
        if kind == 'corrector':
            check = entries[0]['qualification']
            if not check['qualified']:
                reason = 'predictor-unqualified'
                progress[i]['reason'] = reason
                break
            f = mean_component(old.values(current['vectors'],state['keys']),0)
            if abs(f) <= 1e-12:
                correction_waived = check['fold_proximity']
                reason = 'correction-not-needed' if correction_waived else 'scalar-floor-without-full-state-proximity'
                progress[i]['reason'] = reason
                break
        proposed = proposal(state,current,numerical['anchor'],kind)
        if not proposed['qualified']:
            reason = kind+'-proposal-rejected'
            progress[i]['reason'] = reason
            break
        progress[i]['status'] = 'started'
        point = measure(old.warm_plan(numerical,current),proposed['spec'])
        if point['spec'] != proposed['spec']:
            raise ValueError('sole sequential proposal identity differs')
        check = qualification(numerical,start,point)
        entry = dict(proposal=proposed,point=point,qualification=check,
            changes=point_changes(state,current,point,proposed) if check['qualified'] else [])
        entries.append(entry)
        progress[i]['status'] = 'completed'
        completed(entry)
        if i == 0:
            baseline = endpoint(numerical,start,point,check,state['keys'])
        current = point
    for row in progress:
        if row['status'] == 'not-run' and row['reason'] is None:
            row['reason'] = reason
    complete = len(entries) == 2 or correction_waived
    final = endpoint(numerical,start,current,entries[-1]['qualification'],state['keys']) if entries else None
    accepted = bool(complete and final is not None and final['accepted'])
    return dict(initialization=state,entries=entries,analysis=dict(accepted=accepted,
        status='accepted-step' if accepted else reason if not complete else 'terminal-rejected',
        completed_points=len(entries),correction_waived=correction_waived,predictor_only_baseline=baseline,
        terminal=final,joint_proximity=bool(accepted and final['joint_proximity']),symbolic_chains_verified=False))
