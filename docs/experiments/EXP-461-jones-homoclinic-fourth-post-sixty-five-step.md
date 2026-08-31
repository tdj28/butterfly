# EXP-461 — Fourth conservative post-sixty-five-point step

Status: executed; passed every prospective gate

EXP-460 passes at the defect floor, but its minimum singular value is only
`1.66x` the fixed conditioning floor. EXP-461 therefore binds the exact passed
EXP-459/460 receipts, recomputes the tangent at EXP-460, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the sixty-ninth qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-461 passes every gate in two evaluations:

```text
(a, c) = (0.1798464324074268, 10.31699263907364)
Delta a = +1.0353316644562405e-6
Delta c = -3.180519033918472e-6
signed arclength = 0.004598680736439123
maximum block defect = 3.1998500120013065e-9
minimum singular value = 8.273806158992892e-10
node-boundary margin = 0.994022266002597
```

Raw receipt: `artifacts/EXP-461/receipt.json`, 78,650 bytes,
SHA-256 `79a9554ed9bf2da76beaa09a8db7d3c93ee0e09d75df79ae005d52dc61a3a67a`.
Compact receipt: [`receipts/EXP-461.json`](receipts/EXP-461.json).

Manifest:
[`../../experiments/manifests/EXP-461-jones-homoclinic-fourth-post-sixty-five-step.json`](../../experiments/manifests/EXP-461-jones-homoclinic-fourth-post-sixty-five-step.json).
