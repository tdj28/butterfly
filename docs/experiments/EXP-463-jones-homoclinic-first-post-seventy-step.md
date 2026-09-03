# EXP-463 — First conservative post-seventy-point step

Status: executed; passed every prospective gate

EXP-462 passes at the defect floor, but its minimum singular value is only
`1.65x` the fixed conditioning floor. EXP-463 therefore binds the exact passed
EXP-461/462 receipts, recomputes the tangent at EXP-462, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the seventy-first qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-463 passes every gate in two evaluations:

```text
(a, c) = (0.1798485713104803, 10.316986068288356)
Delta a = +1.080790720781044e-6
Delta c = -3.320245443916292e-6
signed arclength = 0.004598680736443392
maximum block defect = 3.199833002925271e-9
minimum singular value = 8.203240088164703e-10
node-boundary margin = 0.993975553988995
```

Raw receipt: `artifacts/EXP-463/receipt.json`, 78,628 bytes,
SHA-256 `131700859842c1b11a4586b15e90d67deb30142cb57463b868d8043db74a4c40`.
Compact receipt: [`receipts/EXP-463.json`](receipts/EXP-463.json).

Manifest:
[`../../experiments/manifests/EXP-463-jones-homoclinic-first-post-seventy-step.json`](../../experiments/manifests/EXP-463-jones-homoclinic-first-post-seventy-step.json).
