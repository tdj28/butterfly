# EXP-267 — Tighter coupled period-192 flip refinement

Status: completed — passed

EXP-266 shows that tighter re-evaluation of the immutable EXP-265 variables
does not satisfy the unchanged `1e-7` flip gate. EXP-267 therefore performs a
new coupled orbit, free-`a`, normalized anti-periodic-tangent correction from
those variables, within the original unique bracket.

Both solvers use maximum step `0.01`; the DOP853 corrector tolerance is
`1e-12`. Reference and independent Radau direct-product multipliers must now
both lie within `1e-7` of `-1`, alongside the existing residual, cyclic,
primitivity, and exact `224/256` identity gates. No threshold is relaxed.

A pass qualifies the fifth event only; the period-384 switch remains a
separate prospective experiment.

Manifest:
[`../../experiments/manifests/EXP-267-jones-period192-augmented-flip-refinement.json`](../../experiments/manifests/EXP-267-jones-period192-augmented-flip-refinement.json).

## Result

At the frozen 40-evaluation ceiling, every tightened science gate passes at
`a=0.24070100861338276`, period `1430.96661257828`. DOP853 orbit/tangent
residuals are `5.18e-11/1.38e-11` and its flip multiplier is
`-0.99999999330`; segmented Radau gives `5.30e-11/1.39e-11` and
`-0.99999992395`. Both multiplier residuals pass the symmetric `1e-7` gate,
and cyclic spreads remain below `3.23e-11`.

The minimum proper-subperiod closure is `5.97e-5`, and exact `224/256`
identity passes. The optimizer status is accepted only because all tightened
science residuals pass. This qualifies a fifth exact returning-arm event and
tangent mode. EXP-268 separately freezes the period-384 switch.

Raw receipt: `artifacts/EXP-267/receipt.json`, 73,663 bytes, SHA-256
`b2ae9d6ec1ecdd56de14d9c97a7a6dd56d444f6d4ace9dc1ea35a9be851243dd`.
Compact receipt:
[`receipts/EXP-267.json`](receipts/EXP-267.json).
