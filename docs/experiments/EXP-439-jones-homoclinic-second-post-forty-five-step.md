# EXP-439 — Second conservative post-forty-five-point step

Status: executed; passed every prospective gate

EXP-438 remains at the defect floor with wide boundary margins. EXP-439 binds
the exact passed EXP-437/438 receipts, recomputes the tangent at EXP-438, and
holds normalized arclength at `0.0045986807364392585`. Every acceptance
threshold remains unchanged.

A pass adds the forty-seventh qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-439 passes every gate in two evaluations:

```text
(a, c) = (0.17982878098808988, 10.317046857779781)
Delta a = +5.6457487071504e-7
Delta c = -1.7340919811204003e-6
signed arclength = 0.00459868073644629
maximum block defect = 3.1999962913963887e-9
minimum singular value = 9.541881150403697e-10
node-boundary margin = 0.9921598876171629
```

Raw receipt: `artifacts/EXP-439/receipt.json`, 78,681 bytes,
SHA-256 `dfbded8b9dec48bcb18245a373bb7120a1010400b66a5e6bf088636b3c8546ee`.
Compact receipt: [`receipts/EXP-439.json`](receipts/EXP-439.json).

Manifest:
[`../../experiments/manifests/EXP-439-jones-homoclinic-second-post-forty-five-step.json`](../../experiments/manifests/EXP-439-jones-homoclinic-second-post-forty-five-step.json).
