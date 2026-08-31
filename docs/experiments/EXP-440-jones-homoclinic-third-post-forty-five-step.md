# EXP-440 — Third conservative post-forty-five-point step

Status: executed; passed every prospective gate

EXP-439 remains at the defect floor and its minimum singular value is only
`1.91x` the fixed conditioning floor. EXP-440 therefore binds the exact passed
EXP-438/439 receipts, recomputes the tangent at EXP-439, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the forty-eighth qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-440 passes every gate in two evaluations:

```text
(a, c) = (0.17982936429612903, 10.317045066220746)
Delta a = +5.833080391481893e-7
Delta c = -1.7915590344586008e-6
signed arclength = 0.004598680736460319
maximum block defect = 3.199990872959372e-9
minimum singular value = 9.471110406817533e-10
node-boundary margin = 0.992225785762578
```

Raw receipt: `artifacts/EXP-440/receipt.json`, 78,655 bytes,
SHA-256 `7889ff252dd9e4b088984e88a53f9d628d844b87960b9c294dd4362226930c5b`.
Compact receipt: [`receipts/EXP-440.json`](receipts/EXP-440.json).

Manifest:
[`../../experiments/manifests/EXP-440-jones-homoclinic-third-post-forty-five-step.json`](../../experiments/manifests/EXP-440-jones-homoclinic-third-post-forty-five-step.json).
