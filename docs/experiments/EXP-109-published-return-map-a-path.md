# EXP-109 — Prospective attracting-set bracket on the published `a` path

Status: executed; ordered attracting-set bracket passed

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

The clean run at `534fba12e9b2eeb1d5c164a4b29d49f83641245f` passed. The
resolved primary two-branch values are `0.11,0.115,0.13,0.15,0.155`; the
resolved three-branch values are
`0.16,0.165,0.17,0.175,0.185,0.19,0.195,0.2`. No resolved coordinate
classification contradicts another, and the ordered attracting-set bracket is
therefore `[0.155,0.16]`.

Five points (`0.118,0.12,0.14,0.145,0.149`) converge to period-4 attractors and
are correctly retained as missing chaotic-saddle topology. Three additional
points (`0.125,0.135,0.18`) are aperiodic under the finite recurrence test but
fail invariant-domain coverage, so they remain unresolved.

The lower bracket endpoint is not a sharp boundary estimate. At `a=0.155`,
the primary `y` map returns two branches at exactly the minimum bootstrap
consensus `0.80`, while `z` is unresolved at consensus `0.70` and its nominal
fit has two critical points. At `a=0.16`, both coordinates return three with
consensus `1.0`. The scientifically honest result is a transition uncertainty
band, with the PRL's nonattracting-saddle TBA potentially lying elsewhere
inside the regular region. Full receipt SHA-256:
`a1595b999f7b52b0b492936e0229b613d41c9df5e3bee9e7749fcb64ca65f2a6`.
