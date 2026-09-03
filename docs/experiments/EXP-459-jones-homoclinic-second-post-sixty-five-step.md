# EXP-459 — Second conservative post-sixty-five-point step

Status: executed; passed every prospective gate

EXP-458 passes at the defect floor, but its minimum singular value is only
`1.68x` the fixed conditioning floor. EXP-459 therefore binds the exact passed
EXP-457/458 receipts, recomputes the tangent at EXP-458, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the sixty-seventh qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-459 passes every gate in two evaluations:

```text
(a, c) = (0.17984438459039667, 10.316998929890794)
Delta a = +9.896061231584596e-7
Delta c = -3.0399775674538887e-6
signed arclength = 0.004598680736436671
maximum block defect = 3.1998663997792753e-9
minimum singular value = 8.354017961898641e-10
node-boundary margin = 0.9940497443107361
```

Raw receipt: `artifacts/EXP-459/receipt.json`, 78,639 bytes,
SHA-256 `148e2eee39dc9585410cc4c99750512f3f6d3a0ac28ecc6d301fb5010d01ee5f`.
Compact receipt: [`receipts/EXP-459.json`](receipts/EXP-459.json).

Manifest:
[`../../experiments/manifests/EXP-459-jones-homoclinic-second-post-sixty-five-step.json`](../../experiments/manifests/EXP-459-jones-homoclinic-second-post-sixty-five-step.json).
