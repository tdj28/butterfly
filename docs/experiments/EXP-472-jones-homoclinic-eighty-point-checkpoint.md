# EXP-472 — Eighty-point homoclinic checkpoint attempt

Status: executed; passed every prospective gate

EXP-471 passes at the defect floor, but its minimum singular value is only
`1.61x` the fixed conditioning floor. EXP-472 therefore binds the exact passed
EXP-470/471 receipts, recomputes the tangent at EXP-471, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the eightieth qualified point and triggers a receipt-bound figure
and manuscript refresh. A failure is preserved. Neither outcome establishes
global nonintersection, uniqueness, proof, or topology.

## Result

EXP-472 passes every gate in two evaluations:

```text
(a, c) = (0.17985928422847947, 10.316953156190541)
Delta a = +1.2743516392688115e-6
Delta c = -3.915141725485682e-6
signed arclength = 0.004598680736496077
maximum block defect = 3.19975131291399e-9
minimum singular value = 8.01872542256545e-10
node-boundary margin = 0.9938611038487002
```

Raw receipt: `artifacts/EXP-472/receipt.json`, 78,637 bytes,
SHA-256 `a94d266fe99dca283811fa20d6406cbc9d26c739310f1745088a1849baa33fce`.
Compact receipt: [`receipts/EXP-472.json`](receipts/EXP-472.json).

The receipt-bound 80-point continuation figure was regenerated from clean
commit `449b727271d8d008b7bac11dd4fcebc6508610d6` and passed full-resolution
visual inspection. Its image SHA-256 is
`247664c311b957db2154ac24ab11286aee1089265d48826b379df23da7886f9b`;
the figure-receipt SHA-256 is
`cb5bf1005d8bc5bc661a1b1115bf1b445316588fc111c38b696354e1e3d91b2c`.

The manuscript was rebuilt from clean figure commit
`8afbbc5fa703e2cedc9681f0b187a92bf29724d4`. The resulting 55-page,
10,185,564-byte PDF has SHA-256
`dd9c0154ed8af98871fdcdb1870064e84a18fc9dcd6d15789fbd68cdf7c52171`.
The build log has no undefined citations or references and no overfull or
underfull boxes. Rendered pages 1, 11, 49, 50, and 55 passed visual inspection.

Manifest:
[`../../experiments/manifests/EXP-472-jones-homoclinic-eighty-point-checkpoint.json`](../../experiments/manifests/EXP-472-jones-homoclinic-eighty-point-checkpoint.json).
