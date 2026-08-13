# EXP-243 — Magnitude-separated period-24 Floquet reclassification

Status: completed — passed

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

## Result

All gates pass. The minimum selected/collapsed modulus ratio is
`5.80e17`, far above the frozen `1e8` requirement. Exactly one real-`-1`
bracket remains, between indices 1 and 2:
`a in [0.24070104185451183, 0.24070114273020712]`, with endpoint multipliers
`-1.0665946990` and `+0.4502522448`.

EXP-244 freezes the exact 32-segment augmented event solve inside this bracket.

Raw receipt: `artifacts/EXP-243/receipt.json`, 7,079 bytes, SHA-256
`9cb35ac8d303dd9a65b29c5e4b22eba8dd1017f0d43fefb1a1604940c6396cf1`.
Compact receipt:
[`receipts/EXP-243.json`](receipts/EXP-243.json).
