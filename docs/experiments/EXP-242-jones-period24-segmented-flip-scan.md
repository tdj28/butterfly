# EXP-242 — Period-24 Floquet scan toward the next flip

Status: frozen — not yet executed

EXP-241 qualifies the near-event child as stable, while EXP-240 qualifies the
EXP-239 terminal child as strongly unstable. EXP-242 computes block-Floquet
spectra at all 21 already-corrected segmented rows and tracks the initially
dominant real multiplier by nearest-neighbor eigenvalue identity.

The frozen pass requires every row, the prior matching residuals, an initially
stable multiplier, a terminal real multiplier below `-2`, and at least one
real-`-1` bracket. A pass nominates an exact period-24-to-48 augmented event
solve; it does not itself establish that event or a period-48 child.

Manifest:
[`../../experiments/manifests/EXP-242-jones-period24-segmented-flip-scan.json`](../../experiments/manifests/EXP-242-jones-period24-segmented-flip-scan.json).
