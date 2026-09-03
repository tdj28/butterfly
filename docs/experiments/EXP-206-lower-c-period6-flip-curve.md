# EXP-206 — Lower-c period-6 flip-curve continuation

Status: completed; all 41 coupled continuation points passed

## Question

Do EXP-205's seven scalar roots belong to one densely sampled, identity-safe
real-minus-one Floquet curve at fixed `b=0.2`?

## Frozen design

The source is EXP-205 event `flip-c7244`. The anti-periodic tangent, periodic
orbit, phase, normalization, and free `a` are solved together with the exact
Rössler first- and second-variational Jacobian. Forty-one fixed-`c` targets
cover `c in [7.16,7.32]` at spacing `0.004`, extending `0.032` beyond the
EXP-205 slice range on both sides. Upward and downward continuation use only
the immediately preceding accepted point.

Every target must solve inside `a in [0.21555,0.2159]`, preserve real-minus-one
and neutral Floquet residuals, retain exactly six historical and eight Barrio
section phases, and keep adjacent `a` motion below `1e-5`.

Manifest:
[`../../experiments/manifests/EXP-206-lower-c-period6-flip-curve.json`](../../experiments/manifests/EXP-206-lower-c-period6-flip-curve.json).

## Claim boundary

A pass establishes a dense sampled segment of one orbit-defined flip curve.
It does not prove global curve connectivity, locate its folds or endpoints,
qualify a period-12 child or supercriticality, identify the TBA curve, or
establish double-critical membership.

## Result

Both directions complete and all 41 points pass. The curve spans
`c in [7.16,7.32]` and `a in [0.2156835308258212,0.2158160512164691]`, with
maximum adjacent `a` motion `4.64e-6`. Maximum orbit, tangent, independent
flip-multiplier, and neutral-multiplier residuals are respectively `1.10e-11`,
`1.71e-12`, `2.05e-9`, and `1.82e-9`. Every event retains six historical and
eight Barrio section phases.

This establishes a dense sampled real-minus-one period-6 curve segment and
promotes it to the parent input for a separately frozen period-12 branch
switch. It does not identify this curve with the TBA curve.

Raw receipt: `artifacts/EXP-206/receipt.json`, 37,724 bytes, SHA-256
`e0ced2227c7074ea5eec55ff191159d80bc43216b8f2d5826c1cfe645f3708ba`.
Compact receipt: [`receipts/EXP-206.json`](receipts/EXP-206.json).
