# EXP-096 — Endpoint-aware period-640 flip resume

Status: preregistered; not executed

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
