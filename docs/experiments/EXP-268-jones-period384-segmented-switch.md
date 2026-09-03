# EXP-268 — Segmented period-384 switch

Status: completed — passed

EXP-268 doubles EXP-267's exact 256-node period-192 event representation and
switches along both signs of its qualified anti-periodic tangent using 512
shooting segments. Three predictor lengths (`0.00025`, `0.0005`, `0.001`) are
frozen before execution.

Matching, phase, full/half closure, neutral, half-node separation, parameter
displacement, period ratio, and exact `448/512` section identity are mandatory.
At least two candidates must pass. A pass only nominates period-384 orbits for
independent stability and sign-equivalence tests.

Manifest:
[`../../experiments/manifests/EXP-268-jones-period384-segmented-switch.json`](../../experiments/manifests/EXP-268-jones-period384-segmented-switch.json).

## Result

All six bilateral candidates pass. At step `0.001`, the negative/positive
candidates lie at `a=0.24070100850046297/0.24070100850674792`, retain
half-period closures `5.63374e-5/5.44780e-5`, and have preliminary stable
moduli `0.390986/0.432548`. All candidates retain exact `448/512` identity;
matching residuals are below `3.43e-13`.

This nominates primitive stable-looking period-384 solutions on both tangent
signs. EXP-269 freezes the independent parent-unstable/child-stable test; no
sixth supercritical rung is claimed before that test passes.

Raw receipt: `artifacts/EXP-268/receipt.json`, 389,758 bytes, SHA-256
`f361d0d23327ef8b66e17312fbeea0b6b90781220889e459127ac8825379f064`.
Compact receipt:
[`receipts/EXP-268.json`](receipts/EXP-268.json).
