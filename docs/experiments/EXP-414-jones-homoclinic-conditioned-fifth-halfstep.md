# EXP-414 — Fifth conditioned outgoing half-step

Status: executed; passed every prospective gate

EXP-413 passes a fourth consecutive conditioned half-step. EXP-414 binds the
exact passed EXP-412/413 pair, recomputes the tangent at EXP-413, and repeats
normalized arclength `0.009197361472878517` with every gate unchanged.

A pass adds a twenty-second qualified point. A root-gate or conditioning
failure instead triggers a smaller-step successor without weakening either
threshold. Neither outcome establishes global nonintersection, uniqueness,
proof, or topology.

## Result

EXP-414 passes every gate in two evaluations:

```text
(a, c) = (0.17981847753898209, 10.31707864002506)
Delta a = +2.506010024494465e-7
Delta c = -7.457800510479728e-7
signed arclength = 0.009197361472863274
maximum block defect = 7.84906626882835e-9
minimum singular value = 1.188885174276799e-9
node-boundary margin = 0.9817613967751271
```

The twenty-second qualified point continues the outgoing arm. Its maximum
defect uses `78.5%` of the frozen root gate, so EXP-415 halves step size while
leaving every acceptance threshold unchanged.

Raw receipt: `artifacts/EXP-414/receipt.json`, 78,541 bytes,
SHA-256 `2745e7f42e74888d8d5136d8ee186656b2a606c80932e06479e0ee7601c608bb`.
Compact receipt: [`receipts/EXP-414.json`](receipts/EXP-414.json).

Manifest:
[`../../experiments/manifests/EXP-414-jones-homoclinic-conditioned-fifth-halfstep.json`](../../experiments/manifests/EXP-414-jones-homoclinic-conditioned-fifth-halfstep.json).
