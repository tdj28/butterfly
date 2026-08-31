# EXP-460 — Third conservative post-sixty-five-point step

Status: executed; passed every prospective gate

EXP-459 passes at the defect floor, but its minimum singular value is only
`1.67x` the fixed conditioning floor. EXP-460 therefore binds the exact passed
EXP-458/459 receipts, recomputes the tangent at EXP-459, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the sixty-eighth qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-460 passes every gate in two evaluations:

```text
(a, c) = (0.17984539707576233, 10.316995819592673)
Delta a = +1.0124853656590105e-6
Delta c = -3.110298120390098e-6
signed arclength = 0.004598680736454052
maximum block defect = 3.1998583030197234e-9
minimum singular value = 8.312747684902909e-10
node-boundary margin = 0.9940480793548403
```

Raw receipt: `artifacts/EXP-460/receipt.json`, 78,621 bytes,
SHA-256 `be5e0e7662090671cae68ba269d7a8161290c42aad4c889cf1f772eb3cbd029e`.
Compact receipt: [`receipts/EXP-460.json`](receipts/EXP-460.json).

Manifest:
[`../../experiments/manifests/EXP-460-jones-homoclinic-third-post-sixty-five-step.json`](../../experiments/manifests/EXP-460-jones-homoclinic-third-post-sixty-five-step.json).
