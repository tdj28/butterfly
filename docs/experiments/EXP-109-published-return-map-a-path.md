# EXP-109 — Prospective attracting-set bracket on the published `a` path

Status: preregistered; not yet executed

With EXP-108 qualifying the published section and both Figure 2 endpoint maps,
scan the declared path `b=0.2,c=20`, `a in [0.11,0.2]`. Freeze a `0.005` base
grid and include the paper's chaotic-saddle/stable-orbit controls `a=0.118` and
`a=0.149`, for 21 DOP853 integrations. Use the exact Barrio section
`x=x_minus`, `dx/dt>0`, 1200 crossings, the baseline gated oracle, primary `y`,
and cross-check `z`.

This is explicitly an attracting-set scan. First apply recurrence through
period 64. If the attracting state is periodic, report the return-map topology
as unresolved because the nonattracting chaotic invariant set was not sampled.
Do not pass repeated periodic points to the branch oracle and do not interpolate
across the gap. A bounded nonperiodic sequence remains an aperiodic candidate,
not a formally Lyapunov-qualified chaotic attractor, although the endpoint
roles have already been qualified in EXP-005/108.

Pass only if the published endpoints reproduce, all simultaneously resolved
`y`/`z` labels agree, and the resolved primary samples form an ordered bracket:
the largest resolved two-branch `a` is smaller than the smallest resolved
three-branch `a`. Retain all periodic and oracle-unresolved points. A pass
locates an attracting-set bracket but not the TBA inside it; refinement through
regular windows requires a separately qualified chaotic-saddle method.
