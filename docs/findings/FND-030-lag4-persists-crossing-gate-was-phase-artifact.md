# FND-030 — Lag 4 persists; the lag-12 crossing failure was a phase-window artifact

Status: qualified positive result and corrected technical interpretation of EXP-136

## Finding

The primitive unstable lag-4 orbit recovered on the three-branch side
continues through all 21 frozen parameter points to the two-branch endpoint.
Throughout `a in [0.148,0.14825]` it retains four oriented Barrio-section
crossings, flow closure below `3.44e-11`, neutral-multiplier accuracy near
`1e-10`, proper-divisor nonclosure above `5.36`, and unstable modulus from
`3.484` to `3.664`.

Its creation or destruction is therefore ruled out as the branch-opening
event inside this sampled interval. Its stable or unstable manifolds may still
undergo a tangency or pruning event.

Both lag-12 continuations fail their prospectively frozen crossing-identity
gate near their source endpoints. The lower path reports 11 rather than 12
oriented crossings at `a=0.148025`; the upper path does so at `a=0.1482375`.
At both failed points, periodic correction, flow closure, neutral multiplier,
primitivity, and strong transverse instability still pass.

A post-hoc boundary audit falsifies the initial section-grazing interpretation.
The shooting states lie extremely close to the Barrio section, and the first
positive crossing moves from the start boundary to `1.132e-6` and `1.054e-6`
after it. The frozen window extended only about `7.5e-7` beyond one period.
Counting over the phase-shifted interval `(0.1 T, 1.1 T]` restores 12 crossings
at every tested lag-12 point. Moreover, the closest orbit extrema are more
than `8.07` and `8.20` x-units from the section, respectively. There is no
numerical evidence here for a grazing.

## Consequence

The strict failure is a phase-window counting artifact, not a dynamical event.
It does not weaken the positive lag-4 persistence result, but it invalidates
the earlier inference that either lag-12 orbit loses a physical intersection
with the section. Section counts for periodic orbits must be taken over a full
period whose boundaries are safely displaced from a crossing.

The two lag-12 endpoint seeds are not yet proved equal or distinct. Their
declared midpoint identity comparison is invalid because neither fixed-lag
path reached the midpoint. The next prospective test must continue the closed
flow orbits without using section count as a stopping gate, record a
phase-shifted count, and perform phase-invariant family matching.

Tracked receipt: `docs/experiments/receipts/EXP-136.json`.
