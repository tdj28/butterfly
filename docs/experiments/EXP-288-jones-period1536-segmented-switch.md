# EXP-288 — Segmented period-1536 switch

Status: completed — passed

EXP-287 independently qualifies the period-768 event represented by EXP-281.
EXP-288 doubles its 1,024 event nodes and switches along both signs of the exact
anti-periodic tangent using 2,048 shooting segments. The three predictor
lengths (`0.0000625`, `0.000125`, and `0.00025`) and every acceptance gate are
frozen before execution.

The correction uses the same analytic multiple-shooting Jacobian as earlier
rungs, stored as CSR rather than a dense 6,146-column matrix. This is a scaling
change, not a mathematical-method change. A dense-versus-sparse regression
test must pass before launch.

Matching, phase, full/half closure, neutral mode, half-node separation,
parameter displacement, period ratio, and exact `1792/2048` section identity
are mandatory. At least two bilateral candidates must pass. A pass only
nominates primitive period-1536 candidates; independent stability exchange and
criticality remain separate.

Manifest:
[`../../experiments/manifests/EXP-288-jones-period1536-segmented-switch.json`](../../experiments/manifests/EXP-288-jones-period1536-segmented-switch.json).

## Result

All six bilateral candidates pass. Each correction terminates in two function
evaluations with matching residual below `1.21e-10`; the event matching and
secondary-null residuals are `1.38e-10/1.84e-12`. All candidates retain exact
`1792/2048` identity and period ratio two to `8.86e-14`.

At the largest predictor, the negative/positive candidates share
`a=0.24070100817350334`; their half-period closures are
`2.89e-6/4.42e-6`, and their half-node RMS values are both `6.31e-6`. The
positive candidate has the best direct closure and neutral residual of that
pair (`5.32e-7/3.26e-5`) and the largest half-period separation, so it is
prospectively selected for independent criticality adjudication in EXP-289.
Its preliminary modulus `0.686` is not promoted because the six long-product
estimates are representation-conditioned.

This nominates a primitive period-1536 child. It does not yet establish that
the child is stable, that the parent/child exchange is supercritical or
subcritical, or that the two tangent signs are one phase-shifted orbit.

Raw receipt: `artifacts/EXP-288/receipt.json`, 1,520,816 bytes, SHA-256
`d06fe7cb53d69d7b4692d14c8947f7db6ebd9ed6952b610eb2817b95c6cf4de0`.
Compact receipt:
[`receipts/EXP-288.json`](receipts/EXP-288.json).
