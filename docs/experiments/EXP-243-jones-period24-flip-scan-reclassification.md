# EXP-243 — Magnitude-separated period-24 Floquet reclassification

Status: frozen — not yet executed

EXP-242's nearest-neighbor tracker follows the wrong transverse eigenvalue
after index 1. EXP-243 reads only the immutable EXP-242 spectra and selects the
larger-modulus non-neutral eigenvalue at every row. This is admissible only if
the selected and collapsed transverse moduli differ by at least eight orders
of magnitude everywhere.

The frozen pass additionally requires all 21 rows, one and only one real-`-1`
bracket, an initially stable value, a terminal value below `-2`, and negligible
imaginary parts. No orbit or spectrum is recomputed.

Manifest:
[`../../experiments/manifests/EXP-243-jones-period24-flip-scan-reclassification.json`](../../experiments/manifests/EXP-243-jones-period24-flip-scan-reclassification.json).
