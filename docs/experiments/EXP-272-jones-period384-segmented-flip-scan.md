# EXP-272 — Segmented period-384 flip scan

Status: frozen — not yet executed

EXP-272 computes block-Floquet spectra at every exact EXP-271 row. It selects
the larger-modulus transverse eigenvalue only while it remains at least eight
orders of magnitude separated from the collapsed mode, preventing a
nearest-neighbor tracker swap.

A pass requires all nine rows, a real multiplier, a stable first row, a
strongly unstable last row, and at least one real-`-1` bracket. A pass only
nominates a bracket for a separately frozen exact 512-segment augmented solve.

Manifest:
[`../../experiments/manifests/EXP-272-jones-period384-segmented-flip-scan.json`](../../experiments/manifests/EXP-272-jones-period384-segmented-flip-scan.json).
