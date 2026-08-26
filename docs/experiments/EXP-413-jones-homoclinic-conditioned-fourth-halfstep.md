# EXP-413 — Fourth conditioned outgoing half-step

Status: executed; passed every prospective gate

EXP-412 passes a third conditioned half-step. EXP-413 binds the exact passed
EXP-411/412 pair, recomputes the tangent at EXP-412, and repeats normalized
arclength `0.009197361472878517` with every gate unchanged.

A pass adds a twenty-first qualified point and tests persistence of the
outgoing trend. It does not establish global nonintersection, uniqueness,
proof, or topology.

## Result

EXP-413 passes every gate in two evaluations:

```text
(a, c) = (0.17981822693797964, 10.31707938580511)
Delta a = +2.1131684213582247e-7
Delta c = -6.21838461611901e-7
signed arclength = 0.009197361472865031
maximum block defect = 6.675875009768019e-9
minimum singular value = 1.2040626414340024e-9
node-boundary margin = 0.981646541993598
```

This fourth consecutive conditioned half-step adds the twenty-first qualified
point. The root defect remains below the frozen gate and conditioning remains
comfortable, resolving a reproducible outgoing arm without proving its global
fate.

Raw receipt: `artifacts/EXP-413/receipt.json`, 78,531 bytes,
SHA-256 `68550310a97e5974f740431b57fe4d52d71b0a0e1e0d76d3f68edcc4673d4a34`.
Compact receipt: [`receipts/EXP-413.json`](receipts/EXP-413.json).

Manifest:
[`../../experiments/manifests/EXP-413-jones-homoclinic-conditioned-fourth-halfstep.json`](../../experiments/manifests/EXP-413-jones-homoclinic-conditioned-fourth-halfstep.json).
