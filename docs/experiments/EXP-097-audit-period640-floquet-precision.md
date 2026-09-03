# EXP-097 — Audit period-640 Floquet precision and representation

Status: executed; passed

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

The exact committed command initially encountered the managed sandbox's OS
semaphore restriction before any orbit evaluation. It was relaunched unchanged
with local worker-process permission. The clean run at
`9df1176523fd0a304a1e540393567df22323c058` then passed.

Both profiles retain the wide signed bracket. At the lower, center, and upper
points, baseline multipliers are `-1.0467621112`, `-1.0000000360`, and
`-0.9741424959`; tight multipliers are `-1.0467544130`, `-0.9999922862`, and
`-0.9741348646`. The center shift is `7.750e-6`. Block-cyclic and median
direct-product multipliers differ by at most `5.83e-14`, while changing among
four cyclic basepoints produces spread at most `6.00e-15`. Matching residuals
remain below `1.47e-12`. Full receipt SHA-256:
`b479121f727a78d657b726a7b74c10689edbca7d1bc5d697bee3f6398462efdc`.

The representation is therefore not the limiting factor. Integration accuracy
shifts the pointwise event at approximately the `1e-12` parameter scale.
EXP-098 binds this audit and refines the event using only the tight solver on
the wide bracket.
