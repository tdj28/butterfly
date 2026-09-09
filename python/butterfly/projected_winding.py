"""Read-only planar polygon winding diagnostics, not validated ODE topology."""
import numpy as np


def hermite(left,right,ql,qr,fl,fr,t):
    """Cubic state interpolant from retained endpoint states and vector fields."""
    if not left < right or not left <= t <= right:
        raise ValueError("interpolation outside a strict retained interval")
    s = (t-left)/(right-left)
    ql,qr,fl,fr = map(np.asarray,(ql,qr,fl,fr))
    return (2*s**3-3*s*s+1)*ql+(s**3-2*s*s+s)*(right-left)*fl+(-2*s**3+3*s*s)*qr+(s**3-s*s)*(right-left)*fr


def polygon_measure(points,*,radius_floor=1e-10,angle_ceiling=2.9):
    """Compute a polygon's signed angle and minimum segment radius exactly.

    Guards reject numerical ambiguity in this polygon; they do not prove
    that an unknown smooth curve between its vertices has no hidden loops.
    """
    q = np.asarray(points,dtype=float)
    if q.ndim != 2 or q.shape[1] != 2 or len(q) < 2 or not np.isfinite(q).all():
        raise ValueError("finite ordered planar polygon required")
    a,b = q[:-1],q[1:]
    delta = b-a
    lengths = np.sum(delta*delta,axis=1)
    s = np.divide(-np.sum(a*delta,axis=1),lengths,out=np.zeros_like(lengths),where=lengths>0)
    closest = a+np.clip(s,0.,1.)[:,None]*delta
    radius = float(np.min(np.linalg.norm(closest,axis=1)))
    if radius == 0. or np.any(np.linalg.norm(q,axis=1) == 0.):
        return dict(qualified=False,reason="polygon intersects winding origin",minimum_radius=radius,
            angle_change=None,endpoint_difference=None,cut_index=None,maximum_angle_step=None,integer_error=None)
    angles = np.arctan2(a[:,0]*b[:,1]-a[:,1]*b[:,0],np.sum(a*b,axis=1))
    change = float(np.sum(angles))
    endpoint = float(np.arctan2(q[-1,1],q[-1,0])-np.arctan2(q[0,1],q[0,0]))
    turns = (change-endpoint)/(2*np.pi)
    index = int(np.rint(turns))
    error = abs(turns-index)
    maximum = float(np.max(np.abs(angles)))
    qualified = radius >= radius_floor and maximum <= angle_ceiling and error <= 1e-10
    return dict(qualified=bool(qualified),reason=None if qualified else "radius/angular/integer guard failed",
        minimum_radius=radius,angle_change=change,endpoint_difference=endpoint,cut_index=index,
        maximum_angle_step=maximum,integer_error=error)


def window_nodes(times,states,extrema,field,start,end):
    """Raw mesh plus extrema; crossing roots are deliberately not inputs."""
    times,states = np.asarray(times),np.asarray(states)
    if times.ndim != 1 or states.shape != (len(times),3) or not np.isfinite(times).all() or not np.isfinite(states).all() or not np.all(np.diff(times)>0) or not times[0] <= start < end <= times[-1]:
        raise ValueError("finite retained mesh containing the window required")
    def endpoint(t):
        j = int(np.searchsorted(times,t))
        if j < len(times) and times[j] == t:
            return states[j].copy()
        return hermite(times[j-1],times[j],states[j-1],states[j],field(times[j-1],states[j-1]),field(times[j],states[j]),t)
    nodes = {float(t):q.copy() for t,q in zip(times,states,strict=True) if start < t < end}
    nodes[start],nodes[end] = endpoint(start),endpoint(end)
    raw = [(t,nodes[t]) for t in sorted(nodes)]
    for e in extrema:
        t,q = e["time"],np.asarray(e["state"])
        if not np.isfinite(t) or q.shape != (3,) or not np.isfinite(q).all():
            raise ValueError("nonfinite extremum node")
        if start < t < end:
            if t in nodes and not np.allclose(nodes[t],q,rtol=0,atol=1e-10):
                raise ValueError("duplicate retained node disagrees")
            nodes[t] = q
    base = [(t,nodes[t]) for t in sorted(nodes)]
    refined = []
    for (ta,qa),(tb,qb) in zip(base[:-1],base[1:],strict=True):
        mid = (ta+tb)/2
        refined.extend(((ta,qa),(mid,hermite(ta,tb,qa,qb,field(ta,qa),field(tb,qb),mid))))
    refined.append(base[-1])
    return dict(raw=raw,extrema_augmented=base,midpoint_enriched=refined)


def compare_polygons(nodes,origin,*,radius_floor=1e-10,angle_ceiling=2.9,angle_agreement=1e-6):
    origin = np.asarray(origin)
    if origin.shape != (2,) or not np.isfinite(origin).all():
        raise ValueError("finite planar origin required")
    measures = {k:polygon_measure(np.array([q[:2]-origin for _,q in v]),radius_floor=radius_floor,angle_ceiling=angle_ceiling) for k,v in nodes.items()}
    a,b = measures["extrema_augmented"],measures["midpoint_enriched"]
    error = abs(a["angle_change"]-b["angle_change"]) if a["angle_change"] is not None and b["angle_change"] is not None else None
    qualified = a["qualified"] and b["qualified"] and a["cut_index"] == b["cut_index"] and error is not None and error <= angle_agreement
    return dict(qualified=bool(qualified),measures=measures,refinement_angle_error=error,
        node_counts={k:len(v) for k,v in nodes.items()})
