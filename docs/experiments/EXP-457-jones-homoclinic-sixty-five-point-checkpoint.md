# EXP-457 — Sixty-five-point homoclinic checkpoint attempt

Status: executed; passed every prospective gate

EXP-456 passes at the defect floor, but its minimum singular value is only
`1.70x` the fixed conditioning floor. EXP-457 therefore binds the exact passed
EXP-455/456 receipts, recomputes the tangent at EXP-456, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the sixty-fifth qualified point and triggers a receipt-bound figure
and manuscript refresh. A failure is preserved. Neither outcome establishes
global nonintersection, uniqueness, proof, or topology.

## Result

EXP-457 passes every gate in two evaluations:

```text
(a, c) = (0.1798424282550444, 10.31700493953329)
Delta a = +9.438853136312098e-7
Delta c = -2.8994548184613222e-6
signed arclength = 0.004598680736418389
maximum block defect = 3.1998820460207597e-9
minimum singular value = 8.443243294685767e-10
node-boundary margin = 0.9938010779404465
```

Raw receipt: `artifacts/EXP-457/receipt.json`, 78,717 bytes,
SHA-256 `d620c4024ea370d9657f580251566f2613b4a1881cdb19dedf9f0a67e0028f0f`.
Compact receipt: [`receipts/EXP-457.json`](receipts/EXP-457.json).

Manifest:
[`../../experiments/manifests/EXP-457-jones-homoclinic-sixty-five-point-checkpoint.json`](../../experiments/manifests/EXP-457-jones-homoclinic-sixty-five-point-checkpoint.json).
