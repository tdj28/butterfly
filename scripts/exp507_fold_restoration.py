"""One outcome-informed fixed-c correction; no target integrations here."""
import math
import numpy as np
from scripts import exp504_continuation_model as old


def propose(numerical, prior, rejected):
    keys = [r['key'] for r in numerical['base_vectors']]
    residuals = old.values(rejected['vectors'], keys)
    state = old.initialize(numerical, prior)
    matrices = np.asarray(state['fine'])
    slopes = matrices[:, 0, 0]
    if not rejected['qualified'] or not np.all(slopes > 1e-8):
        raise ValueError('qualified predecessor and positive resolved fold slopes required')
    mean_f = math.fsum(float(v) for v in residuals[:, 0])/256
    mean_j = math.fsum(float(v) for v in slopes)/256
    raw = -mean_f/mean_j
    delta = max(-.1, min(.1, raw))
    parameters = dict(rejected['spec']['parameters'])
    parameters['a'] += 1e-4*delta
    step = old.displacement(rejected['spec']['parameters'], parameters)
    if (parameters['b'] != .2 or step[1] != 0 or step[0] == 0
            or abs(parameters['a']-numerical['anchor']['a']) > .002
            or abs(step[0]) > .1+1e-12):
        raise ValueError('fixed-c nonzero bounded correction required')
    predicted = matrices@step
    return dict(spec=dict(id='fold-restoration', parameters=parameters),
        mean_fold=mean_f, mean_normalized_slope=mean_j,
        unclipped_normalized_step=raw, realized_normalized_step=step.tolist(),
        predicted=[dict(key=k, change=v.tolist()) for k,v in zip(keys,predicted,strict=True)],
        derivative_source='EXP-502/503 original fine stencil; not a new local derivative')


def decide(numerical, before, point, proposal):
    if point['spec'] != proposal['spec']:
        raise ValueError('unique frozen proposal identity differs')
    original = old.response.correspondence(point['cycle'], numerical['reference_cycle'])
    qualified = bool(point['qualified'] and point['correspondence']['passed'] and original['passed'])
    contact = point['contact']
    distance = contact['envelope']['pair_state_distance'][3] if contact is not None else None
    restored = bool(qualified and distance is not None and distance <= 1e-4)
    result = dict(status='fold-restored' if restored else 'fold-not-restored',
        qualified=qualified, original_correspondence=original, fold_restored=restored,
        worst_fold_distance=distance, joint_proximity=bool(restored and point['joint_proximity']),
        variant_changes=[], mean_signed_fold_reduction=None, half_signed_fold_reduction=False,
        symbolic_chains_verified=False)
    if qualified:
        keys = [r['key'] for r in numerical['base_vectors']]
        a,b = [old.values(r['vectors'],keys) for r in (before,point)]
        initial,final = [math.fsum(float(x) for x in v[:,0])/256 for v in (a,b)]
        reduction = 1-abs(final)/abs(initial) if initial != 0 else None
        result.update(mean_before=np.mean(a,axis=0).tolist(), mean_after=np.mean(b,axis=0).tolist(),
            mean_signed_fold_reduction=reduction,
            half_signed_fold_reduction=bool(reduction is not None and reduction >= .5),
            variant_changes=[dict(key=k, predicted=p['change'], observed=d.tolist())
                for k,p,d in zip(keys,proposal['predicted'],b-a,strict=True)])
    return result
