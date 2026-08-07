# EXP-032 — Period-5 unit-event curve across a

Status: executed; coupled solves passed; frozen b-guard failed
Manifest: `experiments/manifests/EXP-032-period5-unit-event-a-curve.json`
Claim target: extension of the EXP-028 pitchfork-like event into parameter space

## Hypothesis and method

The coupled nontrivial `+1` event at `(a,b,c)=(0.245,0.27228406,5.1)` belongs
to a smooth local curve in `(a,b)` at fixed `c=5.1`, rather than being an
isolated degeneracy.

At nine frozen `a` values from `0.235` through `0.255`, reuse only the nearest
previously corrected event as a seed and solve the full periodic closure,
phase, nontrivial unit-eigenvector, normalization, and flow-orthogonality
system. Continue independently upward and downward from the accepted EXP-028
center; do not fit or extrapolate missing points after execution.

## Acceptance and limits

All nine points are required. Closure, nontrivial eigen, and flow-
orthogonality residuals must each remain at most `1e-8`; `b` must stay inside
`[0.24,0.31]`; and no adjacent corrected `b` jump may exceed `0.02`.

Passing establishes a local codimension-one event curve in this fixed-`c`
plane. It does not yet establish a surface in `(a,b,c)`, preserve the same
normal form everywhere, or connect this curve to the TBA/topology-change locus
and other shrimp families.

## Result

The clean run at commit `fab82c84c03ea5a9126624b228d77b37ba54e2d8`
corrected all nine requested events. Both continuation directions completed;
maximum closure was `2.63e-12`, maximum nontrivial eigen residual `5.48e-13`,
and maximum flow-orthogonality residual `1.37e-18`. The maximum adjacent `b`
jump was `0.00944`.

The curve moves monotonically from `(a,b)=(0.235,0.23841498)` through the
source `(0.245,0.27228406)` to `(0.255,0.30926346)`. The first point lies
`0.001585` below the frozen `b >= 0.24` guard, so the overall gate is failed
despite all coupled numerical solves passing. The complete receipt SHA-256 is
`78fd666ea9cd5714e93c4d319d596d54ce1c1f0361ae4c96240997c8b1d607d1`.

## Decision

Preserve the failed domain gate. Treat the nine solved points as strong
exploratory evidence for a smooth local event curve, not as a passing bounded-
domain experiment. EXP-033 prospectively freezes a materially wider `a` range
and `b` guard; this is domain expansion, not post-hoc redefinition of EXP-032.
