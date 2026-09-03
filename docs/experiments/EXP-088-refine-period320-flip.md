# EXP-088 — Refine the period-320 flip

Status: executed; failed frozen precision gate

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

The clean run at `44796bfc34fa3a09f33f7b540eab23a754361f8a` failed its
prospective precision gate after all eight allowed trials. Its best event
estimate is `b=0.1797124940088`, only `2.86e-10` from the blind EXP-086
prediction, with matching residual `8.58e-13` and a real multiplier
`-0.999976923`. However, multiplier residual `2.31e-5` exceeds `1e-8`, and
the slope-derived parameter uncertainty `1.48e-11` narrowly exceeds `1e-11`.
Full receipt SHA-256:
`7d184accb97ebf5158408fa824313d3c335cf81737e067ad6713ad18463336e5`.

The retained sign bracket is only `3.44e-10` wide. EXP-089 binds this failed
receipt, reuses its endpoint nodes, and permits six further safeguarded secant
trials with a smaller endpoint margin. No scientific gate is relaxed.
