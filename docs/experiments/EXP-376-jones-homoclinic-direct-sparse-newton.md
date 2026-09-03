# EXP-376 — Direct sparse-Newton homoclinic correction

Status: completed; direct Newton step rejected by frozen backtracking gate

EXP-375 proves that the CSR/LSMR trust-region least-squares formulation has
reached a stationary non-root on the reduced crossing plane. EXP-376 binds
that receipt by SHA-256 and retains the qualified EXP-367/368 branch sources,
exact 512-node iterate, physical plane, common gauge, integration/manifold
settings, source-centered bounds, and every scientific acceptance threshold.

The optimizer changes class. Each square analytic Jacobian is column-scaled
by the frozen pseudo-arclength variable scales, converted to CSC, and factored
directly by SuperLU. Newton steps are restricted to `0.99` of the nearest
bound and must pass an Armijo decrease test under factor-two backtracking. A
step smaller than `2^-12` is rejected, and the complete budget is 24 function
evaluations. This allows motion along the nearly null direction that LSMR
regularization suppressed without accepting a residual-increasing jump.

A pass below `a=0.1798` forms a qualified branch bracket. It does not itself
solve the exact historical section or establish uniqueness or computer-
assisted existence.

Manifest:
[`../../experiments/manifests/EXP-376-jones-homoclinic-direct-sparse-newton.json`](../../experiments/manifests/EXP-376-jones-homoclinic-direct-sparse-newton.json).

## Result

Sparse LU solves the scaled linear system to residual `2.57761e-13`, but the
near-null Newton step has scaled norm `1522.68` and maximum component
`799.347`. The nearest source-centered bound limits the first trial to
`5.41071e-4` of the step. That trial increases maximum defect from
`5.20888e-6` to `7.17314e-3`; halving again gives `1.78406e-3`. The next
halving lies below the prospectively frozen `2^-12` floor, so the step is
rejected after three function evaluations and the initial state is preserved.

The direct factorization is accurate; the obstruction is nonlinear curvature
along an enormous near-null step. One successor may lower only the line-search
floor to measure whether the guaranteed infinitesimal Newton descent is
numerically accessible. If it is not, further restarts are rejected in favor
of a better-conditioned boundary formulation or finer segmentation.

Raw receipt: `artifacts/EXP-376/receipt.json`, 78,605 bytes, SHA-256
`5cf1726acf35b04ad32f7cda305d5170be3685a20df54e1fa900e6e099cf57c9`.
