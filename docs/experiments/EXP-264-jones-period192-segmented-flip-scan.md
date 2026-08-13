# EXP-264 — Segmented period-192 flip scan

Status: completed — passed

EXP-264 computes block-Floquet spectra at every exact EXP-263 row. It selects
the larger-modulus transverse eigenvalue only when it remains at least eight
orders of magnitude separated from the collapsed mode, preventing the
nearest-neighbor tracker swap previously exposed by EXP-242.

A pass requires all nine rows, a real multiplier, a stable first row, a
strongly unstable last row, and at least one real-`-1` bracket. A pass only
nominates a bracket for a separately frozen exact augmented solve.

Manifest:
[`../../experiments/manifests/EXP-264-jones-period192-segmented-flip-scan.json`](../../experiments/manifests/EXP-264-jones-period192-segmented-flip-scan.json).

## Result

All nine rows pass. Exactly one real-`-1` bracket is isolated between
`a=0.24070100957644772` (multiplier `0.4611781`) and
`a=0.24070100795063762` (multiplier `-2.0511880`). The minimum transverse-mode
modulus separation is `1.146e18`; maximum four-shift cyclic-product spread is
`1.41e-9`.

EXP-265 freezes the bracket-bound exact 256-segment augmented solve. No fifth
event is claimed from interpolation alone.

Raw receipt: `artifacts/EXP-264/receipt.json`, 22,242 bytes, SHA-256
`101337e5c93d799bd24aecd2f4f16efb272738e86da6e62ec130b181fedee23c`.
Compact receipt:
[`receipts/EXP-264.json`](receipts/EXP-264.json).
