# EXP-095 — Resume the period-640 flip refinement

Status: executed; failed unchanged multiplier gate

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

The clean run at `2ab64ea18ff2e6139d78041191ce3b151ae173fe` exhausted its
four trials and failed the same multiplier gate. The prior best real residual
`-3.57e-8` remains the closest to zero. The four new positive residuals decrease
monotonically from `2.20e-5` to `2.85e-6`, while matching residuals stay below
`1.40e-12`. Full receipt SHA-256:
`aea5b7734bbfa78a66ec0edce6ffb2e14fff79bd5d3c77395ea697fdae0dbf89`.

This pattern does not show a Floquet noise floor. The root lies close enough to
the negative endpoint that the frozen `1%` endpoint safeguard selected four
midpoints instead of the secant point. The retained bracket is now
`3.77e-13` wide. EXP-096 binds it and reduces only the numerical endpoint
margin to `0.1%`; all acceptance gates remain fixed.
