# EXP-373 — Sparse projected-arclength homoclinic crossing

Status: frozen; not yet run

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
