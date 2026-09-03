# EXP-454 — Second conservative post-sixty-point step

Status: executed; passed every prospective gate

EXP-453 passes at the defect floor, but its minimum singular value is only
`1.73x` the fixed conditioning floor. EXP-454 therefore binds the exact passed
EXP-452/453 receipts, recomputes the tangent at EXP-453, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the sixty-second qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-454 passes every gate in two evaluations:

```text
(a, c) = (0.17983966484786867, 10.317013428142225)
Delta a = +8.758487091697909e-7
Delta c = -2.6903541705536327e-6
signed arclength = 0.004598680736419083
maximum block defect = 3.199904283147336e-9
minimum singular value = 8.592526726741141e-10
node-boundary margin = 0.9934540268096015
```

Raw receipt: `artifacts/EXP-454/receipt.json`, 78,648 bytes,
SHA-256 `e75ac2c5ed9da8cb85439164bd1f31326caf958cb13f91169ad5d601c24f1921`.
Compact receipt: [`receipts/EXP-454.json`](receipts/EXP-454.json).

Manifest:
[`../../experiments/manifests/EXP-454-jones-homoclinic-second-post-sixty-step.json`](../../experiments/manifests/EXP-454-jones-homoclinic-second-post-sixty-step.json).
