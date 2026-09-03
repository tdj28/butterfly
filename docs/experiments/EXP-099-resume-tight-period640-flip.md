# EXP-099 — Endpoint-aware tight period-640 flip resume

Status: executed; failed and closed scalar refinement

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

The clean run at `51fb11ca9acd11716b5507091c676252b5aacee8` failed the
unchanged multiplier gate after all three trials. Its best tight-solver point
is `b=0.17971219643223532`, `1.476e-11` from the frozen prediction. Matching
residual is `1.42e-12`, parameter uncertainty is `3.92e-16`, block/product
difference is `8.74e-14`, and cyclic product spread is `4.00e-15`. The real
multiplier residual `1.697e-8` remains above the required `1e-8`. Full receipt
SHA-256:
`1d14204e6227fee99d8dec32c8208b185cd76ec35e39bba28c9f3b6260ad2015`.

The retained signed bracket is `3.22e-15` wide. This is strong evidence for an
event location but does not pass the preregistered pointwise equality. No more
scalar resumes are permitted. The next implementation follows DEC-003: solve
the orbit, parameter, and transported anti-periodic eigenvector together, and
validate that formulation first at the resolved 320→640 event.
