# EXP-157 — Local period-2 switch from the first fixed-path flip

Status: passed frozen local branch-switch gates

## Question

Does the exact period-1 flip from EXP-156 possess a nontrivial local doubled
branch when the fixed `(a,b)=(0.1798,0.2)` path is continued in `c`?

## Frozen method

The EXP-156 parent orbit is represented as a double cover. At a period-doubling
event its closure-plus-phase shooting Jacobian has a two-dimensional
nullspace. The observed doubled-parent tangent from EXP-155 is projected into
that nullspace and removed; the remaining transverse direction seeds the two
signs of the prospective child branch.

Adaptive DOP853 integrates the state, variational equations, and exact
`c`-sensitivity `f_c=(0,0,-z)`. Newton-style least squares only corrects the
finite-dimensional closure, phase, and pseudo-arclength residuals. Centered
finite-difference tests validate the sensitivity and shooting Jacobian.

## Result

The smallest shooting singular value is `5.840844773053272e-15`, and the
absolute parent/child tangent dot product is `5.551115123125783e-17`. Both
transverse signs yield 24 accepted points. Their endpoint distances from the
doubled parent are `0.0794546` and `0.0686120`; half-period closure errors are
`0.2278273` and `0.2041713`. Endpoint dominant nontrivial moduli are
`0.9880594` and `0.9904612`.

## Interpretation boundary

This establishes a nontrivial local doubled branch. The two signs may be
phase-shifted representations of the same orbit, and the stability exchange
still requires an independent solver. EXP-158 tests those claims.

Tracked receipt: `docs/experiments/receipts/EXP-157.json`.
