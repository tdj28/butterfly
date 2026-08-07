# EXP-098 — Tight-solver period-640 flip refinement

Status: preregistered; not executed

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
