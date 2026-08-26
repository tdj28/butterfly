# EXP-428 — Third step in second doubled regime

Status: executed; passed every prospective gate

EXP-426/427 qualify two consecutive doubled steps. EXP-428 binds their exact
receipts, recomputes the tangent at EXP-427, and holds normalized arclength at
`0.009197361472878517`. Every acceptance threshold remains unchanged.

A pass adds the thirty-sixth qualified point. A failure is preserved and
returns the policy to quarter-step. Neither outcome establishes global
nonintersection, uniqueness, proof, or topology.

## Result

EXP-428 passes every gate in two evaluations:

```text
(a, c) = (0.17982353051376063, 10.317063130686032)
Delta a = +7.414840189901017e-7
Delta c = -2.237799845872246e-6
signed arclength = 0.009197361472859586
maximum block defect = 8.4197114421345e-9
minimum singular value = 1.0356793674645222e-9
node-boundary margin = 0.9830824997752003
```

The result is qualified, but maximum defect uses 84.2% of the root gate.
EXP-429 therefore returns prospectively to the proven quarter-step.

Raw receipt: `artifacts/EXP-428/receipt.json`, 78,616 bytes,
SHA-256 `66cc649b7d885244e7921fc0fa20261f21dd8ed81d24b37edf6e27745bc18a79`.
Compact receipt: [`receipts/EXP-428.json`](receipts/EXP-428.json).

Manifest:
[`../../experiments/manifests/EXP-428-jones-homoclinic-third-second-double-step.json`](../../experiments/manifests/EXP-428-jones-homoclinic-third-second-double-step.json).
