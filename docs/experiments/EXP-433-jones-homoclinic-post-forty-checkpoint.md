# EXP-433 — Conservative post-forty-point successor

Status: executed; passed every prospective gate

EXP-432 closes the receipt-bound 40-point checkpoint with its defect at the
persistent numerical floor. Its smallest measured singular value is only
`2.01x` the fixed acceptance floor, so EXP-433 binds the exact passed
EXP-431/432 receipts, recomputes the tangent at EXP-432, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold remains
unchanged.

A pass adds the forty-first qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-433 passes every gate in two evaluations:

```text
(a, c) = (0.17982566328771324, 10.317056440329397)
Delta a = +4.589209526006943e-7
Delta c = -1.4157353760424485e-6
signed arclength = 0.004598680736440425
maximum block defect = 3.200030748480289e-9
minimum singular value = 9.979685140687292e-10
node-boundary margin = 0.9918137927466901
```

The defect remains at the numerical floor and the node margin remains wide.
The minimum singular value is now just below twice the fixed gate, so EXP-434
holds the same conservative step rather than enlarging it.

Raw receipt: `artifacts/EXP-433/receipt.json`, 78,647 bytes,
SHA-256 `cb69fcc72d6dfc58dd1fab4ffff51ddb0bd78d3c7f38d2e28cc788608a4a1064`.
Compact receipt: [`receipts/EXP-433.json`](receipts/EXP-433.json).

Manifest:
[`../../experiments/manifests/EXP-433-jones-homoclinic-post-forty-checkpoint.json`](../../experiments/manifests/EXP-433-jones-homoclinic-post-forty-checkpoint.json).
