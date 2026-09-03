# EXP-415 — Defect-aware conditioned quarter-step

Status: executed; passed every prospective gate

EXP-414 passes but uses `78.5%` of the frozen maximum-block-defect gate.
EXP-415 binds the exact passed EXP-413/414 pair, recomputes the tangent at
EXP-414, and halves normalized arclength to `0.0045986807364392585`. Every
acceptance threshold remains unchanged.

A pass adds a twenty-third qualified point and tests safe progress into the
tighter-defect segment. It does not establish global nonintersection,
uniqueness, proof, or topology.

## Result

EXP-415 passes every gate in two evaluations:

```text
(a, c) = (0.1798186185721344, 10.317078143708969)
Delta a = +1.4103315232327773e-7
Delta c = -4.963160904480901e-7
signed arclength = 0.004598680736431199
maximum block defect = 4.762406069801372e-9
minimum singular value = 1.1812913993560134e-9
node-boundary margin = 0.9909427293101913
```

The defect-aware reduction lowers maximum defect from `7.849e-9` to
`4.762e-9` and halves normalized node displacement. EXP-416 therefore repeats
this step with every threshold unchanged.

Raw receipt: `artifacts/EXP-415/receipt.json`, 78,574 bytes,
SHA-256 `e3b0c84a368206f9192b05796cef1d1473467c48827f7d4d7341924eb93eecd1`.
Compact receipt: [`receipts/EXP-415.json`](receipts/EXP-415.json).

Manifest:
[`../../experiments/manifests/EXP-415-jones-homoclinic-defect-aware-quarterstep.json`](../../experiments/manifests/EXP-415-jones-homoclinic-defect-aware-quarterstep.json).
