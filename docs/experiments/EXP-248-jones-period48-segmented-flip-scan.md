# EXP-248 — Period-48 Floquet scan toward period 96

Status: completed — passed

EXP-246 qualifies the near-event period-48 child as stable, while EXP-247's
terminal diagnostic is strongly unstable. EXP-248 computes block-Floquet
spectra at all nine exact child rows and selects the larger-modulus transverse
mode only when it remains at least `1e8` above the collapsed mode.

The frozen pass requires every row, prior matching residuals, an initially
stable multiplier, a terminal multiplier below `-2`, negligible imaginary
parts, the separation gate, and at least one real-`-1` bracket. A pass is only
a bracket nomination for an exact period-48 augmented solve.

Manifest:
[`../../experiments/manifests/EXP-248-jones-period48-segmented-flip-scan.json`](../../experiments/manifests/EXP-248-jones-period48-segmented-flip-scan.json).

## Result

All gates pass. The selected real multiplier progresses from `+0.987258` to
`-29.2370`, while the minimum selected/collapsed modulus ratio is
`5.87e18`. Exactly one real-`-1` bracket remains between indices 2 and 3:
`a in [0.2407009996983363, 0.2407010233056503]`, with endpoint multipliers
`-2.256540` and `-0.507037`.

EXP-249 freezes the exact 64-segment augmented event solve inside this bracket.

Raw receipt: `artifacts/EXP-248/receipt.json`, 21,953 bytes, SHA-256
`e4cf0f01ee2ad83b5db92b4e55b15f29572e25f83c59415bf929c42a5226fff9`.
Compact receipt:
[`receipts/EXP-248.json`](receipts/EXP-248.json).
