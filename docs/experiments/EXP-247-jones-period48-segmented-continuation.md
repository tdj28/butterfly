# EXP-247 — Segmented period-48 continuation

Status: completed — passed

EXP-246 qualifies a stable primitive period-48 child immediately beside its
birth. EXP-247 continues the exact negative-mode candidate for eight frozen
pseudo-arclength steps of nominal length `0.01` using 64 segments.

All nine retained points must pass matching and half-node separation; the
terminal point must retain full/half closure, neutral, period-ratio, and exact
`56/64` section-identity gates. A pass supplies rows for a separately frozen
next-flip scan, not a period-96 claim.

Manifest:
[`../../experiments/manifests/EXP-247-jones-period48-segmented-continuation.json`](../../experiments/manifests/EXP-247-jones-period48-segmented-continuation.json).

## Result

All eight nominal `0.01` steps pass without halving. The nine retained points
span `2.51e-7` in `a`; half-node RMS grows from `0.000219` to `0.007406`.
The terminal orbit retains `56/64` identity, half-period closure `0.016823`,
and a preliminary multiplier `-29.2370`.

EXP-248 freezes a nine-row block-Floquet scan using the magnitude-separated
mode rule validated by EXP-243.

Raw receipt: `artifacts/EXP-247/receipt.json`, 42,540 bytes, SHA-256
`18003b5b2974fcda199ad9081af67d4b1c4e61879b18be2771697dbdae022ea1`.
Compact receipt:
[`receipts/EXP-247.json`](receipts/EXP-247.json).
