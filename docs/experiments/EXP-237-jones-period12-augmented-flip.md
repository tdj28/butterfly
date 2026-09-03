# EXP-237 — Segmented augmented period-12 flip

Status: completed — passed

EXP-236's full-period corrector converges to the period-12 parent traversed
twice. EXP-237 changes representation rather than thresholds. It samples the
qualified EXP-232 period-12 orbit into 16 shooting segments and solves the
orbit plus its anti-periodic tangent field as one exact augmented system at
fixed `b=0.2` and `c=7.625815600403827`, with `a` as the event parameter.

The frozen gates require small orbit, phase, tangent, and normalization
residuals; agreement with the EXP-232 event; independent Radau closure and
real-`-1` multiplier; primitive `14/16` section identity; and nonclosure at
every proper subperiod. A pass supplies event nodes and the tangent mode for a
separately frozen segmented period-24 switch. It does not itself establish a
period-24 child or its stability.

Manifest:
[`../../experiments/manifests/EXP-237-jones-period12-augmented-flip.json`](../../experiments/manifests/EXP-237-jones-period12-augmented-flip.json).

## Result

All gates pass after two augmented corrections. The corrected event is
`a=0.24070118147582764`, only `2.33e-15` from the EXP-232 seed. Orbit and
anti-periodic tangent residuals are `3.83e-14` and `8.04e-15`; the direct
multiplier is `-0.9999999975`, while independent Radau gives
`-1.0000002741`. The orbit retains `14/16` section identity and a minimum
proper-subperiod closure of `0.0436954`.

Raw receipt: `artifacts/EXP-237/receipt.json`, 7,387 bytes, SHA-256
`088258b0c0cca6f5cb847ced26ff44dff00a6c67bdd50858d4f504e45f4e2cba`.
Compact receipt:
[`receipts/EXP-237.json`](receipts/EXP-237.json).
