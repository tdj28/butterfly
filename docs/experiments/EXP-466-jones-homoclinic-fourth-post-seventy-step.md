# EXP-466 — Fourth conservative post-seventy-point step

Status: executed; passed every prospective gate

EXP-465 passes at the defect floor, but its minimum singular value is only
`1.63x` the fixed conditioning floor. EXP-466 therefore binds the exact passed
EXP-464/465 receipts, recomputes the tangent at EXP-465, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the seventy-fourth qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-466 passes every gate in two evaluations:

```text
(a, c) = (0.1798519481940373, 10.316975694112998)
Delta a = +1.1478537183251536e-6
Delta c = -3.5263719073697075e-6
signed arclength = 0.004598680736428155
maximum block defect = 3.1998065231506935e-9
minimum singular value = 8.116728259286997e-10
node-boundary margin = 0.9939190332657031
```

Raw receipt: `artifacts/EXP-466/receipt.json`, 78,696 bytes,
SHA-256 `e25c3c31ccfe9bd518659774bc3a9113d0b556ada14fd5723c3f72cd13d6279c`.
Compact receipt: [`receipts/EXP-466.json`](receipts/EXP-466.json).

Manifest:
[`../../experiments/manifests/EXP-466-jones-homoclinic-fourth-post-seventy-step.json`](../../experiments/manifests/EXP-466-jones-homoclinic-fourth-post-seventy-step.json).
