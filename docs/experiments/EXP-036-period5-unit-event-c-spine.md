# EXP-036 — Period-5 unit-event spine across c

Status: preregistered; pending clean local execution
Manifest: `experiments/manifests/EXP-036-period5-unit-event-c-spine.json`
Claim target: transverse extension of the fixed-`c` event curve into 3-D

## Hypothesis and method

The EXP-028 nontrivial-unit event continues smoothly under changes in `c` at
fixed `a=0.245`, defining a transverse spine of a two-dimensional event surface
in `(a,b,c)`.

At thirteen frozen `c` values from `4.8` through `5.4`, continue independently
upward and downward from the source at `c=5.1`. For each target, use only the
nearest previously accepted point as the seed and solve periodic closure,
phase, the nontrivial unit eigenvector, normalization, and flow orthogonality;
`b` remains free.

## Acceptance and limits

All thirteen points must solve inside `b in [0.1,0.5]`. Closure, eigen, and
flow-orthogonality residuals must be at most `1e-8`, with no adjacent `b` jump
over `0.03`.

Passing establishes one transverse event spine, not a sampled surface. It does
not show that the pitchfork-like normal form persists away from `c=5.1` or
resolve folds requiring two-parameter pseudo-arclength.
