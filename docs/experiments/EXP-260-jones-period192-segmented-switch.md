# EXP-260 — Segmented period-192 child switch

Status: completed — passed candidate nomination

EXP-259 supplies the exact 128-segment period-96 event and anti-periodic
tangent. EXP-260 doubles it to 256 nodes and opens the child at three frozen
predictor lengths on both tangent signs, with `a` free and
`(b,c)=(0.2,7.625815600403827)` fixed.

Candidates must pass matching, phase, direct closure, neutral, period-ratio,
parameter-displacement, half-period nonclosure, half-node separation, and
exact `224/256` section-identity gates. Survivors are nominations requiring a
separate DOP853/Radau stability-exchange audit; this experiment alone cannot
promote a fourth supercritical rung.

Manifest:
[`../../experiments/manifests/EXP-260-jones-period192-segmented-switch.json`](../../experiments/manifests/EXP-260-jones-period192-segmented-switch.json).

## Result

All six corrections pass. At predictor length `0.002`, both tangent signs
produce exact `224/256` candidates at
`a=0.240701009576448/0.240701009618815`, with matching residuals below
`2.45e-13`, half-period closures `1.067e-4/1.008e-4`, and preliminary stable
moduli `0.4612/0.5206`. The doubled event residual and secondary-null residual
are `6.44e-10` and `2.21e-12`.

EXP-261 freezes independent DOP853/Radau qualification of the negative-mode
near-event child and its period-96 parent. The fourth supercritical rung is not
promoted until that test passes.

Raw receipt: `artifacts/EXP-260/receipt.json`, 201,272 bytes, SHA-256
`e91ec562d7977946c5737cdb73583d9e4c079806374724ebd54a16bdb97f1200`.
Compact receipt:
[`receipts/EXP-260.json`](receipts/EXP-260.json).
