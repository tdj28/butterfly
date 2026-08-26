# EXP-426 — Second adaptive outgoing double-step regime

Status: executed; passed every prospective gate

EXP-423--425 qualify three consecutive post-checkpoint quarter-steps at the
`3.20e-9` defect floor. EXP-426 binds the exact passed EXP-424/425 pair,
recomputes the tangent at EXP-425, and doubles normalized arclength to
`0.009197361472878517`. Every acceptance threshold remains unchanged.

A pass adds the thirty-fourth qualified point. A failure is preserved and
returns the policy to quarter-step. Neither outcome establishes global
nonintersection, uniqueness, proof, or topology.

## Result

EXP-426 passes every gate in two evaluations:

```text
(a, c) = (0.17982210576624263, 10.317067421657564)
Delta a = +6.272924661931967e-7
Delta c = -1.8743126499742857e-6
signed arclength = 0.009197361472881745
maximum block defect = 4.243501927402745e-9
minimum singular value = 1.0661324269887145e-9
node-boundary margin = 0.9827828965534096
```

Raw receipt: `artifacts/EXP-426/receipt.json`, 78,692 bytes,
SHA-256 `d4684feae49445c97648308a3a08d2505021d41cf753fb59ab668ab3164bfc87`.
Compact receipt: [`receipts/EXP-426.json`](receipts/EXP-426.json).

Manifest:
[`../../experiments/manifests/EXP-426-jones-homoclinic-second-adaptive-double-step.json`](../../experiments/manifests/EXP-426-jones-homoclinic-second-adaptive-double-step.json).
