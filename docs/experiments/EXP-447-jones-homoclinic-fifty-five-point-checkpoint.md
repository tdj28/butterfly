# EXP-447 — Fifty-five-point homoclinic checkpoint attempt

Status: executed; passed every prospective gate

EXP-446 passes at the defect floor, but its minimum singular value is only
`1.81x` the fixed conditioning floor. EXP-447 therefore binds the exact passed
EXP-445/446 receipts, recomputes the tangent at EXP-446, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the fifty-fifth qualified point and triggers a receipt-bound figure
and manuscript refresh. A failure is preserved. Neither outcome establishes
global nonintersection, uniqueness, proof, or topology.

## Result

EXP-447 passes every gate in two evaluations:

```text
(a, c) = (0.1798339982049874, 10.317030833792156)
Delta a = +7.231052072953492e-7
Delta c = -2.2209764658498443e-6
signed arclength = 0.004598680736436541
maximum block defect = 3.1999507416356106e-9
minimum singular value = 9.000945034453671e-10
node-boundary margin = 0.9927636535572404
```

Raw receipt: `artifacts/EXP-447/receipt.json`, 78,727 bytes,
SHA-256 `132f1c4ef43d40a67a85a2cadcd27e1990a690e78b715c6e9328098113e2be9d`.
Compact receipt: [`receipts/EXP-447.json`](receipts/EXP-447.json).

Manifest:
[`../../experiments/manifests/EXP-447-jones-homoclinic-fifty-five-point-checkpoint.json`](../../experiments/manifests/EXP-447-jones-homoclinic-fifty-five-point-checkpoint.json).
