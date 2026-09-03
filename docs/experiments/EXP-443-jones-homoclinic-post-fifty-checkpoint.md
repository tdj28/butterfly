# EXP-443 — Conservative post-fifty-point successor

Status: executed; passed every prospective gate

EXP-442 closes the receipt-bound 50-point checkpoint at the defect floor, but
its minimum singular value is only `1.87x` the fixed conditioning floor.
EXP-443 therefore binds the exact passed EXP-441/442 receipts, recomputes the
tangent at EXP-442, and holds normalized arclength at
`0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the fifty-first qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-443 passes every gate in two evaluations:

```text
(a, c) = (0.17983122978796817, 10.317039336693972)
Delta a = +6.414053912995321e-7
Delta c = -1.9699645967818924e-6
signed arclength = 0.004598680736435413
maximum block defect = 3.1999742462252293e-9
minimum singular value = 9.263682608694516e-10
node-boundary margin = 0.9924392254129444
```

Raw receipt: `artifacts/EXP-443/receipt.json`, 78,649 bytes,
SHA-256 `fe44913a59af5662a1ab7e34570e9dbc267f2a3d79aa4d1047e7460a64c91879`.
Compact receipt: [`receipts/EXP-443.json`](receipts/EXP-443.json).

Manifest:
[`../../experiments/manifests/EXP-443-jones-homoclinic-post-fifty-checkpoint.json`](../../experiments/manifests/EXP-443-jones-homoclinic-post-fifty-checkpoint.json).
