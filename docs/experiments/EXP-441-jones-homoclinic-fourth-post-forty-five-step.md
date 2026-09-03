# EXP-441 — Fourth conservative post-forty-five-point step

Status: executed; passed every prospective gate

EXP-440 passes at the defect floor, but its minimum singular value is only
`1.89x` the fixed conditioning floor. EXP-441 therefore binds the exact passed
EXP-439/440 receipts, recomputes the tangent at EXP-440, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the forty-ninth qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-441 passes every gate in two evaluations:

```text
(a, c) = (0.17982996665568382, 10.317043216177796)
Delta a = +6.023595547910432e-7
Delta c = -1.850042950835018e-6
signed arclength = 0.004598680736477784
maximum block defect = 3.1999854427032864e-9
minimum singular value = 9.401110719656303e-10
node-boundary margin = 0.9922942490653952
```

Raw receipt: `artifacts/EXP-441/receipt.json`, 78,614 bytes,
SHA-256 `0084768ce0ac2f66a909f61fe66645be1c0aa478d002bad434f3c0a787b96cbc`.
Compact receipt: [`receipts/EXP-441.json`](receipts/EXP-441.json).

Manifest:
[`../../experiments/manifests/EXP-441-jones-homoclinic-fourth-post-forty-five-step.json`](../../experiments/manifests/EXP-441-jones-homoclinic-fourth-post-forty-five-step.json).
