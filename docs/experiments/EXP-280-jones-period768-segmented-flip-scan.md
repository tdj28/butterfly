# EXP-280 — Segmented period-768 flip scan

Status: frozen — not yet executed

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
