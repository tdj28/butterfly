# EXP-094 — Refine the period-640 flip

Status: preregistered; not executed

Bind the full EXP-093 scan receipt and refine its frozen real `-1` bracket with
a safeguarded secant solve. Every trial independently corrects the 64-segment
period-640 orbit and recomputes the signed block-Floquet multiplier. The
algorithm retains both sign endpoints, every evaluated node set, the local
multiplier slope, and a slope-derived parameter uncertainty.

Pass only if the best correction has matching residual `<=1e-8`, real
multiplier residual `<=1e-8` with imaginary part `<=1e-8`, half-node RMS
`>=1e-5`, estimated `b` uncertainty `<=1e-11`, and absolute error `<=5e-8`
from the prospectively frozen EXP-092 prediction. Permit at most eight trials;
if the gates are narrowly missed, retain the bracket and preregister a bound
resume rather than relaxing any scientific threshold.

Passing establishes a corrected period-640 `-1` event and validates the third
prospective event prediction at refined precision. It does not establish
supercriticality or a period-1280 child. Branch switching and independent
common-parameter identity/stability qualification remain separate experiments.
