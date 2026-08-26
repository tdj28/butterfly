# EXP-430 — Repeat third defect-aware quarter-step

Status: executed; passed every prospective gate

EXP-429 qualifies the defect-aware reduction. EXP-430 binds the exact passed
EXP-428/429 pair, recomputes the tangent at EXP-429, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold remains
unchanged.

A pass adds the thirty-eighth qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-430 passes every gate in two evaluations:

```text
(a, c) = (0.17982433569483397, 10.317060555685652)
Delta a = +4.1037029038792916e-7
Delta c = -1.2969277864982587e-6
signed arclength = 0.004598680736436234
maximum block defect = 3.4424357533527506e-9
minimum singular value = 1.0204950347865223e-9
node-boundary margin = 0.9916687797231276
```

Raw receipt: `artifacts/EXP-430/receipt.json`, 78,627 bytes,
SHA-256 `1d601b53338923425e2f1ca00d37494ae3c947f1c5e052e8dad26d0d8884b9ab`.
Compact receipt: [`receipts/EXP-430.json`](receipts/EXP-430.json).

Manifest:
[`../../experiments/manifests/EXP-430-jones-homoclinic-repeat-third-quarter-step.json`](../../experiments/manifests/EXP-430-jones-homoclinic-repeat-third-quarter-step.json).
