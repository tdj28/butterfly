# EXP-468 — First conservative post-seventy-five-point step

Status: executed; passed every prospective gate

EXP-467 passes at the defect floor, but its minimum singular value is only
`1.62x` the fixed conditioning floor. EXP-468 therefore binds the exact passed
EXP-466/467 receipts, recomputes the tangent at EXP-467, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the seventy-sixth qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-468 passes every gate in two evaluations:

```text
(a, c) = (0.17985430934117327, 10.316968440239535)
Delta a = +1.1913856155509883e-6
Delta c = -3.6601672235292426e-6
signed arclength = 0.004598680736453933
maximum block defect = 3.1997883185634873e-9
minimum singular value = 8.072649888863062e-10
node-boundary margin = 0.9938912216178979
```

Raw receipt: `artifacts/EXP-468/receipt.json`, 78,608 bytes,
SHA-256 `1a1b442d0ae81d815931f69737f9670f148c911b20503893be815271fb467b9a`.
Compact receipt: [`receipts/EXP-468.json`](receipts/EXP-468.json).

Manifest:
[`../../experiments/manifests/EXP-468-jones-homoclinic-first-post-seventy-five-step.json`](../../experiments/manifests/EXP-468-jones-homoclinic-first-post-seventy-five-step.json).
