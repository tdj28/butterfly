# EXP-272 — Segmented period-384 flip scan

Status: completed — passed

EXP-272 computes block-Floquet spectra at every exact EXP-271 row. It selects
the larger-modulus transverse eigenvalue only while it remains at least eight
orders of magnitude separated from the collapsed mode, preventing a
nearest-neighbor tracker swap.

A pass requires all nine rows, a real multiplier, a stable first row, a
strongly unstable last row, and at least one real-`-1` bracket. A pass only
nominates a bracket for a separately frozen exact 512-segment augmented solve.

Manifest:
[`../../experiments/manifests/EXP-272-jones-period384-segmented-flip-scan.json`](../../experiments/manifests/EXP-272-jones-period384-segmented-flip-scan.json).

## Result

All nine rows pass. Exactly one real-`-1` bracket is isolated between
`a=0.24070100850046297` (multiplier `0.3911758`) and
`a=0.24070100810074033` (multiplier `-2.5500985`). The minimum transverse-mode
modulus separation is `1.908e18`; maximum four-shift cyclic-product spread is
`4.99e-9`.

EXP-273 freezes the bracket-bound exact 512-segment augmented solve. No sixth
event is claimed from interpolation alone.

Raw receipt: `artifacts/EXP-272/receipt.json`, 22,217 bytes, SHA-256
`43fbf99939a8f1b6bdc60a5b42405e96fa30b7481b278ccb507e6fa4da8c7a06`.
Compact receipt:
[`receipts/EXP-272.json`](receipts/EXP-272.json).
