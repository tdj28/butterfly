# EXP-355 — Crossing predictor warm restart

Status: failed; convergence continues above the gate

EXP-354 lowers the fixed-`c` curve-step defect to `3.83423e-5` while retaining
a large optimizer descent signal and `0.67218` node-boundary margin. EXP-355
binds its exact 127 internal nodes and restarts at the same
`c=10.317135394165936`.

No physical setting, Radau tolerance, segmentation, node-bound radius,
boundary gate, optimization budget, or `1e-8` scientific threshold changes.
Passing qualifies the curve point and its remaining `a-0.1798` offset; exact
fixed `a` must still be solved afterward.

Manifest:
[`../../experiments/manifests/EXP-355-jones-homoclinic-crossing-warm-restart.json`](../../experiments/manifests/EXP-355-jones-homoclinic-crossing-warm-restart.json).

The run is preserved as failed after reducing maximum defect from
`3.83423e-5` to `8.30202e-6`. It moves to
`a=0.1798386480583239`, only `3.86481e-5` above the historical value, and
retains `0.84923` normalized node margin. Nine blocks remain above `1e-8`.

Optimizer optimality remains `9.76e-7`, so the curve correction is still
descending rather than sitting at the fixed-`a` floor. One more exact-node
same-`c` successor is prospectively justified without changing any gate.

Raw receipt: `artifacts/EXP-355/receipt.json`, 32,130 bytes, SHA-256
`78911336ad90fdac0df83828c1fa0712361702ed6788f54c84cd8c811c552964`.
