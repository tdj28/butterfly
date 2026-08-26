# EXP-418 — Defect-aware outgoing successor

Status: executed; passed every prospective gate

EXP-417 completes the 25-point checkpoint with comfortable root and
conditioning margins. EXP-418 binds the exact passed EXP-416/417 pair,
recomputes the tangent at EXP-417, and repeats normalized arclength
`0.0045986807364392585` with every gate unchanged.

A pass adds the twenty-sixth qualified point. It does not establish global
nonintersection, uniqueness, proof, or topology.

## Result

EXP-418 passes every gate in two evaluations:

```text
(a, c) = (0.17981910528146058, 10.317076583680448)
Delta a = +1.730551554557369e-7
Delta c = -5.422299675927889e-7
signed arclength = 0.004598680736433097
maximum block defect = 3.200218810992994e-9
minimum singular value = 1.1583095842162112e-9
node-boundary margin = 0.9910424155413295
```

The twenty-sixth point preserves the `3.20e-9` defect floor and more than
twice the conditioning gate. EXP-419 prospectively doubles arclength while
leaving every acceptance threshold unchanged.

Raw receipt: `artifacts/EXP-418/receipt.json`, 78,531 bytes,
SHA-256 `a6eb1d24bec7a97c3ac9f759ee54e109c353251e1f35f8fe72ee6731d0862b7e`.
Compact receipt: [`receipts/EXP-418.json`](receipts/EXP-418.json).

Manifest:
[`../../experiments/manifests/EXP-418-jones-homoclinic-quarterstep-successor.json`](../../experiments/manifests/EXP-418-jones-homoclinic-quarterstep-successor.json).
