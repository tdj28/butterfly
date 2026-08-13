# FND-079 — A period-12 child sheet is qualified over a dense period-6 flip patch

Status: qualified on the prospectively frozen 31-by-4 grid

EXP-211 independently interpolates the three EXP-209 child families to all 124
cells above the EXP-206 period-6 flip curve. Every cell converges directly to a
primitive stable period-12 child; none uses the declared fallback. This repairs
EXP-210's root-selection pathology without erasing its 16 documented
double-covered-parent collapses or relaxing any scientific gate.

All 31 fixed-`c` opening fits give exponent `0.502636--0.503088` with minimum
`R^2=0.99999696`. Adjacent child orbits agree to RMS `0.005020`. Every parent
is unstable, every child stable, all section counts are exactly 6/8 versus
12/16, and every proper subperiod is rejected. The multiplier ratio remains
in `4.01176--4.12635`, while six Radau controls reproduce DOP853 to maximum
whole-orbit RMS `1.314e-8`.

This is strong orbit-level support for Jones's period-doubling organization:
the previously sampled flip edge now has a dense, regular sampled child sheet
with replicated supercritical scaling. It is not yet a theorem of continuity,
a global endpoint continuation, a TBA identification, or evidence that either
critical point belongs to these cycles.

Evidence:
[`../experiments/EXP-211-period12-surface-recovery.md`](../experiments/EXP-211-period12-surface-recovery.md).
