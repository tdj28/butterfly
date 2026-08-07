# EXP-050 — Identity-constrained period-5 continuation

Status: preregistered after EXP-049; pending clean execution

Restart from the independently verified EXP-022 period-5 orbit at
`(a,b,c)=(0.245,0.2,5.1)`. Continue at fixed `(a,c)` with a secant predictor,
but accept a corrected orbit only when one closed traversal has exactly five
legacy-section intersections. Wrong-family roots force step halving and remain
in the receipt.

Pass requires ten accepted points, at least two in each direction, closures
below `1e-8`, identity 5 everywhere, and at least one recorded rejected
wrong-family trial. Reaching either wide parameter guard is not required;
identity-safe termination is evidence about the branch's accessible extent.
