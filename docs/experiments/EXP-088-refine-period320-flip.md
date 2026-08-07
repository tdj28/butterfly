# EXP-088 — Refine the period-320 flip

Status: preregistered after EXP-087; pending clean execution

Refine EXP-087's frozen real `-1` bracket with a safeguarded secant solve. Each
evaluation independently corrects the 32-segment orbit and recomputes the
signed block-Floquet multiplier. Retain the sign bracket, all trial nodes, and
the local multiplier slope. Estimate parameter uncertainty as multiplier
residual divided by that slope.

Pass only if matching residual is `<=1e-8`, real multiplier residual is
`<=1e-8` with imaginary part `<=1e-8`, half-orbit node RMS remains `>=1e-5`,
estimated `b` uncertainty is `<=1e-11`, and the resolved event lies within
`5e-8` of the prospectively frozen EXP-086 prediction. Passing verifies the
prediction and establishes a period-320 `-1` event; period 640 remains a
separate branch-switch and qualification claim.
