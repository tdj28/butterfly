# EXP-456 — Fourth conservative post-sixty-point step

Status: executed; passed every prospective gate

EXP-455 passes at the defect floor, but its minimum singular value is only
`1.71x` the fixed conditioning floor. EXP-456 therefore binds the exact passed
EXP-454/455 receipts, recomputes the tangent at EXP-455, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the sixty-fourth qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-456 passes every gate in two evaluations:

```text
(a, c) = (0.17984148436973077, 10.317007838988108)
Delta a = +9.211049578072839e-7
Delta c = -2.829441342555583e-6
signed arclength = 0.004598680736429585
maximum block defect = 3.1998896362835923e-9
minimum singular value = 8.49103190623204e-10
node-boundary margin = 0.9936819172477271
```

Raw receipt: `artifacts/EXP-456/receipt.json`, 78,679 bytes,
SHA-256 `4d62843ec583949cd8a48b3cd127bb0d3b79b4e0f4c3e932540a720790148269`.
Compact receipt: [`receipts/EXP-456.json`](receipts/EXP-456.json).

Manifest:
[`../../experiments/manifests/EXP-456-jones-homoclinic-fourth-post-sixty-step.json`](../../experiments/manifests/EXP-456-jones-homoclinic-fourth-post-sixty-step.json).
