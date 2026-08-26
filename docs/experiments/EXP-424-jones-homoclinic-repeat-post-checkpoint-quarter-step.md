# EXP-424 — Repeat post-checkpoint quarter-step

Status: executed; passed every prospective gate

EXP-423 qualifies the first point beyond the figure checkpoint. EXP-424 binds
the exact passed EXP-422/423 pair, recomputes the tangent at EXP-423, and holds
normalized arclength at `0.0045986807364392585`. Every acceptance threshold
remains unchanged.

A pass adds the thirty-second qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-424 passes every gate in two evaluations:

```text
(a, c) = (0.17982118406053907, 10.317070210090035)
Delta a = +2.811330139240731e-7
Delta c = -8.812732694707393e-7
signed arclength = 0.004598680736444361
maximum block defect = 3.2001329025753887e-9
minimum singular value = 1.0891655637185577e-9
node-boundary margin = 0.9913233570392137
```

Raw receipt: `artifacts/EXP-424/receipt.json`, 78,532 bytes,
SHA-256 `21d68c8806945e09bdd3bc58ba006e7c8e01cb39004993ab470f773ec88d4d83`.
Compact receipt: [`receipts/EXP-424.json`](receipts/EXP-424.json).

Manifest:
[`../../experiments/manifests/EXP-424-jones-homoclinic-repeat-post-checkpoint-quarter-step.json`](../../experiments/manifests/EXP-424-jones-homoclinic-repeat-post-checkpoint-quarter-step.json).
