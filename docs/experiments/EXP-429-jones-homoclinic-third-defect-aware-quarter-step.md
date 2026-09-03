# EXP-429 — Third defect-aware quarter-step reduction

Status: executed; passed every prospective gate

EXP-428 qualifies the third doubled step but uses 84.2% of the hard root gate.
EXP-429 binds the exact passed EXP-427/428 pair, recomputes the tangent at
EXP-428, and returns normalized arclength to `0.0045986807364392585`. Every
acceptance threshold remains unchanged.

A pass adds the thirty-seventh qualified point. A failure is preserved.
Neither outcome establishes global nonintersection, uniqueness, proof, or
topology.

## Result

EXP-429 passes every gate in two evaluations:

```text
(a, c) = (0.17982392532454358, 10.317061852613438)
Delta a = +3.948107829554459e-7
Delta c = -1.2780725935357395e-6
signed arclength = 0.004598680736432861
maximum block defect = 5.223704638209505e-9
minimum singular value = 1.0280737408487904e-9
node-boundary margin = 0.991624084657424
```

Raw receipt: `artifacts/EXP-429/receipt.json`, 78,724 bytes,
SHA-256 `8d28dcefaddc848dade2343f955356ac6239c39fc4dc670ae2d1f20362c5d5f6`.
Compact receipt: [`receipts/EXP-429.json`](receipts/EXP-429.json).

Manifest:
[`../../experiments/manifests/EXP-429-jones-homoclinic-third-defect-aware-quarter-step.json`](../../experiments/manifests/EXP-429-jones-homoclinic-third-defect-aware-quarter-step.json).
