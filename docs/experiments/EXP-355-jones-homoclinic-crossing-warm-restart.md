# EXP-355 — Crossing predictor warm restart

Status: frozen; not yet run

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
