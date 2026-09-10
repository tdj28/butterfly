"""Retain and replay six-dimensional SciPy dense polynomials, without new IVPs.

Extrema are solver-detected, not rigorously isolated. Replaying the interpolant
checks evidence consistency, not an independent integration or exact ODE proof.
"""
from unittest.mock import patch
import numpy as np
from scipy.optimize import brentq
from butterfly import section_census
from butterfly.periodic_winding import dense_value
from scripts import exp511_curve_coverage as model


def capture(candidate,u,method,settings,rhs,jacobian,section,retain,budget):
    initial = np.asarray(candidate['initial_state'])+u*np.asarray(candidate['initial_tangent'])
    tangent = np.asarray(candidate['initial_tangent'])
    original = section_census.solve_ivp
    products = []
    def solve(*args,**kwargs):
        budget(True)
        solution = original(*args,**kwargs)
        name = 'main' if kwargs.get('dense_output') else 'guard'
        raw = dict(times=solution.t,augmented_states=solution.y.T,
            success=np.array(solution.success),nfev=np.array(solution.nfev),njev=np.array(solution.njev))
        if name == 'main':
            segments = solution.sol.interpolants
            raw.update(dense_old=np.asarray([s.y_old for s in segments]),
                dense_coefficients=np.asarray([s.F if method=='DOP853' else s.Q for s in segments]))
            for i,label in enumerate(('plane','extrema')):
                raw[label+'_times'] = np.asarray(solution.t_events[i])
                raw[label+'_augmented_states'] = np.asarray(solution.y_events[i]).reshape(-1,6)
        # Retain failed solutions too, before the census collector can raise.
        retain(name,raw)
        products.append(name)
        return solution
    options = {k:settings[k] for k in ('rtol','atol','max_step','guard','extremum_margin')}
    try:
        with patch.object(section_census,'solve_ivp',solve):
            report,_ = section_census.collect(rhs,jacobian,initial,tangent,section,
                method=method,horizon=candidate['horizon'],**options)
    except ValueError as exc:
        if str(exc) not in ('guard integration failed','census integration failed'):
            raise
        return dict(method=method,status='integration-failed',reason=str(exc),products=products)
    return dict(method=method,status='completed',products=products,report=report,
        measurement=model.observation(report,candidate,rhs,section,settings['thresholds']))


def close(a,b,message,atol=1e-10):
    a,b = np.asarray(a),np.asarray(b)
    if a.shape != b.shape or not np.isfinite(a).all() or not np.isfinite(b).all() or not np.allclose(a,b,rtol=1e-12,atol=atol):
        raise ValueError(message)


def replay(profile,candidate,u,settings,rhs,section,raws):
    expected = ['guard','main'] if profile['status']=='completed' or profile.get('reason')=='census integration failed' else ['guard']
    if profile['products'] != expected or set(raws) != set(expected):
        raise ValueError('complete guard/main product matrix required')
    initial = np.r_[np.asarray(candidate['initial_state'])+u*np.asarray(candidate['initial_tangent']),candidate['initial_tangent']]
    for name,raw in raws.items():
        t,q = raw['times'],raw['augmented_states']
        if (t.ndim != 1 or len(t)<1 or q.shape!=(len(t),6) or not np.isfinite(t).all()
                or not np.all(np.diff(t)>0) or int(raw['nfev'])<1):
            raise ValueError('malformed retained solver mesh')
        if bool(raw['success']) and not np.isfinite(q).all():
            raise ValueError('successful mesh nonfinite')
    guard = raws['guard']
    if guard['times'][0] != 0 or not np.array_equal(guard['augmented_states'][0],initial):
        raise ValueError('guard initial identity differs')
    if profile['status']!='completed':
        failed = raws[expected[-1]]
        if profile['status']!='integration-failed' or (bool(failed['success']) and np.isfinite(failed['augmented_states']).all()):
            raise ValueError('failed profile has no failed numerical product')
        if expected==['guard','main']:
            if not bool(guard['success']) or guard['times'][-1]!=settings['guard'] or not np.array_equal(guard['augmented_states'][-1],failed['augmented_states'][0]):
                raise ValueError('failed main guard continuity differs')
        return {k:profile[k] for k in ('method','status','reason','products')}
    raw = raws['main']
    t,q = raw['times'],raw['augmented_states']
    method = profile['method']
    shape = (len(t)-1,7,6) if method=='DOP853' else (len(t)-1,6,3)
    if (method not in ('DOP853','Radau') or not bool(guard['success']) or not bool(raw['success'])
            or guard['times'][-1]!=settings['guard'] or t[0]!=settings['guard'] or t[-1]!=candidate['horizon']
            or not np.array_equal(guard['augmented_states'][-1],q[0])
            or raw['dense_old'].shape!=(len(t)-1,6) or raw['dense_coefficients'].shape!=shape
            or not np.isfinite(raw['dense_coefficients']).all()):
        raise ValueError('dense mesh/configuration/guard continuity differs')
    close(raw['dense_old'],q[:-1],'dense left endpoints differ')
    coefficients = raw['dense_coefficients']
    end = raw['dense_old']+(coefficients[:,0,:] if method=='DOP853' else coefficients.sum(axis=2))
    close(end,q[1:],'dense right endpoints differ')
    for label in ('plane','extrema'):
        times,values = raw[label+'_times'],raw[label+'_augmented_states']
        if times.ndim!=1 or values.shape!=(len(times),6) or not np.all(np.diff(times)>0):
            raise ValueError('dense event matrix differs')
        for time,value in zip(times,values,strict=True):
            close(dense_value(raw,method,time),value,'dense solver event differs')
            residual = section.value(value[:3]) if label=='plane' else np.asarray(section.normal)@rhs(time,value[:3])
            if not np.isfinite(residual) or abs(residual)>1e-8:
                raise ValueError('retained event is not a numerical root')
    def record(time,value):
        state = np.asarray(value)[:3]
        field = np.asarray(rhs(float(time),state))
        normal = np.asarray(section.normal)
        velocity = float(normal@field)
        return dict(time=float(time),state=state.tolist(),raw_tangent=np.asarray(value)[3:].tolist(),
            normal_velocity=velocity,angle=float(abs(velocity)/(np.linalg.norm(normal)*np.linalg.norm(field))),
            residual=section.value(state),accepted=bool(section.accepts(state) and section.direction*velocity>0))
    ordinary = [record(time,value) for time,value in zip(raw['plane_times'],raw['plane_augmented_states'],strict=True)]
    extrema = [dict(record(time,value),plane_value=section.value(value[:3])) for time,value in zip(raw['extrema_times'],raw['extrema_augmented_states'],strict=True)]
    knots = np.unique(np.r_[settings['guard'],raw['extrema_times'],candidate['horizon']])
    values = [section.value(dense_value(raw,method,time)[:3]) for time in knots]
    reconstructed = []
    for left,right,a,b in zip(knots[:-1],knots[1:],values[:-1],values[1:],strict=True):
        if a*b<0:
            time = brentq(lambda time:section.value(dense_value(raw,method,time)[:3]),left,right,xtol=1e-12,rtol=1e-14)
            reconstructed.append(dict(record(time,dense_value(raw,method,time)),bracket=[float(left),float(right)]))
    report = dict(method=method,max_step=settings['max_step'],rtol=settings['rtol'],atol=settings['atol'],
        horizon=candidate['horizon'],guard=settings['guard'],initial_state=initial[:3].tolist(),initial_tangent=initial[3:].tolist(),
        ordinary=ordinary,reconstructed=reconstructed,extrema=extrema,
        uncertain_extrema=[dict(time=v['time'],plane_value=v['plane_value'],state=v['state']) for v in extrema if abs(v['plane_value'])<=settings['extremum_margin']],
        knots=knots.tolist(),knot_values=values,nfev=int(raw['nfev']),njev=int(raw['njev']),numerical_all_root_proof=False)
    return dict(method=method,status='completed',products=expected,report=report,
        measurement=model.observation(report,candidate,rhs,section,settings['thresholds']))
