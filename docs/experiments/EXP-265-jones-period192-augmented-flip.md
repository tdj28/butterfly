# EXP-265 — Exact augmented period-192 flip

Status: completed — failed one derived multiplier gate

EXP-264 supplies one magnitude-separated real-`-1` bracket on the exact
period-192 branch. EXP-265 phase-aligns and interpolates both bracket endpoint
node fields, then solves the coupled 256-segment orbit, free `a`, normalized
anti-periodic tangent equations.

The independent Radau check uses the identical segmented augmented equations
and four cyclic block-Floquet products. A maximum-evaluation optimizer stop is
accepted only if every unchanged DOP853 science residual passes. Orbit, phase,
tangent, normalization, real-`-1`, cyclic, every proper-subperiod, and exact
`224/256` identity gates remain mandatory.

A pass qualifies a fifth exact returning-arm event and tangent mode for a
separately gated period-384 switch. It does not establish that child or a
limiting scaling law.

Manifest:
[`../../experiments/manifests/EXP-265-jones-period192-augmented-flip.json`](../../experiments/manifests/EXP-265-jones-period192-augmented-flip.json).

## Result

The 1,538-variable solve converges in four evaluations to
`a=0.24070100863058516`, period `1430.966612912069`. Its DOP853 orbit/tangent
residuals are `9.14e-11/4.18e-12`; segmented Radau independently gives
`9.42e-11/2.58e-11`. Every gate passes except the reference direct-product
flip residual: `1.06496e-7` versus the frozen `1e-7` limit. Radau gives
`-2.26706e-7` against its separately frozen `1e-4` gate. Proper-subperiod
closure (`5.97e-5` minimum), cyclic spreads, and exact `224/256` identity pass.

No event is promoted from this receipt. EXP-266 freezes an unchanged-solution,
tighter-step DOP853/Radau representation audit with the same `1e-7` flip
threshold and a new `1e-7` cross-solver agreement gate.

Raw receipt: `artifacts/EXP-265/receipt.json`, 56,897 bytes, SHA-256
`5d305bf240dbf84c6d1dd8558f8208ef813a8b9d4543572da604d321a30ee7ce`.
