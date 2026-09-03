# EXP-450 — Eighth conservative post-fifty-point step

Status: executed; passed every prospective gate

EXP-449 passes at the defect floor, but its minimum singular value is only
`1.78x` the fixed conditioning floor. EXP-450 therefore binds the exact passed
EXP-448/449 receipts, recomputes the tangent at EXP-449, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the fifty-eighth qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-450 passes every gate in two evaluations:

```text
(a, c) = (0.1798362953022788, 10.317023778217887)
Delta a = +7.872466323832761e-7
Delta c = -2.41807084577772e-6
signed arclength = 0.004598680736452584
maximum block defect = 3.199931707865768e-9
minimum singular value = 8.816791471948846e-10
node-boundary margin = 0.99303955114069
```

Raw receipt: `artifacts/EXP-450/receipt.json`, 78,610 bytes,
SHA-256 `5dcbfa7ac3c26c3517c6e3a3bb9cb77382844dbbd6d88641c83f64c11f18911c`.
Compact receipt: [`receipts/EXP-450.json`](receipts/EXP-450.json).

Manifest:
[`../../experiments/manifests/EXP-450-jones-homoclinic-eighth-post-fifty-step.json`](../../experiments/manifests/EXP-450-jones-homoclinic-eighth-post-fifty-step.json).
