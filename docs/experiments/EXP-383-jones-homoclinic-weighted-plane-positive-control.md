# EXP-383 — Weighted-plane multiple-shooting positive control

Status: completed; passed weighted-plane positive control

EXP-382 rejects unconstrained collocation even at the qualified EXP-368 root.
EXP-371--377 show that the pure physical `(a,c)` plane is nearly singular,
whereas EXP-369 shows that the unweighted full-state plane can select a
wrong-direction root.  EXP-383 returns to the bounded analytic-variational
multiple-shooting representation and tests a prospectively weighted hybrid.

The closing-plane weights are fixed before execution:

```text
nodes = 0.01
total flight time = 0.01
a = 1
c = 1
angle = 0.01
```

With the EXP-367/368 secant and existing variable scales, this makes the
physical `(a,c)` direction dominant while retaining a small full-state
component to regularize the measured near-null mode.  The predictor step is
exactly zero.  Deterministic subdivision converts the two 256-arc sources to
512 arcs, and the result must reproduce EXP-368 without moving `c` by more
than `1e-8`.

Manifest:
[`../../experiments/manifests/EXP-383-jones-homoclinic-weighted-plane-positive-control.json`](../../experiments/manifests/EXP-383-jones-homoclinic-weighted-plane-positive-control.json).

## Result

EXP-383 passes all ten frozen checks in three evaluations.  It reduces the
maximum matching-block defect from `9.999341446e-9` after deterministic
subdivision to `5.108875696e-9`, with arclength residual `-1.85489e-13`.
The corrected `c` coordinate moves only `1.68723e-9`, well inside the
stationary `1e-8` control gate, and the node-boundary margin is `0.999728`.

The measured closing tangent has group norms `a=0.54299`, `c=0.83394`,
`nodes=0.06995`, `angle=0.06936`, and `time=0.000618`.  The smallest analytic
Jacobian singular value is `1.79318e-9`, versus `2.70368e-10` for the failed
pure physical-plane solve.  The weak full-state term therefore regularizes the
measured near-null mode without allowing nuisance variables to dominate.

This pass licenses the prospectively frozen EXP-384 forward crossing step.  It
does not itself qualify the exact historical-section intersection.

Raw receipt: `artifacts/EXP-383/receipt.json`, 78,223 bytes, SHA-256
`22dd98d870e099a8fb8f3d11f9a5e45b41641ec4163641a3d5f5062b5d773d8c`.
