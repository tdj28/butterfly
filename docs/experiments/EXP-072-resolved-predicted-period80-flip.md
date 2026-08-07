# EXP-072 — Resolve the predicted period-80 flip

Status: preregistered after EXP-071; pending clean execution

Repeat only the final EXP-071 bracket using `rtol=2e-13`, `atol=2e-15`,
`max_step=0.015`, and bisection tolerance `1e-13`. Require bracket width
`<=2e-13`, multiplier residual `<=5e-9`, real multiplier, closure `<=1e-9`,
and half-period closure `>=0.001`.

The manifest preserves the original EXP-066 prediction. Passing will support
the fifth event parameter and permit the third spacing ratio and prospective
prediction error to enter the finding; it still will not prove universality or
the period-160 child.
