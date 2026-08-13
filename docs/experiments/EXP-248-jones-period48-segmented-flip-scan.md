# EXP-248 — Period-48 Floquet scan toward period 96

Status: frozen — not yet executed

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
