# EXP-419 — Adaptive outgoing double-step

Status: executed; passed every prospective gate

EXP-416--418 pass three consecutive quarter-steps at the persistent
`3.20e-9` maximum-defect floor, with minimum singular value still above twice
its gate. EXP-419 binds the exact passed EXP-417/418 pair, recomputes the
tangent at EXP-418, and doubles normalized arclength to
`0.009197361472878517`. Every acceptance threshold remains unchanged.

A pass adds the twenty-seventh qualified point. A failure is preserved and
returns the policy to quarter-step. Neither outcome establishes global
nonintersection, uniqueness, proof, or topology.

## Result

EXP-419 passes every gate in two evaluations:

```text
(a, c) = (0.1798194835027311, 10.317075467157622)
Delta a = +3.782212705250032e-7
Delta c = -1.1165228261944549e-6
signed arclength = 0.009197361472872837
maximum block defect = 3.793684200085656e-9
minimum singular value = 1.1429607711155884e-9
node-boundary margin = 0.9821539086544675
```

The first doubled step is therefore qualified and remains comfortably inside
every numerical gate. EXP-420 repeats this doubled step after recomputing the
tangent at EXP-419; it does not enlarge the step again.

Raw receipt: `artifacts/EXP-419/receipt.json`, 78,622 bytes,
SHA-256 `317400c34a043195885d056714dd049c9e8f0a44204e9a4879100be6993f4978`.
Compact receipt: [`receipts/EXP-419.json`](receipts/EXP-419.json).

Manifest:
[`../../experiments/manifests/EXP-419-jones-homoclinic-adaptive-double-step.json`](../../experiments/manifests/EXP-419-jones-homoclinic-adaptive-double-step.json).
