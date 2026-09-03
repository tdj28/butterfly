# EXP-373 — Sparse projected-arclength homoclinic crossing

Status: completed; failed prospectively frozen matching and termination gates

EXP-371 and EXP-372 converge to the same residual floor despite a fourfold
widening of the nuisance departure-angle range. EXP-373 retains their
qualified sources, 512-arc representation, full-state predictor, physical
`(a,c)` closing plane, desired `c` increment, bounds, 40-evaluation budget,
and every scientific acceptance gate.

Two numerical choices are prospectively changed. The analytic multiple-
shooting Jacobian is exposed as CSR and solved by regularized LSMR, exploiting
its block-bidiagonal structure. The closing equation's residual weight changes
from `0.01` to `1.0`; its zero set and the unchanged `1e-8` unweighted
arclength gate are identical, but the optimizer can no longer trade a large
plane error cheaply against matching defects.

A pass below `a=0.1798` forms a qualified branch bracket. It does not itself
solve the exact historical section or establish uniqueness or computer-
assisted existence.

Manifest:
[`../../experiments/manifests/EXP-373-jones-homoclinic-sparse-projected-arclength.json`](../../experiments/manifests/EXP-373-jones-homoclinic-sparse-projected-arclength.json).

## Result

EXP-373 reaches the 40-evaluation cap at
`(a,c)=(0.1798218288661,10.3173007208813)`. The unweighted projected
arclength residual is `-3.85232e-9`, a four-order improvement over EXP-372
and inside the unchanged `1e-8` gate. The maximum matching defect remains
`1.1374390009342667e-5`, however, so the root and termination checks fail.
All source, initial-residual, finite-state, direction, node-bound, global-bound,
flight-time, and evaluation-budget checks pass.

The sparse formulation therefore repairs continuation-plane enforcement but
does not qualify the orbit match at the requested step. The next prospective
attempt halves the desired `c` increment to `7.5e-5`. That is still large
enough for the qualified local secant to cross `a=0.1798`, while reducing the
nonlinear correction distance; no acceptance threshold changes.

Raw receipt: `artifacts/EXP-373/receipt.json`, 85,628 bytes, SHA-256
`04acc23d368304f9d6938ee28e67c7bc265bb13c9f0c23798d3f971a6e8ec874`.
