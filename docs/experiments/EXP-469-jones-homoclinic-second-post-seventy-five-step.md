# EXP-469 — Second conservative post-seventy-five-point step

Status: executed; passed every prospective gate

EXP-468 passes at the defect floor, but its minimum singular value is only
`1.61x` the fixed conditioning floor. EXP-469 therefore binds the exact passed
EXP-467/468 receipts, recomputes the tangent at EXP-468, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the seventy-seventh qualified point. A failure is preserved.
Neither outcome establishes global nonintersection, uniqueness, proof, or
topology.

## Result

EXP-469 passes every gate in two evaluations:

```text
(a, c) = (0.17985552203128571, 10.316964714594972)
Delta a = +1.2126901124398515e-6
Delta c = -3.725644562635466e-6
signed arclength = 0.004598680736467822
maximum block defect = 3.199779173213645e-9
minimum singular value = 8.054840696863713e-10
node-boundary margin = 0.9938804489142896
```

Raw receipt: `artifacts/EXP-469/receipt.json`, 78,650 bytes,
SHA-256 `459bfe4f8889f243ba32e879b09436a16dc4e724b7c1a79a09e0fc4103cedef3`.
Compact receipt: [`receipts/EXP-469.json`](receipts/EXP-469.json).

Manifest:
[`../../experiments/manifests/EXP-469-jones-homoclinic-second-post-seventy-five-step.json`](../../experiments/manifests/EXP-469-jones-homoclinic-second-post-seventy-five-step.json).
