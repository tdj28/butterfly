# EXP-471 — Fourth conservative post-seventy-five-point step

Status: executed; passed every prospective gate

EXP-470 passes at the defect floor, but its minimum singular value is only
`1.61x` the fixed conditioning floor. EXP-471 therefore binds the exact passed
EXP-469/470 receipts, recomputes the tangent at EXP-470, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the seventy-ninth qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-471 passes every gate in two evaluations:

```text
(a, c) = (0.1798580098768402, 10.316957071332267)
Delta a = +1.2542045723651363e-6
Delta c = -3.85322944751465e-6
signed arclength = 0.004598680736410118
maximum block defect = 3.1997605598566762e-9
minimum singular value = 8.02785104500578e-10
node-boundary margin = 0.9938653672585698
```

Raw receipt: `artifacts/EXP-471/receipt.json`, 78,691 bytes,
SHA-256 `f1e020c1391b5086fc253b3988fb15c0b5aac96f69af9367d882c0037da416e9`.
Compact receipt: [`receipts/EXP-471.json`](receipts/EXP-471.json).

Manifest:
[`../../experiments/manifests/EXP-471-jones-homoclinic-fourth-post-seventy-five-step.json`](../../experiments/manifests/EXP-471-jones-homoclinic-fourth-post-seventy-five-step.json).
