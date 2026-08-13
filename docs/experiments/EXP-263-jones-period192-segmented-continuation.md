# EXP-263 — Segmented period-192 continuation

Status: completed — passed

EXP-261 qualifies the fourth local stability exchange and EXP-262 establishes
that both period-192 switch signs are one orbit. EXP-263 continues the exact
negative-mode representative for eight frozen pseudo-arclength steps of
nominal length `0.0025`.

All nine retained points must pass matching and half-node separation; the
terminal point must retain full/half closure, neutral, period-ratio, and exact
`224/256` section-identity gates. A pass supplies rows for a separately frozen
next-flip scan, not a period-384 child or universality claim.

Manifest:
[`../../experiments/manifests/EXP-263-jones-period192-segmented-continuation.json`](../../experiments/manifests/EXP-263-jones-period192-segmented-continuation.json).

## Result

All eight nominal `0.0025` steps pass without halving. The nine retained
points span `3.13e-8` in `a`; half-node RMS grows from `1.43e-4` to
`1.21e-3`. The terminal orbit retains exact `224/256` identity, half-period
closure `0.001032`, closure error `3.38e-7`, and preliminary multiplier
`-265.739`.

EXP-264 freezes a nine-row magnitude-separated block-Floquet scan for a
possible period-192-to-384 event.

Raw receipt: `artifacts/EXP-263/receipt.json`, 148,772 bytes, SHA-256
`80d306c1fffc7f235800613095a9b19e6c13d4e2f36ed5365a1374a2d6990606`.
Compact receipt:
[`receipts/EXP-263.json`](receipts/EXP-263.json).
