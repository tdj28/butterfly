# EXP-035 — Full unit-event pseudo-arclength below a=0.235

Status: preregistered; pending clean local execution
Manifest: `experiments/manifests/EXP-035-event-pseudo-arclength.json`
Claim target: lower-`a` continuation boundary in EXP-034

## Hypothesis and method

The period-5 nontrivial-unit event continues past the fixed-`a` corrector
failure near `a=0.2325`. Treat state, period, `a`, `b`, and the event
eigenvector as nine unknowns. Couple flow closure, phase, `(M-I)q=0`, vector
normalization, flow orthogonality, and a secant pseudo-arclength condition in
one overdetermined corrector.

Use only the accepted EXP-034 events at `a=0.2375` and `0.235` as seeds, with
consistent eigenvector sign. Freeze a constant step equal to one half of their
nine-dimensional secant norm and attempt thirty downward-oriented steps. The
corrector may pass through an `a` turn; neither `a` nor `b` is fixed.

## Acceptance and limits

At least twelve new corrected points are required, with at least one reaching
`a <= 0.232`. Closure, eigen, flow-orthogonality, and arclength residuals must
each stay below `1e-8`, inside the declared `a` and `b` guards.

Passing demonstrates that the natural-continuation failure was a projection or
seeding problem and resolves the curve beyond it. It does not prove global
continuation, establish the same pitchfork normal form along the curve, or
construct the two-dimensional event surface under changes in `c`.
