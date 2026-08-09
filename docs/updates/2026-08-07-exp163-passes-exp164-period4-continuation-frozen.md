# EXP-163 passes; EXP-164 period-4 continuation frozen

Date: 2026-08-07

At the untouched common checkpoint `c=4.318`, EXP-163 independently qualifies
the second cascade child. Radau gives the unstable period-2 parent multiplier
`-1.0115948996` and stable period-4 child multiplier `0.9535193007`. The two
switch arms agree up to phase with RMS `3.14e-7`; their period ratios are
`2.000002`, half-period closures exceed `0.2148`, and their windings are four.
A 96-period perturbed integration recovers the same child to RMS `2.83e-9`.

EXP-164 is frozen before execution. It seeds pseudo-arclength continuation
from the last two points of the positive EXP-162 arm, enforces period-4
half-period nonclosure and four windings, independently checks DOP853/Radau
whole-orbit identity every 20 points, and stops only after bracketing the first
real `-1` multiplier crossing plus four successor points. The claim is only an
identity-safe bracket; an exact period-4-to-8 event and period-8 child remain
separate gates.
