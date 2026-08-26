# EXP-422 — Defect-aware quarter-step

Status: executed; passed every prospective gate

EXP-421 qualifies the third consecutive doubled step, but its maximum defect
has risen to 73.9% of the hard root gate. EXP-422 binds the exact passed
EXP-420/421 pair, recomputes the tangent at EXP-421, and returns normalized
arclength to `0.0045986807364392585`. Every acceptance threshold remains
unchanged.

A pass adds the thirtieth qualified point and triggers the planned figure and
manuscript checkpoint. A failure is preserved. Neither outcome establishes
global nonintersection, uniqueness, proof, or topology.

## Result

EXP-422 passes every gate in two evaluations:

```text
(a, c) = (0.1798206348113553, 10.317071946863937)
Delta a = +2.553698143781258e-7
Delta c = -8.417420360729011e-7
signed arclength = 0.00459868073642693
maximum block defect = 4.583852170039189e-9
minimum singular value = 1.1045871273016951e-9
node-boundary margin = 0.9912613041673239
```

The defect-aware reduction restores defect margin and adds the thirtieth
qualified point. The figure, manuscript, and claim-ledger checkpoint now
incorporates EXP-418--422.

Raw receipt: `artifacts/EXP-422/receipt.json`, 78,618 bytes,
SHA-256 `55d1b075b6c152a78f1a0cf540e73173023ce053789d7b0b91f5dfd4ef2fbb15`.
Compact receipt: [`receipts/EXP-422.json`](receipts/EXP-422.json).

Manifest:
[`../../experiments/manifests/EXP-422-jones-homoclinic-defect-aware-quarter-step.json`](../../experiments/manifests/EXP-422-jones-homoclinic-defect-aware-quarter-step.json).
