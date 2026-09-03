# EXP-409 — Repeated post-turn homoclinic step

Status: executed; failed the prospective conditioning floor alone

EXP-408 passes the accelerated normalized step `0.018394722945757034` and
moves `a` upward by `1.01389e-7` with comfortable margins. EXP-409 binds the
passed EXP-407/408 pair, recomputes the tangent at EXP-408, and repeats the
same coordinate-free step and every numerical gate.

A pass adds an eighteenth point and tests persistence of the outgoing trend.
It does not establish global nonintersection, uniqueness, proof, or topology.

## Result

EXP-409 finds a clean forward root in 12 evaluations, but does not pass:

```text
(a, c) = (0.17981786298396138, 10.317080367276866)
Delta a = +2.598283360688569e-7
Delta c = -7.97725505208291e-7
maximum block defect = 2.3383926265602196e-9
minimum singular value = 4.2239893646025396e-10
```

Conditioning is the sole failed check; the singular value is below the fixed
`5e-10` floor.  EXP-410 halves normalized arclength to
`0.009197361472878517` from the same passed EXP-407/408 sources and leaves all
thresholds unchanged.

Raw receipt: `artifacts/EXP-409/receipt.json`, 80,792 bytes,
SHA-256 `aad8be54a0d777bed3375dae413e341908e8aec54127385f5a35ddd193dd297e`.
Compact receipt: [`receipts/EXP-409.json`](receipts/EXP-409.json).

Manifest:
[`../../experiments/manifests/EXP-409-jones-homoclinic-postturn-repeat-step.json`](../../experiments/manifests/EXP-409-jones-homoclinic-postturn-repeat-step.json).
