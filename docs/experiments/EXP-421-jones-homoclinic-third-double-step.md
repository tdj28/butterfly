# EXP-421 — Third outgoing double-step

Status: executed; passed every prospective gate

EXP-419 and EXP-420 qualify two consecutive doubled steps. EXP-421 binds the
exact passed EXP-419/420 pair, recomputes the tangent at EXP-420, and holds
normalized arclength at `0.009197361472878517`. Every acceptance threshold
remains unchanged.

A pass adds the twenty-ninth qualified point. A failure is preserved and
returns the policy to quarter-step. Neither outcome establishes global
nonintersection, uniqueness, proof, or topology.

## Result

EXP-421 passes every gate in two evaluations:

```text
(a, c) = (0.17982037944154092, 10.317072788605973)
Delta a = +4.7182977214177413e-7
Delta c = -1.4150586320482716e-6
signed arclength = 0.009197361472868672
maximum block defect = 7.3878045401729176e-9
minimum singular value = 1.112273997393049e-9
node-boundary margin = 0.9824102449813594
```

The third consecutive doubled step is qualified, but maximum defect has risen
to 73.9% of its hard gate. EXP-422 therefore returns prospectively to the
proven quarter-step after recomputing the tangent at EXP-421.

Raw receipt: `artifacts/EXP-421/receipt.json`, 78,559 bytes,
SHA-256 `1beed362f67665f802d5237aafddc42dfa7e7cba8d52d5755661a4d94498f664`.
Compact receipt: [`receipts/EXP-421.json`](receipts/EXP-421.json).

Manifest:
[`../../experiments/manifests/EXP-421-jones-homoclinic-third-double-step.json`](../../experiments/manifests/EXP-421-jones-homoclinic-third-double-step.json).
