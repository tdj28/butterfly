# EXP-442 — Fifty-point homoclinic checkpoint attempt

Status: executed; passed every prospective gate

EXP-441 passes at the defect floor, but its minimum singular value is only
`1.88x` the fixed conditioning floor. EXP-442 therefore binds the exact passed
EXP-440/441 receipts, recomputes the tangent at EXP-441, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the fiftieth qualified point and triggers a receipt-bound figure
and manuscript refresh. A failure is preserved. Neither outcome establishes
global nonintersection, uniqueness, proof, or topology.

## Result

EXP-442 passes every gate in two evaluations:

```text
(a, c) = (0.17983058838257687, 10.317041306658568)
Delta a = +6.217268930519548e-7
Delta c = -1.9095192271834094e-6
signed arclength = 0.00459868073643685
maximum block defect = 3.199979919390989e-9
minimum singular value = 9.33194693281577e-10
node-boundary margin = 0.9923653700094661
```

Raw receipt: `artifacts/EXP-442/receipt.json`, 78,641 bytes,
SHA-256 `bc07d26e06d7fabb7cb217f417d6485553760fe97c779b07286ef4d002b874f7`.
Compact receipt: [`receipts/EXP-442.json`](receipts/EXP-442.json).

Manifest:
[`../../experiments/manifests/EXP-442-jones-homoclinic-fifty-point-checkpoint.json`](../../experiments/manifests/EXP-442-jones-homoclinic-fifty-point-checkpoint.json).
