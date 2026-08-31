# EXP-465 — Third conservative post-seventy-point step

Status: executed; passed every prospective gate

EXP-464 passes at the defect floor, but its minimum singular value is only
`1.63x` the fixed conditioning floor. EXP-465 therefore binds the exact passed
EXP-463/464 receipts, recomputes the tangent at EXP-464, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the seventy-third qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-465 passes every gate in two evaluations:

```text
(a, c) = (0.17985080034031897, 10.316979220484905)
Delta a = +1.125698103066064e-6
Delta c = -3.4582746426536914e-6
signed arclength = 0.004598680736445145
maximum block defect = 3.199815479652537e-9
minimum singular value = 8.142900472327874e-10
node-boundary margin = 0.9939359652953712
```

Raw receipt: `artifacts/EXP-465/receipt.json`, 78,624 bytes,
SHA-256 `364d350747539d5bbb9abc0369eced5b097863a7f3322e70eee543ffbb1aae89`.
Compact receipt: [`receipts/EXP-465.json`](receipts/EXP-465.json).

Manifest:
[`../../experiments/manifests/EXP-465-jones-homoclinic-third-post-seventy-step.json`](../../experiments/manifests/EXP-465-jones-homoclinic-third-post-seventy-step.json).
