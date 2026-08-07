# EXP-089 — Resume the period-320 flip refinement

Status: preregistered after EXP-088; pending clean execution

Bind EXP-088's failed receipt and resume directly from its retained
`3.44e-10` sign bracket, reusing the exact segmented endpoint nodes. Permit at
most six further safeguarded secant trials and reduce the minimum endpoint
margin from `5%` to `1%`, which is appropriate after the root was localized
near the upper endpoint.

All scientific gates are unchanged: matching residual `<=1e-8`, real
multiplier residual `<=1e-8`, imaginary part `<=1e-8`, half-node RMS
`>=1e-5`, slope-derived `b` uncertainty `<=1e-11`, and absolute error from
the blind EXP-086 prediction `<=5e-8`.
