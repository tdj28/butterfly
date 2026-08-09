# EXP-162 passes; EXP-163 period-4 qualification frozen

Date: 2026-08-07

EXP-162 passes the local branch-switch gates in both nullspace signs. The
smallest shooting singular value is `1.18e-13`, while the primary/secondary
tangent dot product is `5.55e-17`. Both arms contain 32 corrected points.
Their endpoints are `0.0917` and `0.1005` from the interpolated doubled
period-2 parent, have half-period nonclosures `0.2390` and `0.2951`, and have
dominant multiplier moduli `0.9427` and `0.9120`.

EXP-163 is frozen at the common interior value `c=4.318`. Independent Radau
correction must show that the two switch arms are one phase-shifted primitive
period-4 orbit, the period-2 parent is unstable while the period-4 child is
stable, the period ratio is two, the windings are two and four respectively,
and a perturbed state recovers the same child. This is the same qualification
logic used for EXP-158, applied to the second cascade rung.
