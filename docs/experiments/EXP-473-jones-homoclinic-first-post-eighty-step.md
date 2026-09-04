# EXP-473 — First conservative post-eighty-point step

Status: executed; passed every prospective gate

EXP-472 passes at the defect floor, but its minimum singular value is only
`1.60x` the fixed conditioning floor. EXP-473 therefore binds the exact passed
EXP-471/472 receipts, recomputes the tangent at EXP-472, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the eighty-first qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-473 passes every gate in two evaluations:

```text
(a, c) = (0.179860578278265, 10.316949180519163)
Delta a = +1.2940497855218336e-6
Delta c = -3.9756713778871244e-6
signed arclength = 0.0045986807364583986
maximum block defect = 3.1997419033005116e-9
minimum singular value = 8.012533846968259e-10
node-boundary margin = 0.9938590494991724
```

Raw receipt: `artifacts/EXP-473/receipt.json`, 78,640 bytes,
SHA-256 `b93d2b38587dec27838d659ee6107ea702c2ec01c89f75bbfa2f6f8b61c0323b`.
Compact receipt: [`receipts/EXP-473.json`](receipts/EXP-473.json).

Manifest:
[`../../experiments/manifests/EXP-473-jones-homoclinic-first-post-eighty-step.json`](../../experiments/manifests/EXP-473-jones-homoclinic-first-post-eighty-step.json).
