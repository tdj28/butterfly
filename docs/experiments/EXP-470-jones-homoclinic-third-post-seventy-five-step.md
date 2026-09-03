# EXP-470 — Third conservative post-seventy-five-point step

Status: executed; passed every prospective gate

EXP-469 passes at the defect floor, but its minimum singular value is only
`1.61x` the fixed conditioning floor. EXP-470 therefore binds the exact passed
EXP-468/469 receipts, recomputes the tangent at EXP-469, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the seventy-eighth qualified point. A failure is preserved.
Neither outcome establishes global nonintersection, uniqueness, proof, or
topology.

## Result

EXP-470 passes every gate in two evaluations:

```text
(a, c) = (0.17985675567226783, 10.316960924561714)
Delta a = +1.2336409821178673e-6
Delta c = -3.7900332578999496e-6
signed arclength = 0.00459868073648069
maximum block defect = 3.1997698267870753e-9
minimum singular value = 8.03989657761402e-10
node-boundary margin = 0.9938718199704422
```

Raw receipt: `artifacts/EXP-470/receipt.json`, 78,658 bytes,
SHA-256 `4e9823116d3eaa41e1783f75664912f134222dcdcbc9c0bdf69b36c98c242b66`.
Compact receipt: [`receipts/EXP-470.json`](receipts/EXP-470.json).

Manifest:
[`../../experiments/manifests/EXP-470-jones-homoclinic-third-post-seventy-five-step.json`](../../experiments/manifests/EXP-470-jones-homoclinic-third-post-seventy-five-step.json).
