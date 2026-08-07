# EXP-099 — Endpoint-aware tight period-640 flip resume

Status: preregistered; not executed

Bind EXP-098's failed full receipt and reuse its exact tight-solver endpoint
nodes. The retained signed bracket is `9.91e-11` wide, and the local slope
places the root `1.90e-14` below the upper endpoint (`0.019%` of the width).
Permit at most three trials and reduce only the numerical endpoint margin from
`1%` to `0.01%` so that the indicated secant point is admissible.

The tight solver and every scientific gate are unchanged: matching and real
multiplier residuals `<=1e-8`, imaginary part `<=1e-8`, half-node RMS
`>=1e-5`, parameter uncertainty `<=1e-11`, prediction error `<=5e-8`, and
block/product difference and cyclic product spread each `<=1e-8`.

Passing establishes the corrected period-640 `-1` event but not a period-1280
child. Failure closes tight scalar refinement and retains only the signed
bracket claim.
