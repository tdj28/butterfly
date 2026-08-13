# EXP-259 — Exact augmented period-96 flip

Status: completed — passed

EXP-258 supplies one magnitude-separated real-`-1` bracket on the exact
period-96 branch. EXP-259 phase-aligns and interpolates both bracket endpoint
node fields, then solves the coupled 128-segment orbit, free `a`, normalized
anti-periodic tangent equations.

The independent Radau check uses the identical segmented augmented equations
and four cyclic block-Floquet products, avoiding the long-period single-shot
conditioning already exposed by EXP-250. A maximum-evaluation optimizer stop
is accepted only if every unchanged DOP853 science residual passes. Orbit,
phase, tangent, normalization, real-`-1`, cyclic, every proper-subperiod, and
exact `112/128` identity gates remain explicit.

Manifest:
[`../../experiments/manifests/EXP-259-jones-period96-augmented-flip.json`](../../experiments/manifests/EXP-259-jones-period96-augmented-flip.json).

## Result

The 770-variable solve converges in 10 evaluations to
`a=0.2407010100842176`, period `715.4833192761138`. DOP853 orbit/tangent
residuals are `4.55e-10/3.57e-11` and the flip multiplier is
`-1.00000003941`; segmented Radau independently gives residuals
`4.55e-10/4.89e-11` and multiplier `-0.99999991487`. Four-shift cyclic
spreads are below `1.88e-11`. Every proper subperiod, including half-period
closure `1.68e-4`, and exact `112/128` identity pass.

This qualifies a fourth exact returning-arm event and tangent mode. EXP-260
freezes the separately gated period-192 switch; supercriticality is not yet
claimed for this rung.

Raw receipt: `artifacts/EXP-259/receipt.json`, 32,644 bytes, SHA-256
`189d4ba3b89b93611456a68c3c0a6ea793b151ebf7bc7bedaa8bc09a655cb3be`.
Compact receipt:
[`receipts/EXP-259.json`](receipts/EXP-259.json).
