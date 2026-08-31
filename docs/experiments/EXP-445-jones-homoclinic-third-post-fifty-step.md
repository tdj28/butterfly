# EXP-445 — Third conservative post-fifty-point step

Status: executed; passed every prospective gate

EXP-444 passes at the defect floor, but its minimum singular value is only
`1.84x` the fixed conditioning floor. EXP-445 therefore binds the exact passed
EXP-443/444 receipts, recomputes the tangent at EXP-444, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the fifty-third qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-445 passes every gate in two evaluations:

```text
(a, c) = (0.17983257285126794, 10.317035211660485)
Delta a = +6.816735409753694e-7
Delta c = -2.0936756879308405e-6
signed arclength = 0.004598680736423289
maximum block defect = 3.1999626934048755e-9
minimum singular value = 9.130107604819868e-10
node-boundary margin = 0.9925954781104451
```

Raw receipt: `artifacts/EXP-445/receipt.json`, 78,633 bytes,
SHA-256 `e2f5b66ae272cc5482f8a4e4abe907a64f7922629f53cb88eea35c521ac87423`.
Compact receipt: [`receipts/EXP-445.json`](receipts/EXP-445.json).

Manifest:
[`../../experiments/manifests/EXP-445-jones-homoclinic-third-post-fifty-step.json`](../../experiments/manifests/EXP-445-jones-homoclinic-third-post-fifty-step.json).
