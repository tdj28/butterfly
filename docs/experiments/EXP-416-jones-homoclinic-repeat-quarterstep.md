# EXP-416 — Repeated defect-aware quarter-step

Status: executed; passed every prospective gate

EXP-415 restores root-defect margin at normalized arclength
`0.0045986807364392585`. EXP-416 binds the exact passed EXP-414/415 pair,
recomputes the tangent at EXP-415, and repeats that step with every gate
unchanged.

A pass adds a twenty-fourth qualified point. It does not establish global
nonintersection, uniqueness, proof, or topology.

## Result

EXP-416 passes every gate in two evaluations:

```text
(a, c) = (0.17981877006088498, 10.317077643388632)
Delta a = +1.514887505715823e-7
Delta c = -5.003203362718978e-7
signed arclength = 0.004598680736440682
maximum block defect = 3.200240553035763e-9
minimum singular value = 1.1736418831754682e-9
node-boundary margin = 0.9909748927302928
```

The repeated smaller step lowers maximum defect to the persistent
`3.20e-9` floor and adds the twenty-fourth qualified point. EXP-417 freezes
one more identical-gate quarter-step for a 25-point checkpoint.

Raw receipt: `artifacts/EXP-416/receipt.json`, 78,616 bytes,
SHA-256 `8aa7ad2226240acdf646713c6f51415465be86c70de0e60f9363b6e87d4c857c`.
Compact receipt: [`receipts/EXP-416.json`](receipts/EXP-416.json).

Manifest:
[`../../experiments/manifests/EXP-416-jones-homoclinic-repeat-quarterstep.json`](../../experiments/manifests/EXP-416-jones-homoclinic-repeat-quarterstep.json).
