# FND-081 — A standard section counter loses crossings near the refined grazing

Status: qualified negative method result; continuous grazing remains nominated

EXP-213 refines a sign change in the continuous grazing residual to a
`6.58e-11` `c` bracket. DOP853 and Radau agree on the orbit, flip event,
clearance, gate coincidence, and large nonzero curvature. Nevertheless the
frozen experiment fails because the standard section event collector reports
six historical crossings on both final sides.

Farther below the same root, the collector reports seven. As the maximum
approaches the section plane, its two neighboring roots coalesce; an adaptive
step may span both without a sign change and report neither. The integer count
therefore becomes numerically discontinuous before the continuous geometric
event. This is a method failure, not contrary evidence against the grazing.

EXP-214 must partition the period at every `y` extremum and bracket roots on
each monotone interval. Only cross-solver agreement of that count can promote
the grazing claim.

Evidence:
[`../experiments/EXP-213-period6-flip-section-grazing.md`](../experiments/EXP-213-period6-flip-section-grazing.md).
