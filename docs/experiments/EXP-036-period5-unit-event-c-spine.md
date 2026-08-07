# EXP-036 — Period-5 unit-event spine across c

Status: executed; passed
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

## Result

The clean run at commit `4d243ab8668daaa3a6c3da326aa8cada6ca2020a`
passed all thirteen points and both directions. The event parameter decreases
smoothly from `b=0.31343846` at `c=4.8`, through the source, to `b=0.23832715`
at `c=5.4`. Maximum adjacent `b` jump was `0.00847`; maximum closure was
`1.69e-12`, maximum eigen residual `5.48e-13`, and maximum flow-orthogonality
residual `3.70e-17`.

The complete receipt SHA-256 is
`5ced7a162409846449bf1b51015b9a6f5b19826aac6b042b1de334ed34176ba1`.

## Decision

Accept a transverse fixed-`a=0.245` event spine over the declared `c` range.
Together with EXP-035, this establishes two intersecting curves of the same
coupled event set. It is not yet a surface measurement. EXP-037 freezes a
`5 x 5` `(a,c)` patch, using each EXP-036 point only as its slice center and
independently correcting the neighboring `a` values.
