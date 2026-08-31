# EXP-462 — Seventy-point homoclinic checkpoint attempt

Status: executed; passed every prospective gate

EXP-461 passes at the defect floor, but its minimum singular value is only
`1.65x` the fixed conditioning floor. EXP-462 therefore binds the exact passed
EXP-460/461 receipts, recomputes the tangent at EXP-461, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the seventieth qualified point and triggers a receipt-bound figure
and manuscript refresh. A failure is preserved. Neither outcome establishes
global nonintersection, uniqueness, proof, or topology.

## Result

EXP-462 passes every gate in two evaluations:

```text
(a, c) = (0.1798474905197595, 10.3169893885338)
Delta a = +1.058112332724681e-6
Delta c = -3.2505398390725304e-6
signed arclength = 0.004598680736386297
maximum block defect = 3.1998415721262874e-9
minimum singular value = 8.23728082842405e-10
node-boundary margin = 0.9939980592662687
```

Raw receipt: `artifacts/EXP-462/receipt.json`, 78,683 bytes,
SHA-256 `4bf9cd03b27a49e7aacb6234ed4961a307f0c2ef11b87c866759e334e324d2f5`.
Compact receipt: [`receipts/EXP-462.json`](receipts/EXP-462.json).

Manifest:
[`../../experiments/manifests/EXP-462-jones-homoclinic-seventy-point-checkpoint.json`](../../experiments/manifests/EXP-462-jones-homoclinic-seventy-point-checkpoint.json).
