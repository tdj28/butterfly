# EXP-257 — Segmented period-96 continuation

Status: completed — passed

EXP-256 establishes that both switch signs are one stable primitive period-96
orbit. EXP-257 continues the exact negative-mode representative for eight
frozen pseudo-arclength steps of nominal length `0.005`. The failed-status
EXP-250 parent event is usable only under its hash-bound passing EXP-251 audit.

All nine retained points must pass matching and half-node separation; the
terminal point must retain full/half closure, neutral, period-ratio, and exact
`112/128` section-identity gates. A pass supplies rows for a separately frozen
next-flip scan, not a period-192 or universality claim.

Manifest:
[`../../experiments/manifests/EXP-257-jones-period96-segmented-continuation.json`](../../experiments/manifests/EXP-257-jones-period96-segmented-continuation.json).

## Result

All eight nominal `0.005` steps pass without halving. The nine retained points
span `1.17e-7` in `a`; half-node RMS grows from `0.000203` to `0.003462`.
The terminal orbit retains exact `112/128` identity, half-period closure
`0.001677`, closure error `1.10e-7`, and preliminary multiplier `-148.708`.

EXP-258 freezes a nine-row magnitude-separated block-Floquet scan for a
possible period-96-to-192 event.

Raw receipt: `artifacts/EXP-257/receipt.json`, 78,221 bytes, SHA-256
`5356c719ff84a1ff91c00eb1ca000eaeca2635ea2965a70eeb01fcbed1a7eb6b`.
Compact receipt:
[`receipts/EXP-257.json`](receipts/EXP-257.json).
