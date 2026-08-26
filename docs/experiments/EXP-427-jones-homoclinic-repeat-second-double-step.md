# EXP-427 — Repeat second adaptive double-step

Status: executed; passed every prospective gate

EXP-426 qualifies the new doubled step with comfortable margins. EXP-427 binds
the exact passed EXP-425/426 pair, recomputes the tangent at EXP-426, and holds
normalized arclength at `0.009197361472878517`. Every acceptance threshold
remains unchanged.

A pass adds the thirty-fifth qualified point and triggers a figure checkpoint.
A failure is preserved and returns the policy to quarter-step. Neither outcome
establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-427 passes every gate in two evaluations:

```text
(a, c) = (0.17982278902974164, 10.317065368485878)
Delta a = +6.832634990017183e-7
Delta c = -2.05317168600061e-6
signed arclength = 0.009197361472873505
maximum block defect = 6.4733581479261344e-9
minimum singular value = 1.0508716293716163e-9
node-boundary margin = 0.9829269436134638
```

Raw receipt: `artifacts/EXP-427/receipt.json`, 78,648 bytes,
SHA-256 `7b9c2408360ad6cac07605d71ceee86693c34dc38beca9ae9256f4245d2223b0`.
Compact receipt: [`receipts/EXP-427.json`](receipts/EXP-427.json).

Manifest:
[`../../experiments/manifests/EXP-427-jones-homoclinic-repeat-second-double-step.json`](../../experiments/manifests/EXP-427-jones-homoclinic-repeat-second-double-step.json).
