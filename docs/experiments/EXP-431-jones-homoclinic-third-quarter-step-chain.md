# EXP-431 — Third point in current quarter-step chain

Status: executed; passed every prospective gate

EXP-429/430 qualify two consecutive defect-aware quarter-steps. EXP-431 binds
their exact receipts, recomputes the tangent at EXP-430, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold remains
unchanged.

A pass adds the thirty-ninth qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-431 passes every gate in two evaluations:

```text
(a, c) = (0.17982476193981012, 10.317059226198632)
Delta a = +4.262449761482934e-7
Delta c = -1.3294870200297737e-6
signed arclength = 0.004598680736431024
maximum block defect = 3.2000488230226367e-9
minimum singular value = 1.0129496355374346e-9
node-boundary margin = 0.9917152471474466
```

The defect has returned to the persistent numerical floor, but the minimum
singular value continues its gradual decline. EXP-432 therefore holds the
conservative quarter-step once more rather than doubling immediately. A pass
adds the fortieth qualified point and triggers a figure/manuscript checkpoint.

Raw receipt: `artifacts/EXP-431/receipt.json`, 78,687 bytes,
SHA-256 `d9d3570b4d16bda9f5777c26094d6ec7eadff07bdb0deed2b9359d933de94e15`.
Compact receipt: [`receipts/EXP-431.json`](receipts/EXP-431.json).

Manifest:
[`../../experiments/manifests/EXP-431-jones-homoclinic-third-quarter-step-chain.json`](../../experiments/manifests/EXP-431-jones-homoclinic-third-quarter-step-chain.json).
