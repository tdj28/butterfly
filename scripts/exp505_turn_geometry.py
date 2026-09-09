"""Additional turning geometry for an explicitly retrospective sensitivity."""
import numpy as np
from scipy.optimize import brentq
from butterfly import return_map as legacy


def inspect(spline,*,grid_size,minimum_prominence):
    derivative = spline.derivative()
    grid = np.linspace(0.,1.,grid_size)
    values = derivative(grid)
    roots = []
    for left,right,a,b in zip(grid[:-1],grid[1:],values[:-1],values[1:],strict=True):
        if a == 0.:
            roots.append(float(left))
        elif a*b < 0.:
            roots.append(float(brentq(derivative,left,right)))
    unique = []
    for root in roots:
        if 1e-6 < root < 1.-1e-6 and (not unique or abs(root-unique[-1]) > 2./grid_size):
            unique.append(root)
    landmarks = [0.,*unique,1.]
    rows = []
    for index,root in enumerate(unique,1):
        left,right = landmarks[index-1],landmarks[index+1]
        value = float(spline(root))
        changes = [value-float(spline(q)) for q in (left,right)]
        prominent = min(map(abs,changes)) >= minimum_prominence
        delta = min(1./(grid_size-1),(root-left)/4,(right-root)/4)
        probes = [root-delta,root+delta]
        slopes = [float(derivative(q)) for q in probes]
        signs = bool(np.isfinite(slopes).all() and slopes[0]*slopes[1] < 0.)
        heights = bool(np.isfinite(changes).all() and changes[0]*changes[1] > 0.)
        rows.append(dict(root=root,neighbors=[left,right],probes=probes,slopes=slopes,
            signed_height_changes=changes,legacy_retained=prominent,opposite_derivatives=signs,
            extremum_heights=heights,filtered_retained=bool(prominent and signs and heights)))
    return dict(candidates=rows,legacy=[r['root'] for r in rows if r['legacy_retained']],
        filtered=[r['root'] for r in rows if r['filtered_retained']])


def pairs(states,times,ids,axis):
    states,times,ids = map(np.asarray,(states,times,ids))
    if (states.shape != (len(times),3) or ids.shape != times.shape or times.ndim != 1
            or not np.isfinite(states).all() or not np.isfinite(times).all()
            or ids.dtype.kind not in 'iu' or axis not in (0,2)):
        raise ValueError('finite authenticated midpoint arrays required')
    # Separate implementation from survivor_return_pairs: adjacent sorted
    # records are selected by equality, instead of splitting at ID boundaries.
    order = sorted(range(len(times)),key=lambda i:(int(ids[i]),float(times[i])))
    left,right = [],[]
    for a,b in zip(order[:-1],order[1:],strict=True):
        if ids[a] == ids[b]:
            if not times[a] < times[b]:
                raise ValueError('strictly ordered distinct returns required')
            left.append(states[a,axis])
            right.append(states[b,axis])
    return np.asarray(left),np.asarray(right)


class Analytic:
    def __init__(self,kind):
        self.kind = kind

    def __call__(self,x):
        if self.kind == 'stationary-inflection':
            return (x-.5)**3
        if self.kind == 'two-turn':
            return x**3/3-.5*x*x+.21*x
        factor = {'maximum':-1.,'minimum':1.,'low-prominence':.01}[self.kind]
        return factor*(x-.5)**2

    def derivative(self):
        if self.kind == 'stationary-inflection':
            return lambda x:3*(x-.5)**2
        if self.kind == 'two-turn':
            return lambda x:(x-.3)*(x-.7)
        factor = {'maximum':-1.,'minimum':1.,'low-prominence':.01}[self.kind]
        return lambda x:2*factor*(x-.5)


def controls():
    rows = []
    for kind,old_count,new_count,prominence in [('stationary-inflection',1,0,.03),
            ('maximum',1,1,.03),('minimum',1,1,.03),('two-turn',2,2,.001),('low-prominence',0,0,.03)]:
        spline = Analytic(kind)
        row = inspect(spline,grid_size=4097,minimum_prominence=prominence)
        old = legacy._critical_points(spline,grid_size=4097,minimum_prominence=prominence)
        if row['legacy'] != list(old) or len(old) != old_count or len(row['filtered']) != new_count:
            raise ValueError('analytic turning control failed: '+kind)
        rows.append(dict(kind=kind,passed=True,geometry=row))
    return dict(passed=True,cases=rows,target_integrations=0)
