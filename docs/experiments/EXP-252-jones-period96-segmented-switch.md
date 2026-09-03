# EXP-252 — Segmented period-96 child switch

Status: completed — passed candidate nomination

EXP-252 doubles the 64 nodes of the EXP-250 period-48 event only under the
passing, hash-bound EXP-251 residual-safe audit. It opens the child along the
qualified anti-periodic tangent at three frozen predictor lengths and both
signs, with `a` free and `(b,c)=(0.2,7.625815600403827)` fixed.

Candidates must pass matching, phase, direct closure, neutral, period-ratio,
parameter-displacement, half-period nonclosure, half-node separation, and
exact `112/128` section-identity gates. Any survivor is only a nomination for
independent solver, sign-equivalence, stability-exchange, attraction, and
branch qualification.

Manifest:
[`../../experiments/manifests/EXP-252-jones-period96-segmented-switch.json`](../../experiments/manifests/EXP-252-jones-period96-segmented-switch.json).

## Result

All six corrections pass. At predictor length `0.002`, both tangent signs
produce exact `112/128` candidates at
`a=0.240701016004533/0.240701015999747`, with matching residuals below
`1.7e-13`, half-period closures `5.09e-5/5.12e-5`, and preliminary dominant
moduli `0.89392/0.89253`. The event residual and secondary-null residual are
`3.05e-10` and `2.94e-12`.

These are period-96 nominations, not yet a stability-exchange claim. EXP-253
freezes independent DOP853/Radau qualification of one near-event child and its
period-48 parent.

Raw receipt: `artifacts/EXP-252/receipt.json`, 107,193 bytes, SHA-256
`5cfed28b20ba1050486804ed39b4d09ebc2041baf9c81c710112e78d12f45a68`.
Compact receipt:
[`receipts/EXP-252.json`](receipts/EXP-252.json).
