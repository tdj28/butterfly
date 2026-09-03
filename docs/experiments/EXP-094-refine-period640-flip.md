# EXP-094 — Refine the period-640 flip

Status: executed; failed frozen multiplier gate

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

The clean run at `50ca40ed2a94050fb639eb299d17a84d66ef9eff` exhausted all
eight trials and failed one unchanged gate. The best estimate is
`b=0.1797121964332984`, only `1.370e-11` from the frozen prediction, with
matching residual `1.41e-12` and slope-derived parameter uncertainty
`4.92e-15`. Its real multiplier residual is `-3.57e-8`, however, which exceeds
the required absolute `1e-8`. Full receipt SHA-256:
`a45fecf05fde97a68d35440a40f8c801fea2e97e89494bd4deec436c5bd8c64a`.

The run retains a signed bracket only `6.02e-12` wide. EXP-095 binds these
exact endpoint nodes and permits four further trials with a smaller endpoint
margin. No scientific acceptance threshold is relaxed.
