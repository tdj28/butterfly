# EXP-280 — Segmented period-768 flip scan

Status: completed — passed

EXP-280 computes block-Floquet spectra at every exact EXP-279 row. It selects
the larger-modulus transverse eigenvalue only while it remains at least eight
orders of magnitude separated from the collapsed mode, preventing a
nearest-neighbor tracker swap.

A pass requires all nine rows, a real multiplier, a stable first row, a
strongly unstable last row, and at least one real-`-1` bracket. A pass only
nominates a bracket for a separately frozen exact 1,024-segment augmented
solve.

Manifest:
[`../../experiments/manifests/EXP-280-jones-period768-segmented-flip-scan.json`](../../experiments/manifests/EXP-280-jones-period768-segmented-flip-scan.json).

## Result

All nine rows pass. Exactly one real-`-1` bracket is isolated between
`a=0.24070100827074953` (multiplier `0.0836277`) and
`a=0.24070100814897039` (multiplier `-4.4092070`). The minimum transverse-mode
modulus separation is `1.875e17`; maximum four-shift cyclic-product spread is
`2.88e-8`.

EXP-281 freezes the bracket-bound exact 1,024-segment augmented solve. No
seventh event is claimed from interpolation alone.

Raw receipt: `artifacts/EXP-280/receipt.json`, 22,201 bytes, SHA-256
`882a2943be868e3f1ed0edbd0cd4c4912d88d38a09fa3985c3302a3bed6034b2`.
Compact receipt:
[`receipts/EXP-280.json`](receipts/EXP-280.json).
