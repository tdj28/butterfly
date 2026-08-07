# EXP-089 — Resume the period-320 flip refinement

Status: executed; passed

Bind EXP-088's failed receipt and resume directly from its retained
`3.44e-10` sign bracket, reusing the exact segmented endpoint nodes. Permit at
most six further safeguarded secant trials and reduce the minimum endpoint
margin from `5%` to `1%`, which is appropriate after the root was localized
near the upper endpoint.

All scientific gates are unchanged: matching residual `<=1e-8`, real
multiplier residual `<=1e-8`, imaginary part `<=1e-8`, half-node RMS
`>=1e-5`, slope-derived `b` uncertainty `<=1e-11`, and absolute error from
the blind EXP-086 prediction `<=5e-8`.

The clean run at `0ca4463164f343e2a01a4953f10595260203b87a` passed. The
resolved event is `b=0.17971249399392974`; its dominant nontrivial multiplier
is `-0.9999999924978`, matching residual is `7.32e-13`, and slope-derived
parameter uncertainty is `4.82e-15`. The event misses the prospectively frozen
EXP-086 prediction by only `3.00e-10`, or `0.0216%` of the newly observed
spacing. Full receipt SHA-256:
`663aa90f447d7bb13c04dd04984cf441c03b0b17c3b8e246afb45da296a40dc2`.

The observed 160→320 to 320→640 spacing ratio is `4.6681920`. EXP-090 now
freezes a 64-segment branch switch; period 640 is not claimed until a distinct
child and subsequent independent qualification pass.
