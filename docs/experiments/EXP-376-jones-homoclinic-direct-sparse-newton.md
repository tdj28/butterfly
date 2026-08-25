# EXP-376 — Direct sparse-Newton homoclinic correction

Status: frozen; not yet run

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
