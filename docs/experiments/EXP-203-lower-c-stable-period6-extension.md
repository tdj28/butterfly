# EXP-203 — Lower-c stable period-6 extension

Status: completed; seed passed but coverage failed with 551/1,000 qualified

## Question

Does the corrected stable period-6 family extend far enough below EXP-202's
sampled field to support a new, independently gated scale-ensemble residual
search?

## Frozen computation

The immutable seed is EXP-201 candidate `local-a020-c016` at
`(a,b,c)=(0.2156,0.2,7.264)`, the lowest-`c` qualified orbit with the smallest
observed second residual. A `61 x 103` grid covers `a in [0.2155,0.2161]` and
`c in [6.88,7.288]`, overlapping the qualified field by `0.024` while extending
`0.384` below the seed. Resolution remains `1e-5` by `0.004`.

Each of 6,283 points is corrected directly from the same seed using DOP853.
The EXP-198 gates are unchanged: closure, phase, correction distance, period
identity, neutral and dominant Floquet multipliers, stability, and exactly six
historical-section plus eight Barrio-section crossings. The seed must pass and
at least 1,000 points must qualify.

Manifest:
[`../../experiments/manifests/EXP-203-lower-c-stable-period6-extension.json`](../../experiments/manifests/EXP-203-lower-c-stable-period6-extension.json).

## Claim boundary

A pass establishes a new corrected stable-orbit candidate field only. Critical
points, signed residuals, and any center claim remain hidden until a separate
successor is frozen. A failure can reveal a stability or correction boundary,
but cannot be interpreted as nonexistence of an unstable continuation.

## Result

All 6,283 corrections complete without an exception. The seed passes, but only
551 candidates pass every gate, below the frozen minimum of 1,000. The
qualified field spans `a in [0.2155,0.2158]`, `c in [7.132,7.288]`, in five
eight-connected components of sizes `331,156,62,1,1`.

The 331-point seed component touches the lower-`a` boundary and spans only
`c in [7.22,7.268]`. The upper 62-point component touches the `c=7.288`
overlap boundary. Only one isolated qualified point appears below `c=7.184`.
The dominant nontrivial Floquet modulus reaches `0.99945` within the qualified
field.

First-failure attribution is 4,921 correction failures, 806 stability
failures, and five correction-distance failures. Thus the unconstrained
EXP-202 residual gradient runs into a correction/stability boundary rather
than an open stable sheet. Preserve all 551 individually qualified orbits for
a separately frozen residual replay, and continue the boundary or unstable
family before extrapolating farther.

Raw artifact: `artifacts/EXP-203/candidates.json`, 9,899,065 bytes, SHA-256
`db4c841dd678e0355ff1ed1ecfb9c8d03e630ce00e4d892f2fc237d09c2e2a02`.
Compact receipt: [`receipts/EXP-203.json`](receipts/EXP-203.json).
