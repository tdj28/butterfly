# EXP-159 period-2 continuation frozen

Date: 2026-08-07

EXP-159 continues the primitive stable period-2 child from EXP-157 on the fixed
`(a,b)=(0.1798,0.2)` Jones path. A frozen 142-point grid covers
`c=3.1845..6.0` and stops four accepted points after the first real `-1`
bracket.

Every accepted row must retain periodic closure, neutral Floquet identity,
failure of half-period closure, and winding two. Radau checkpoints require
whole-orbit and multiplier agreement with DOP853. A bracket is accepted only
when the dominant multiplier is real within `1e-6` and its `lambda+1`
residual changes sign.

Passing supplies a bracket for an exact coupled period-2-to-4 event solve. It
does not itself establish the exact event, a switched period-4 child, later
ordering, or the homoclinic endpoint.
