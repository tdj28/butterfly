# EXP-458 — First conservative post-sixty-five-point step

Status: executed; passed every prospective gate

EXP-457 passes at the defect floor, but its minimum singular value is only
`1.69x` the fixed conditioning floor. EXP-458 therefore binds the exact passed
EXP-456/457 receipts, recomputes the tangent at EXP-457, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the sixty-sixth qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-458 passes every gate in two evaluations:

```text
(a, c) = (0.1798433949842735, 10.317001969868361)
Delta a = +9.667292291126728e-7
Delta c = -2.969664928187399e-6
signed arclength = 0.004598680736428072
maximum block defect = 3.199874328179077e-9
minimum singular value = 8.397550033283366e-10
node-boundary margin = 0.9939236977819803
```

Raw receipt: `artifacts/EXP-458/receipt.json`, 78,641 bytes,
SHA-256 `ee008f715b86fcf4a3297dbba157ede88981179f7b50a3fcfefe5b70da1c9555`.
Compact receipt: [`receipts/EXP-458.json`](receipts/EXP-458.json).

Manifest:
[`../../experiments/manifests/EXP-458-jones-homoclinic-first-post-sixty-five-step.json`](../../experiments/manifests/EXP-458-jones-homoclinic-first-post-sixty-five-step.json).
