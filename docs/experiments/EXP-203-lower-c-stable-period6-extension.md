# EXP-203 — Lower-c stable period-6 extension

Status: prospectively frozen before orbit correction

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
