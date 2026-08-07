# EXP-096 — Endpoint-aware period-640 flip resume

Status: executed; failed and closed scalar-resume path

Bind the failed EXP-095 receipt and its exact `3.77e-13` signed bracket. The
four EXP-095 trial residuals decrease monotonically, but its `1%` endpoint
safeguard repeatedly selected bracket midpoints because the secant root lies
near the negative endpoint. Permit at most three additional trials and reduce
only the numerical minimum endpoint fraction to `0.1%`.

No scientific gate changes: matching residual `<=1e-8`, real multiplier
residual `<=1e-8`, imaginary part `<=1e-8`, half-node RMS `>=1e-5`,
slope-derived `b` uncertainty `<=1e-11`, and absolute error from the frozen
EXP-092 prediction `<=5e-8`.

Passing will establish the corrected period-640 `-1` event but not a
period-1280 child. Failure with nonmonotone or irreducible multiplier residuals
will trigger a precision/segmentation audit rather than another blind resume.

The clean run at `88440bc1bc3961ca9c22bc9290f400461b72f0fc` failed the
unchanged multiplier gate after three endpoint-aware trials. Its best
`b=0.1797121964332993` is `1.370e-11` from the blind prediction, with matching
residual `1.40e-12` and slope-derived uncertainty `8.89e-17`; the real
multiplier residual remains `-3.60e-8`. Full receipt SHA-256:
`e4765a1531057934a060c6f6c29adf45f00d99b667b12385a793b6f38d4aa50e`.

The final reported sign interval is only `7.22e-16` wide. At this scale,
neighboring corrections change the multiplier by more than its `1e-8` gate,
so further scalar secant trials with the same integration and block-eigenvalue
representation are not justified. EXP-097 must audit solver precision and
representation stability on a much wider, already verified sign bracket.
