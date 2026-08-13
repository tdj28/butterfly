# EXP-264 — Segmented period-192 flip scan

Status: frozen — not yet executed

EXP-264 computes block-Floquet spectra at every exact EXP-263 row. It selects
the larger-modulus transverse eigenvalue only when it remains at least eight
orders of magnitude separated from the collapsed mode, preventing the
nearest-neighbor tracker swap previously exposed by EXP-242.

A pass requires all nine rows, a real multiplier, a stable first row, a
strongly unstable last row, and at least one real-`-1` bracket. A pass only
nominates a bracket for a separately frozen exact augmented solve.

Manifest:
[`../../experiments/manifests/EXP-264-jones-period192-segmented-flip-scan.json`](../../experiments/manifests/EXP-264-jones-period192-segmented-flip-scan.json).
