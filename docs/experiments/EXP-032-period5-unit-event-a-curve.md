# EXP-032 — Period-5 unit-event curve across a

Status: preregistered; pending clean local execution
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
