# EXP-472 — Eighty-point homoclinic checkpoint attempt

Status: executed; passed every prospective gate

EXP-471 passes at the defect floor, but its minimum singular value is only
`1.61x` the fixed conditioning floor. EXP-472 therefore binds the exact passed
EXP-470/471 receipts, recomputes the tangent at EXP-471, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the eightieth qualified point and triggers a receipt-bound figure
and manuscript refresh. A failure is preserved. Neither outcome establishes
global nonintersection, uniqueness, proof, or topology.

## Result

EXP-472 passes every gate in two evaluations:

```text
(a, c) = (0.17985928422847947, 10.316953156190541)
Delta a = +1.2743516392688115e-6
Delta c = -3.915141725485682e-6
signed arclength = 0.004598680736496077
maximum block defect = 3.19975131291399e-9
minimum singular value = 8.01872542256545e-10
node-boundary margin = 0.9938611038487002
```

Raw receipt: `artifacts/EXP-472/receipt.json`, 78,637 bytes,
SHA-256 `a94d266fe99dca283811fa20d6406cbc9d26c739310f1745088a1849baa33fce`.
Compact receipt: [`receipts/EXP-472.json`](receipts/EXP-472.json).

Manifest:
[`../../experiments/manifests/EXP-472-jones-homoclinic-eighty-point-checkpoint.json`](../../experiments/manifests/EXP-472-jones-homoclinic-eighty-point-checkpoint.json).
