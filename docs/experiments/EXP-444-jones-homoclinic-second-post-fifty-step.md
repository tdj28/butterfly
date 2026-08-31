# EXP-444 — Second conservative post-fifty-point step

Status: executed; passed every prospective gate

EXP-443 passes at the defect floor, but its minimum singular value is only
`1.85x` the fixed conditioning floor. EXP-444 therefore binds the exact passed
EXP-442/443 receipts, recomputes the tangent at EXP-443, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the fifty-second qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-444 passes every gate in two evaluations:

```text
(a, c) = (0.17983189117772697, 10.317037305336173)
Delta a = +6.613897587937068e-7
Delta c = -2.0313577984154563e-6
signed arclength = 0.004598680736440373
maximum block defect = 3.199968492555076e-9
minimum singular value = 9.196378305809325e-10
node-boundary margin = 0.9925158998180237
```

Raw receipt: `artifacts/EXP-444/receipt.json`, 78,693 bytes,
SHA-256 `020a4155c0e8cbce2a38b8d407316b4440fce94548169969ad243b853fc4e062`.
Compact receipt: [`receipts/EXP-444.json`](receipts/EXP-444.json).

Manifest:
[`../../experiments/manifests/EXP-444-jones-homoclinic-second-post-fifty-step.json`](../../experiments/manifests/EXP-444-jones-homoclinic-second-post-fifty-step.json).
