# EXP-464 — Second conservative post-seventy-point step

Status: executed; passed every prospective gate

EXP-463 passes at the defect floor, but its minimum singular value is only
`1.64x` the fixed conditioning floor. EXP-464 therefore binds the exact passed
EXP-462/463 receipts, recomputes the tangent at EXP-463, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the seventy-second qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-464 passes every gate in two evaluations:

```text
(a, c) = (0.1798496746422159, 10.316982678759548)
Delta a = +1.1033317356134997e-6
Delta c = -3.3895288087393283e-6
signed arclength = 0.004598680736428014
maximum block defect = 3.1998242716381766e-9
minimum singular value = 8.171760745937059e-10
node-boundary margin = 0.9939548286210744
```

Raw receipt: `artifacts/EXP-464/receipt.json`, 78,650 bytes,
SHA-256 `6d44a40c953412b9ace0aa11388531eb93127b50a8188a62cc275ebcdd94329e`.
Compact receipt: [`receipts/EXP-464.json`](receipts/EXP-464.json).

Manifest:
[`../../experiments/manifests/EXP-464-jones-homoclinic-second-post-seventy-step.json`](../../experiments/manifests/EXP-464-jones-homoclinic-second-post-seventy-step.json).
