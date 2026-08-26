# EXP-417 — Twenty-five-point outgoing checkpoint

Status: executed; passed every prospective gate

EXP-416 passes the repeated defect-aware quarter-step. EXP-417 binds the exact
passed EXP-415/416 pair, recomputes the tangent at EXP-416, and repeats
normalized arclength `0.0045986807364392585` with every gate unchanged.

A pass adds the twenty-fifth qualified point and triggers a batched figure,
manuscript, and claim-ledger refresh. It does not establish global
nonintersection, uniqueness, proof, or topology.

## Result

EXP-417 passes every gate in two evaluations:

```text
(a, c) = (0.17981893222630513, 10.317077125910416)
Delta a = +1.6216542014779733e-7
Delta c = -5.174782167216563e-7
signed arclength = 0.0045986807364287
maximum block defect = 3.200228858797601e-9
minimum singular value = 1.1659807652054476e-9
node-boundary margin = 0.991008108621827
```

This adds the twenty-fifth qualified point. The outgoing arm is now reproduced
under eight consecutive newly computed tangents after EXP-408, including two
defect-aware smaller steps. Root and conditioning margins remain intact; its
global fate remains open.

Raw receipt: `artifacts/EXP-417/receipt.json`, 78,550 bytes,
SHA-256 `a855f6406c3b6b4fd3028b92ecbb4be759637c8d967fd2bd77f59346a1d7cd94`.
Compact receipt: [`receipts/EXP-417.json`](receipts/EXP-417.json).

Manifest:
[`../../experiments/manifests/EXP-417-jones-homoclinic-quarterstep-checkpoint.json`](../../experiments/manifests/EXP-417-jones-homoclinic-quarterstep-checkpoint.json).
