"""Finite curve-sampling diagnostics; a grid never certifies global root absence."""
import math
import numpy as np
from butterfly.return_image_curve import observe_curve,candidate_intervals
from butterfly.projected_fold_qualification import image_from_census


def grid(candidate, roots):
    left,right = candidate['u_box']
    if len(roots)!=2 or not np.isfinite([left,right,candidate['epsilon'],*roots]).all() or candidate['epsilon']<=0 or not left<right:
        raise ValueError('finite ordered grid declaration required')
    center = math.fsum(roots)/2
    eps = candidate['epsilon']
    values = sorted(set([math.fsum([left,(right-left)*i/16]) for i in range(17)]
        +[center-eps,center,center+eps]))
    if len(roots) != 2 or not left < center-eps < center+eps < right or len(values) > 20:
        raise ValueError('complete in-domain diagnostic anchors required')
    return values


def observation(report,candidate,rhs,section,thresholds):
    image = image_from_census(report,candidate['count'],rhs,section,thresholds)
    return dict(image=image,observation=observe_curve(image,
        minimum_gain=thresholds['minimum_gain'],minimum_x_component=thresholds['minimum_x_component']))


def pair(profiles,scales):
    if [p['method'] for p in profiles] != ['DOP853','Radau']:
        raise ValueError('complete ordered solver pair required')
    result = dict(event_agreement=False,regular=False,state_difference=None,time_difference=None,
        tangent_difference=None,reason='missing or unqualified event prefix')
    if not all(p['status']=='completed' and p['measurement']['image']['status']=='returned' for p in profiles):
        return result
    events = [p['measurement']['image']['events'] for p in profiles]
    if len(events[0]) != len(events[1]) or len(events[0])<2:
        return result
    if not np.isfinite(scales).all() or np.asarray(scales).shape!=(3,) or min(scales)<=0:
        raise ValueError('positive finite state scales required')
    for rows in events:
        for event in rows:
            if not np.isfinite([event['time'],*event['state'],*event['tangent']]).all():
                raise ValueError('nonfinite event comparison')
    state = max(float(np.max(abs((np.asarray(a['state'])-b['state'])/scales)))
        for a,b in zip(*events,strict=True))
    time = max(abs(a['time']-b['time']) for a,b in zip(*events,strict=True))
    agreement = state <= 1e-6 and time <= 1e-7
    obs = [p['measurement']['observation'] for p in profiles]
    tangent = None
    regular = False
    if agreement and all(o['valid'] for o in obs):
        a,b = [np.asarray(e[-2]['tangent'])[[0,2]]/[15.,.01] for e in events]
        a,b = a/np.linalg.norm(a),b/np.linalg.norm(b)
        tangent = float(np.max(abs(a-b)))
        slopes = [o['x_graph_slope'] for o in obs]
        regular = tangent <= 1e-6 and abs(slopes[0]-slopes[1]) <= 1e-6*max(1.,*map(abs,slopes))
    return dict(event_agreement=bool(agreement),regular=bool(regular),state_difference=state,
        time_difference=time,tangent_difference=tangent,
        reason=None if regular else 'solver disagreement or irregular input curve')


def analyze(candidate,samples,targets):
    if [s['u'] for s in samples] != candidate['grid']:
        raise ValueError('complete fixed grid in order required')
    if len(targets) != 4:
        raise ValueError('all depth-4 comparison states required')
    if any(not np.isfinite([*t['image_state'],*t['next_state']]).all() for t in targets):
        raise ValueError('nonfinite reference target')
    methods = ['DOP853','Radau']
    per_method = []
    for method in methods:
        observed = []
        distances = []
        for i,sample in enumerate(samples):
            p = next(p for p in sample['profiles'] if p['method']==method)
            o = p['measurement']['observation'] if p['status']=='completed' else dict(valid=False)
            observed.append(o if sample['pair']['regular'] else dict(o,valid=False))
            if 'image_state' in o:
                distances.append(dict(index=i,u=sample['u'],regular=sample['pair']['regular'],
                    input_distances=[float(np.max(abs((np.asarray(o['image_state'])-t['image_state'])/[15.,15.,.01]))) for t in targets],
                    output_distances=[float(np.max(abs((np.asarray(o['next_state'])-t['next_state'])/[15.,15.,.01]))) for t in targets],
                    input_x=o['image_state'][0]))
        turns = []
        for i,(a,b) in enumerate(zip(observed[:-1],observed[1:],strict=True)):
            x,y = a.get('input_x_tangent'),b.get('input_x_tangent')
            if x is not None and y is not None and x*y <= 0:
                turns.append([i,i+1])
        per_method.append(dict(method=method,candidate_brackets=candidate_intervals(observed),
            input_coordinate_turn_cells=turns,distances=distances,
            sampled_input_range=None if not distances else [min(d['input_x'] for d in distances),max(d['input_x'] for d in distances)]))
    common = per_method[0]['candidate_brackets']==per_method[1]['candidate_brackets']
    invalid = [i for i,s in enumerate(samples) if not s['pair']['regular']]
    cells = [[i,i+1] for i in range(len(samples)-1)]
    return dict(family_id=candidate['family_id'],samples=len(samples),regular_samples=len(samples)-len(invalid),
        unresolved_sample_indices=invalid,per_method=per_method,bracket_sets_agree=common,
        matched_candidate_brackets=per_method[0]['candidate_brackets'] if common else [],
        all_unsampled_cells_not_certified=cells,global_root_absence_proved=False,
        exact_flow_root_isolation=False,symbolic_chains_verified=False,
        scope='Endpoint-regular numerical bracket candidates and sampled state coverage only; no continuity enclosure or root-absence proof between samples.')
