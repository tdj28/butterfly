# FND-108 — Jones homoclinic mechanism qualifies at a revised coordinate

Status: qualified numerical finding; bounded uniqueness and rigorous proof open

At fixed `(b,c)=(0.2,10.3084)`, a 16-arc DOP853 boundary-value solve first
nominates an equilibrium homoclinic connection. Independent 32-arc Radau
shooting reproduces the root, and Radau corrections persist when the nonlinear
stable-manifold matching sphere shrinks from radius `0.03` to `0.025` and
`0.02`.

Across the qualified roots, `a` remains near `0.182643608174`; the two smaller
radii differ from their sources by `1.30e-13` and `4.34e-13`. Maximum arc
defects are `1.08861e-9`, `5.49708e-9`, and `5.60724e-9`. Preserved failures
EXP-343 and EXP-345 show that departure angle is a nearly null nuisance gauge:
it drifts to prospective boundaries while `a` and the manifold match remain
stable. Exact-node successors EXP-344 and EXP-346 validate the roots without
further optimization under corrected gauges.

## Consequence for Jones

The proposed saddle-focus homoclinic organizing mechanism receives strong
modern numerical support. The printed point does not: at the printed
`c=10.3084`, the qualified root is about `0.00284361` above `a=0.1798`, far
beyond four-decimal rounding. The natural next test is to continue the
homoclinic curve in `(a,c)` and determine whether it crosses the historical
fixed-`a=0.1798` path near the earlier scan minimum around `c=10.319`.

Two qualified local continuation steps now sharpen that test. EXP-347 passes
at `(a,c)=(0.1819925796550,10.3104)`, and EXP-350 passes at
`(0.1806904556213,10.3144)`. Their successive secant slopes are
`-0.3255142594` and `-0.3255310084`, predicting the historical-path
intersection near `c=10.3171354`. This agreement supports a smooth local root
curve but does not replace the required direct intersection solve.

## Limits

This is not a computer-assisted existence proof and does not establish a
unique root on any declared parameter segment. Direct long initial-value
replay diverges because the orbit is extremely unstable; the qualified object
is the matched boundary-value solution. Continuation, an explicit phase/gauge
condition, and eventually validated numerics remain required.

Evidence: EXP-341 through EXP-347 and EXP-350 with their hash-bound compact
receipts.
