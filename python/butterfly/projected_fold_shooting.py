"""Fixed-time determinant equations for a projected fold of an event map."""
import numpy as np
from scipy.integrate import solve_ivp


def equations(q, v, w, f, j, offset):
    q,v,w,f,j = map(np.asarray,(q,v,w,f,j))
    if any(x.shape != (3,) or not np.isfinite(x).all() for x in (q,v,w,f)) or j.shape != (3,3) or not np.isfinite(j).all() or not np.isfinite(offset):
        raise ValueError("malformed or nonfinite fold inputs")
    jv,jf = j@v,j@f
    g = f[1]*v[0]-f[0]*v[1]
    gu = jv[1]*v[0]+f[1]*w[0]-jv[0]*v[1]-f[0]*w[1]
    gt = jf[1]*v[0]+f[1]*jv[0]-jf[0]*v[1]-f[0]*jv[1]
    residual = np.array([q[1]-offset,g])
    matrix = np.array([[v[1],f[1]],[gu,gt]])
    if not np.isfinite(residual).all() or not np.isfinite(matrix).all():
        raise ValueError("nonfinite fold equations")
    return residual,matrix


def event_second_derivative(v, f, j, residual, matrix):
    v,f,j = map(np.asarray,(v,f,j))
    if f[1] == 0:
        raise ValueError("tangent event has no regular event derivative")
    tau = -v[1]/f[1]
    return float((matrix[1,0]+matrix[1,1]*tau)/f[1]-residual[1]*(j@(v+f*tau))[1]/f[1]**2)


def shoot(rhs,jac,hvv,candidate,section,method,plan,retain):
    q0,v0 = np.asarray(candidate["initial_state"]),np.asarray(candidate["initial_tangent"])
    u,t = candidate["seed_u"],candidate["seed_time"]
    trace = []
    for iteration in range(plan["iterations"]):
        def field(time,state):
            q,v,w = state[:3],state[3:6],state[6:]
            j = jac(time,q)
            return np.r_[rhs(time,q),j@v,j@w+hvv(time,q,v)]
        sol = solve_ivp(field,(0.,t),np.r_[q0+u*v0,v0,np.zeros(3)],method=method,
                        **{k:plan[k] for k in ("rtol","atol","max_step")})
        retain(iteration,dict(integration_times=sol.t,integration_augmented_states=sol.y.T))
        if not sol.success or not np.isfinite(sol.y).all():
            trace.append(dict(iteration=iteration,u=u,time=t,integration_failed=True,
                              observed_last_time=float(sol.t[-1]),finite_states=bool(np.isfinite(sol.y).all())))
            return dict(converged=False,reason="integration failed",trace=trace)
        q,v,w = sol.y[:3,-1],sol.y[3:6,-1],sol.y[6:,-1]
        f,j = rhs(t,q),jac(t,q)
        residual,matrix = equations(q,v,w,f,j,section.offset)
        scale = max(1.,float(np.linalg.norm(f)*np.linalg.norm(v)))
        row = dict(iteration=iteration,u=u,time=t,state=q.tolist(),first=v.tolist(),second=w.tolist(),
                   residual=residual.tolist(),jacobian=matrix.tolist(),determinant_scale=scale,
                   angle=float(abs(f[1])/np.linalg.norm(f)) if np.linalg.norm(f) else 0.)
        trace.append(row)
        if abs(residual[0]) <= plan["root_plane"] and abs(residual[1])/scale <= plan["root_determinant"]:
            if row["angle"] >= plan["thresholds"]["angle"]:
                row["event_second_derivative"] = event_second_derivative(v,f,j,residual,matrix)
            return dict(converged=True,reason="equation tolerances",trace=trace)
        try:
            step = np.linalg.solve(matrix,residual)
        except np.linalg.LinAlgError:
            return dict(converged=False,reason="singular Newton matrix",trace=trace)
        row["newton_step"] = step.tolist()
        u,t = float(u-step[0]),float(t-step[1])
        if not candidate["u_box"][0] <= u <= candidate["u_box"][1] or not candidate["time_box"][0] <= t <= candidate["time_box"][1] or t <= 0:
            return dict(converged=False,reason="fixed search box exceeded",trace=trace)
    return dict(converged=False,reason="iteration limit",trace=trace)
