# EXP-411 — Repeated conditioned outgoing half-step

Status: executed; passed every prospective gate

EXP-410 recovers comfortable conditioning at normalized arclength
`0.009197361472878517`. EXP-411 binds the exact passed EXP-408/410 pair,
recomputes the tangent at EXP-410, aligns it with their full-state secant, and
repeats that step with every gate unchanged.

A pass adds a nineteenth qualified point and tests whether the conditioned
outgoing trend persists. It does not establish global nonintersection,
uniqueness, proof, or topology.

## Result

EXP-411 passes every gate in two evaluations:

```text
(a, c) = (0.17981784213116253, 10.317080509277266)
Delta a = +1.37051304915925e-7
Delta c = -3.847965750480853e-7
signed arclength = 0.009197361472853214
maximum block defect = 3.812750018598277e-9
minimum singular value = 1.234246763155655e-9
node-boundary margin = 0.9814370704121274
```

The newly recomputed tangent reproduces the outgoing trend with comfortable
conditioning. This adds the nineteenth qualified point and rules out a
one-step recovery artifact, but not a later turn or another branch.

Raw receipt: `artifacts/EXP-411/receipt.json`, 78,510 bytes,
SHA-256 `a25dc39c991b03913446c6bf3a8cbdbb20a00d77d79abf24582056e88decce71`.
Compact receipt: [`receipts/EXP-411.json`](receipts/EXP-411.json).

Manifest:
[`../../experiments/manifests/EXP-411-jones-homoclinic-conditioned-repeat-halfstep.json`](../../experiments/manifests/EXP-411-jones-homoclinic-conditioned-repeat-halfstep.json).
