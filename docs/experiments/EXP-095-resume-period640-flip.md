# EXP-095 — Resume the period-640 flip refinement

Status: preregistered; not executed

Bind EXP-094's failed full receipt and resume from its retained signed bracket,
reusing the exact 64-segment endpoint nodes. The bracket width is
`6.02e-12`. Permit at most four additional safeguarded secant trials and reduce
the endpoint margin from `5%` to `1%`; this changes only the numerical search
inside the already localized bracket.

All scientific gates remain unchanged: matching residual `<=1e-8`, real
multiplier residual `<=1e-8`, imaginary part `<=1e-8`, half-node RMS
`>=1e-5`, slope-derived `b` uncertainty `<=1e-11`, and absolute error from
the frozen EXP-092 prediction `<=5e-8`.

Passing will establish the corrected period-640 `-1` event. A period-1280
child and supercriticality remain unclaimed until separate branch-switch and
identity/stability experiments pass.
