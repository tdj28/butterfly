# EXP-242 — Period-24 Floquet scan toward the next flip

Status: completed — failed eigenvalue-identity rule

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

## Result

All 21 spectra and prior orbit-residual gates pass, but the preregistered
nearest-neighbor tracker swaps branches after index 1. It follows the collapsed
transverse multiplier near `1e-18` instead of the nontrivial branch that moves
from `+0.450252` at index 1 to `-1.066595` at index 2 and then to
`-703.436354` at index 20. The experiment therefore fails with zero reported
brackets.

The raw spectra make the administrative cause auditable: at every row the two
transverse moduli are widely separated. EXP-243 freezes a reclassification of
the immutable spectra using that separation and requires a minimum ratio of
`1e8`; no integration or numerical result is changed.

Raw receipt: `artifacts/EXP-242/receipt.json`, 47,714 bytes, SHA-256
`f86482271775b9f0ba2af25312c1522845b80bfaabd63ee25f3b52c44d88ad9c`.
Compact receipt:
[`receipts/EXP-242.json`](receipts/EXP-242.json).
