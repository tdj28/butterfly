# EXP-097 — Audit period-640 Floquet precision and representation

Status: preregistered; not executed

Bind the passed EXP-093 wide scan and the failed EXP-096 endpoint-aware
refinement. Recorrect the verified lower endpoint `b=0.17971219`, the EXP-096
center estimate, and the verified upper endpoint `b=0.17971220` under two
frozen solver profiles: the established baseline and a tighter profile with
tenfold smaller tolerances and half the maximum step.

For every corrected orbit, compute the nontrivial multiplier in two ways:

1. the established 64-block cyclic eigenproblem with signed 64th powers; and
2. direct products of the 3-by-3 segment transition matrices at four cyclic
   basepoints.

Run the six independent corrections with three local workers. This uses CPU
parallelism but no GPU or Runpod budget.

The audit passes if all matching residuals are `<=1e-8`, every half-node RMS is
`>=1e-5`, both solver profiles retain a real signed `-1` bracket across the
wide endpoints, block and median direct-product multipliers differ by at most
`1e-4`, and the four cyclic direct products spread by at most `1e-4`.

Passing does not retroactively pass EXP-094 through EXP-096. It decides whether
a tighter augmented event solve can be trusted and identifies which multiplier
representation should define it. Failure routes to a periodic-QR/Schur or
higher-precision implementation before any period-1280 switch.
