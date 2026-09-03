# EXP-451 — Ninth conservative post-fifty-point step

Status: executed; passed every prospective gate

EXP-450 passes at the defect floor, but its minimum singular value is only
`1.76x` the fixed conditioning floor. EXP-451 therefore binds the exact passed
EXP-449/450 receipts, recomputes the tangent at EXP-450, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the fifty-ninth qualified point and licenses the same-size
sixty-point checkpoint attempt. A failure is preserved. Neither outcome
establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-451 passes every gate in two evaluations:

```text
(a, c) = (0.1798371044053574, 10.317021292982432)
Delta a = +8.091030786194775e-7
Delta c = -2.485235455651491e-6
signed arclength = 0.0045986807364082755
maximum block defect = 3.1999251040590094e-9
minimum singular value = 8.758279526012158e-10
node-boundary margin = 0.9931380784605679
```

Raw receipt: `artifacts/EXP-451/receipt.json`, 78,743 bytes,
SHA-256 `083f7102e3e3c929b92e7861a24d278aa1017a007842c10604dec4ad50ff897c`.
Compact receipt: [`receipts/EXP-451.json`](receipts/EXP-451.json).

Manifest:
[`../../experiments/manifests/EXP-451-jones-homoclinic-ninth-post-fifty-step.json`](../../experiments/manifests/EXP-451-jones-homoclinic-ninth-post-fifty-step.json).
