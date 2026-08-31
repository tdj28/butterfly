# EXP-449 — Seventh conservative post-fifty-point step

Status: executed; passed every prospective gate

EXP-448 passes at the defect floor, but its minimum singular value is only
`1.79x` the fixed conditioning floor. EXP-449 therefore binds the exact passed
EXP-447/448 receipts, recomputes the tangent at EXP-448, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the fifty-seventh qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-449 passes every gate in two evaluations:

```text
(a, c) = (0.1798355080556464, 10.317026196288733)
Delta a = +7.656180462389806e-7
Delta c = -2.3516083569319335e-6
signed arclength = 0.004598680736418146
maximum block defect = 3.1999381883472427e-9
minimum singular value = 8.876797887335232e-10
node-boundary margin = 0.9929443493327099
```

Raw receipt: `artifacts/EXP-449/receipt.json`, 78,724 bytes,
SHA-256 `5e2f26c7972dd253067987f15f5a0f2fbfa17fc5e659ca068f0777f6d5d0de52`.
Compact receipt: [`receipts/EXP-449.json`](receipts/EXP-449.json).

Manifest:
[`../../experiments/manifests/EXP-449-jones-homoclinic-seventh-post-fifty-step.json`](../../experiments/manifests/EXP-449-jones-homoclinic-seventh-post-fifty-step.json).
