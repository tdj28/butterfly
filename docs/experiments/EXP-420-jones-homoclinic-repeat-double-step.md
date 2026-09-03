# EXP-420 — Repeat outgoing double-step

Status: executed; passed every prospective gate

EXP-419 qualifies the first adaptive double-step with maximum defect
`3.794e-9`, minimum singular value `1.143e-9`, and two evaluations. EXP-420
binds the exact passed EXP-418/419 pair, recomputes the tangent at EXP-419, and
holds normalized arclength at `0.009197361472878517`. Every acceptance
threshold remains unchanged.

A pass adds the twenty-eighth qualified point. A failure is preserved and
returns the policy to quarter-step. Neither outcome establishes global
nonintersection, uniqueness, proof, or topology.

## Result

EXP-420 passes every gate in two evaluations:

```text
(a, c) = (0.17981990761176878, 10.317074203664605)
Delta a = +4.241090376666534e-7
Delta c = -1.2634930168786696e-6
signed arclength = 0.009197361472876517
maximum block defect = 5.71266351566524e-9
minimum singular value = 1.1276252152329895e-9
node-boundary margin = 0.9823022025657338
```

The second consecutive doubled step is qualified. EXP-421 repeats the same
step once more after recomputing the tangent at EXP-420.

Raw receipt: `artifacts/EXP-420/receipt.json`, 78,563 bytes,
SHA-256 `c57234080b7acb3cb3c5913fc40cd3f846fdb68cff7e7bc4464da45089cdd31b`.
Compact receipt: [`receipts/EXP-420.json`](receipts/EXP-420.json).

Manifest:
[`../../experiments/manifests/EXP-420-jones-homoclinic-repeat-double-step.json`](../../experiments/manifests/EXP-420-jones-homoclinic-repeat-double-step.json).
