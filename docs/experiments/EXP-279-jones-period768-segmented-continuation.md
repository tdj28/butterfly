# EXP-279 — Segmented period-768 continuation

Status: completed — passed

EXP-275 qualifies the sixth local stability exchange, and EXP-278 combines the
passed bilateral whole-orbit identities with a canonical two-solver Floquet
audit. EXP-279 continues the independently preselected negative-mode
representative for eight frozen pseudo-arclength steps of nominal length
`0.000625`.

All nine retained points must pass matching and half-node separation; the
terminal point must retain full/half closure, neutral, period-ratio, and exact
`896/1024` section-identity gates. A pass supplies rows for a separately
frozen next-flip scan, not a period-1536 child or universality claim.

Manifest:
[`../../experiments/manifests/EXP-279-jones-period768-segmented-continuation.json`](../../experiments/manifests/EXP-279-jones-period768-segmented-continuation.json).

## Result

All eight nominal `0.000625` steps pass without halving. The nine retained
points span `2.21e-9` in `a`; half-node RMS grows from `1.79e-5` to
`1.44e-4`. The terminal orbit retains exact `896/1024` identity, half-period
closure `2.88e-5`, closure error `1.93e-8`, and preliminary multiplier
`-946.310`.

EXP-280 freezes a nine-row magnitude-separated block-Floquet scan for a
possible period-768-to-1536 event.

Raw receipt: `artifacts/EXP-279/receipt.json`, 572,920 bytes, SHA-256
`b5fc6c5465eb0869542a3ce8ee716e352309df5d5dd1ee40245c0cb0540ee4cb`.
Compact receipt:
[`receipts/EXP-279.json`](receipts/EXP-279.json).
