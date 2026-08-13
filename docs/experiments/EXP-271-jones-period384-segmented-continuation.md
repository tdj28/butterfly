# EXP-271 — Segmented period-384 continuation

Status: completed — passed

EXP-269 qualifies the fifth local stability exchange and EXP-270 establishes
that both period-384 switch signs are one orbit. EXP-271 continues the exact
negative-mode representative for eight frozen pseudo-arclength steps of
nominal length `0.00125`.

All nine retained points must pass matching and half-node separation; the
terminal point must retain full/half closure, neutral, period-ratio, and exact
`448/512` section-identity gates. A pass supplies rows for a separately frozen
next-flip scan, not a period-768 child or universality claim.

Manifest:
[`../../experiments/manifests/EXP-271-jones-period384-segmented-continuation.json`](../../experiments/manifests/EXP-271-jones-period384-segmented-continuation.json).

## Result

All eight nominal `0.00125` steps pass without halving. The nine retained
points span `8.55e-9` in `a`; half-node RMS grows from `4.73e-5` to
`4.23e-4`. The terminal orbit retains exact `448/512` identity, half-period
closure `5.04e-4`, closure error `5.54e-7`, and preliminary multiplier
`-533.597`.

EXP-272 freezes a nine-row magnitude-separated block-Floquet scan for a
possible period-384-to-768 event.

Raw receipt: `artifacts/EXP-271/receipt.json`, 290,095 bytes, SHA-256
`3f351eb00322c6f3284dfdcaf3e1a1d023abdad51939c854a319647adbeefc0a`.
Compact receipt:
[`receipts/EXP-271.json`](receipts/EXP-271.json).
