# EXP-425 — Third post-checkpoint quarter-step

Status: executed; passed every prospective gate

EXP-423 and EXP-424 qualify two post-checkpoint quarter-steps at the persistent
defect floor. EXP-425 binds their exact receipts, recomputes the tangent at
EXP-424, and holds normalized arclength at `0.0045986807364392585`. Every
acceptance threshold remains unchanged.

A pass adds the thirty-third qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-425 passes every gate in two evaluations:

```text
(a, c) = (0.17982147847377644, 10.317069295970214)
Delta a = +2.9441323737278147e-7
Delta c = -9.141198216155999e-7
signed arclength = 0.004598680736436638
maximum block defect = 3.2001239508191048e-9
minimum singular value = 1.081462877776198e-9
node-boundary margin = 0.9913561926589338
```

Raw receipt: `artifacts/EXP-425/receipt.json`, 78,598 bytes,
SHA-256 `f898b24f71f2dbdeb484523987d8cf599b81c6a2128a6fb9646409afa4c310ca`.
Compact receipt: [`receipts/EXP-425.json`](receipts/EXP-425.json).

Manifest:
[`../../experiments/manifests/EXP-425-jones-homoclinic-third-post-checkpoint-quarter-step.json`](../../experiments/manifests/EXP-425-jones-homoclinic-third-post-checkpoint-quarter-step.json).
