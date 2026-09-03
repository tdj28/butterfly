# EXP-098 — Tight-solver period-640 flip refinement

Status: executed; failed frozen multiplier gate

Bind the passed EXP-097 precision/representation audit and the passed EXP-093
seed scan. Use only EXP-097's tighter solver profile and its verified wide sign
bracket `[0.17971219,0.17971220]`. Correct every trial independently from the
nearest retained 64-segment seed and recompute both the block-cyclic and four
cyclic direct-product multiplier representations.

Permit at most eight safeguarded secant trials. Pass only if matching residual
is `<=1e-8`, the block multiplier residual is `<=1e-8` with imaginary part
`<=1e-8`, half-node RMS is `>=1e-5`, slope-derived parameter uncertainty is
`<=1e-11`, and the event remains within `5e-8` of the frozen EXP-092
prediction. At the accepted point, block and median direct-product multipliers
must agree within `1e-8`, and cyclic product spread must be `<=1e-8`.

Passing establishes a precision-audited period-640 `-1` event and resolves the
third prospective prediction at the tighter numerical profile. It still does
not establish supercriticality or a period-1280 child.

The clean run at `46b759ce889b4c76d910b242a24200b3bab7ad81` exhausted all
eight trials and failed only the unchanged pointwise multiplier gate. Its best
estimate `b=0.1797121964322511` is `1.475e-11` from the frozen prediction, with
matching residual `1.27e-12`, parameter uncertainty `1.90e-14`, block/product
difference `3.71e-14`, and cyclic spread `3.55e-15`. The multiplier residual
`1.376e-7` remains above `1e-8`. Full receipt SHA-256:
`661920325aaaad061e52d1739f19fead4090a53ad5bc520cf6a6f293f4bc10b9`.

The trial residuals are monotone on each side. After the endpoint-near positive
trial, the `1%` safeguard forced two midpoint evaluations. The retained signed
bracket is `9.91e-11` wide and the local slope places the root `1.90e-14` from
the upper endpoint, or `0.019%` of the width. EXP-099 binds the exact nodes and
reduces only the numerical endpoint margin to `0.01%`; scientific gates and
the tight solver are unchanged.
