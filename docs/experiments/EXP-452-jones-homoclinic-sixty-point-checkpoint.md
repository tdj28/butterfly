# EXP-452 — Sixty-point homoclinic checkpoint attempt

Status: executed; passed every prospective gate

EXP-451 passes at the defect floor, but its minimum singular value is only
`1.75x` the fixed conditioning floor. EXP-452 therefore binds the exact passed
EXP-450/451 receipts, recomputes the tangent at EXP-451, and holds normalized
arclength at `0.0045986807364392585`. Every acceptance threshold is unchanged.

A pass adds the sixtieth qualified point and triggers a receipt-bound figure
and manuscript refresh. A failure is preserved. Neither outcome establishes
global nonintersection, uniqueness, proof, or topology.

## Result

EXP-452 passes every gate in two evaluations:

```text
(a, c) = (0.17983793557436534, 10.317018739937058)
Delta a = +8.311690079254586e-7
Delta c = -2.553045373332452e-6
signed arclength = 0.004598680736420661
maximum block defect = 3.199918306056248e-9
minimum singular value = 8.701342755625068e-10
node-boundary margin = 0.993239973092436
```

Raw receipt: `artifacts/EXP-452/receipt.json`, 78,678 bytes,
SHA-256 `283f2a12a1b3a8b400b23cfbf88e14c5df9249b64d5b5d42c1a85e856fb66275`.
Compact receipt: [`receipts/EXP-452.json`](receipts/EXP-452.json).

Manifest:
[`../../experiments/manifests/EXP-452-jones-homoclinic-sixty-point-checkpoint.json`](../../experiments/manifests/EXP-452-jones-homoclinic-sixty-point-checkpoint.json).
