# EXP-274 — Segmented period-768 switch

Status: completed — passed

EXP-274 doubles EXP-273's exact 512-node period-384 event representation and
switches along both signs of its qualified anti-periodic tangent using 1,024
shooting segments. Three predictor lengths (`0.000125`, `0.00025`, `0.0005`)
are frozen before execution.

Matching, phase, full/half closure, neutral, half-node separation, parameter
displacement, period ratio, and exact `896/1024` section identity are
mandatory. At least two candidates must pass. A pass only nominates
period-768 orbits for independent stability and sign-equivalence tests.

Manifest:
[`../../experiments/manifests/EXP-274-jones-period768-segmented-switch.json`](../../experiments/manifests/EXP-274-jones-period768-segmented-switch.json).

## Result

All six bilateral candidates pass. At step `0.0005`, the negative/positive
candidates lie at `a=0.24070100827074953/0.24070100827083100`, retain
half-period closures `6.10313e-6/6.17534e-6`, and have preliminary stable
moduli `0.081322/0.085443`. All candidates retain exact `896/1024` identity;
matching residuals are below `4.80e-13`.

This nominates primitive stable-looking period-768 solutions on both tangent
signs. EXP-275 freezes the independent parent-unstable/child-stable test; no
sixth supercritical rung is claimed before that test passes.

Raw receipt: `artifacts/EXP-274/receipt.json`, 766,640 bytes, SHA-256
`8f3cd67cbebc7dbf2b85db3b0fc666a3827b77bc03d4f97989ff64234fefc932`.
Compact receipt:
[`receipts/EXP-274.json`](receipts/EXP-274.json).
