# EXP-166 passes; EXP-167 period-8 qualification frozen

Date: 2026-08-07

EXP-166 passes the local period-8 branch switch in both tangent signs. The
smallest shooting singular value is `2.89e-12`; the primary and secondary
tangents are orthogonal to printed precision. Both arms contain 32 points,
remain at least `0.0558` from the interpolated doubled period-4 parent, retain
half-period nonclosure, and end locally stable.

EXP-167 is frozen at the common interior point `c=4.65`. DOP853 and independent
Radau corrections must identify the two arms as one phase-shifted primitive
period-8 orbit, verify period-4-to-period-8 stability exchange, period ratio
two, windings four and eight, and recovery after 96 perturbed child periods.
The fixed thresholds are loosened only in proportion to the doubled orbit
length and remain far tighter than the expected branch separation.
