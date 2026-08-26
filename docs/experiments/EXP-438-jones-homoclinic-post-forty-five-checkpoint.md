# EXP-438 — Conservative post-forty-five-point successor

Status: executed; passed every prospective gate

EXP-437 closes the receipt-bound 45-point checkpoint with its defect at the
persistent numerical floor. EXP-438 binds the exact passed EXP-436/437
receipts, recomputes the tangent at EXP-437, and holds normalized arclength at
`0.0045986807364392585`. Every acceptance threshold remains unchanged.

A pass adds the forty-sixth qualified point. A failure is preserved. Neither
outcome establishes global nonintersection, uniqueness, proof, or topology.

## Result

EXP-438 passes every gate in two evaluations:

```text
(a, c) = (0.17982821641321917, 10.317048591871762)
Delta a = +5.461627484437681e-7
Delta c = -1.677680433687101e-6
signed arclength = 0.004598680736419322
maximum block defect = 3.200001701010852e-9
minimum singular value = 9.61337113286038e-10
node-boundary margin = 0.9920964792867579
```

Raw receipt: `artifacts/EXP-438/receipt.json`, 78,620 bytes,
SHA-256 `81bbf32721c6f45763e9c60a7e3c3d4186fc5c19437b18f9ec80346b9714adc2`.
Compact receipt: [`receipts/EXP-438.json`](receipts/EXP-438.json).

Manifest:
[`../../experiments/manifests/EXP-438-jones-homoclinic-post-forty-five-checkpoint.json`](../../experiments/manifests/EXP-438-jones-homoclinic-post-forty-five-checkpoint.json).
