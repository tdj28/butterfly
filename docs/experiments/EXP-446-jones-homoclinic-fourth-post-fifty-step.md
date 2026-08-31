# EXP-446 — Fourth conservative post-fifty-point step

Status: executed; passed every prospective gate

EXP-445 passes at the defect floor, but its minimum singular value is only
`1.83x` the fixed conditioning floor. EXP-446 therefore binds the exact passed
EXP-444/445 receipts, recomputes the tangent at EXP-445, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the fifty-fourth qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-446 passes every gate in two evaluations:

```text
(a, c) = (0.17983327509978012, 10.317033054768622)
Delta a = +7.022485121743749e-7
Delta c = -2.156891863336341e-6
signed arclength = 0.004598680736434709
maximum block defect = 3.1999568000620774e-9
minimum singular value = 9.064937090906435e-10
node-boundary margin = 0.9926780369844934
```

Raw receipt: `artifacts/EXP-446/receipt.json`, 78,621 bytes,
SHA-256 `5f3df28b58bdd6c2263a1ab4c506fe27572d63de37f20b54b1566dd9ba00c736`.
Compact receipt: [`receipts/EXP-446.json`](receipts/EXP-446.json).

Manifest:
[`../../experiments/manifests/EXP-446-jones-homoclinic-fourth-post-fifty-step.json`](../../experiments/manifests/EXP-446-jones-homoclinic-fourth-post-fifty-step.json).
