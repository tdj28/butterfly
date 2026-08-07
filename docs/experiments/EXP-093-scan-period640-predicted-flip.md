# EXP-093 — Scan the predicted period-640 flip

Status: executed; passed

Bind the independently qualified EXP-091 period-640 orbit and the prospective
EXP-092 period-640-to-1280 prediction by their full receipt hashes. Continue
one of the two phase-equivalent 64-segment representations through nine frozen
`b` values from `0.17971235` to `0.17971215`, with the densest spacing around
the prediction `b=0.1797121964470`.

At every point, use fixed-parameter multiple-shooting correction and the signed
block-cyclic Floquet calculation already qualified at periods 320 and 640.
Raise each cluster of block roots to the 64th power so the full-orbit
multiplier's sign is retained. Do not infer a flip from its modulus alone.

Pass only if all nine corrections have matching residual `<=1e-8`, all remain
distinct from a half-period representation by node RMS `>=1e-5`, and a real
`-1` crossing is bracketed with width `<=2e-8` and midpoint error `<=5e-8`
from the frozen prediction. The imaginary part at both bracket endpoints must
be `<=1e-6`.

Passing will establish only a prospective period-640 flip bracket. It will not
establish the event at corrected precision or a period-1280 child. Those
require an independently bound event refinement, branch switch, common-
parameter identity comparison, and block-Floquet stability qualification.

The clean run at `7b33167c940d2b02a057b402aba387e60cadd5d9` passed. All
nine matching residuals are below `1.72e-12`, and every orbit stays distinct
from its half-period representation by node RMS at least `2.85e-4`. The real
dominant multiplier changes from `-0.97414250` at `b=0.17971220` to
`-1.04676211` at `b=0.17971219`. The `1e-8` bracket midpoint misses the
prospectively frozen prediction by only `1.447e-9`. Full receipt SHA-256:
`759affdd469eac535c8ea46a7665e8265a7843db011da5dcf9e34ff5191cecc3`.

EXP-094 must bind this bracket and refine the signed `-1` residual before any
period-1280 branch switch is attempted.
