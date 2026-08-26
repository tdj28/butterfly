# EXP-408 — Sixteenfold-base post-turn step

Status: executed; passed all prospective gates

EXP-407 passes at normalized step `0.0045986807364392585`, with only `0.00941`
normalized node displacement and ample global margins.  Its corrected point
moves decisively toward larger `a` and smaller `c` after the local minimum.

EXP-408 binds EXP-406/407, recomputes the tangent at EXP-407, aligns it with
their full-state secant, and increases normalized arclength fourfold to
`0.018394722945757034`.  Both parameters remain unconstrained and signed
full-state arclength remains the direction gate.  Every numerical-quality,
conditioning, margin, integration, and optimizer threshold is unchanged.

A pass adds a seventeenth point and accelerates the outgoing-branch trace.  It
does not establish global nonintersection, uniqueness, proof, or topology.

## Result

EXP-408 passes every gate in four evaluations:

```text
(a, c) = (0.1798176031556253, 10.31708116500237)
Delta a = +1.01389154710807e-7
Delta c = -3.1843000058984217e-7
signed arclength = 0.01839472294581864
maximum block defect = 3.2014760135363268e-9
minimum singular value = 1.2641974917275312e-9
node margin = 0.9630351160415529
```

This adds the seventeenth point and separates the outgoing branch clearly from
the local minimum.  EXP-409 freezes one more same-scale chained step to test
whether this trend persists without another step increase.

Raw receipt: `artifacts/EXP-408/receipt.json`, 79,254 bytes,
SHA-256 `38ed9bf6012a15942b724161fe1fb7c25f7d1234903850a96c50851440cbeff8`.
Compact receipt: [`receipts/EXP-408.json`](receipts/EXP-408.json).

Manifest:
[`../../experiments/manifests/EXP-408-jones-homoclinic-postturn-sixteenfold-step.json`](../../experiments/manifests/EXP-408-jones-homoclinic-postturn-sixteenfold-step.json).
