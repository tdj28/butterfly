# EXP-423 — Post-checkpoint outgoing quarter-step

Status: executed; passed every prospective gate

EXP-422 qualifies the defect-aware reduction and closes the 30-point figure
checkpoint. EXP-423 binds the exact passed EXP-421/422 pair, recomputes the
tangent at EXP-422, and holds normalized arclength at
`0.0045986807364392585`. Every acceptance threshold remains unchanged.

A pass adds the thirty-first qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-423 passes every gate in two evaluations:

```text
(a, c) = (0.17982090292752514, 10.317071091363305)
Delta a = +2.681161698492307e-7
Delta c = -8.555006321131486e-7
signed arclength = 0.004598680736433894
maximum block defect = 3.2001446174639726e-9
minimum singular value = 1.0968739932468152e-9
node-boundary margin = 0.9912917448560989
```

Raw receipt: `artifacts/EXP-423/receipt.json`, 78,575 bytes,
SHA-256 `f2d81805a026c1b741622e11377f7d00eddfdd7da8eb90814f798a8c3013fa05`.
Compact receipt: [`receipts/EXP-423.json`](receipts/EXP-423.json).

Manifest:
[`../../experiments/manifests/EXP-423-jones-homoclinic-post-checkpoint-quarter-step.json`](../../experiments/manifests/EXP-423-jones-homoclinic-post-checkpoint-quarter-step.json).
