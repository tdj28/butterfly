# FND-088 — The returning-child path recrosses the known flip arm

Status: corrected by EXP-229; the former second-boundary interpretation is
retracted

EXP-223 tracks the closest-to-event stable primitive period-12 child through
212 accepted points, 45 exact returning-arm events, and `c=7.62518642` without
relaxing closure, stability, period-ratio, proper-subperiod, two-section
identity, or branch-coherence gates. DOP853/Radau controls pass at the near
slice and source-event index 25.

The full route to the middle slice is rejected. Inside the narrow next bracket
`c=[7.62518642,7.62541565]`, the lower-offset period-6 parent changes from
unstable to stable and correction of the nominal child collapses onto the
parent traversed twice. This differs qualitatively from EXP-221's jump to a
distant primitive unstable root.

The result narrows the returning-arm picture: local opposing-side child
opening persists over a substantial sampled interval, but not to the frozen
middle slice at this fixed event-relative offset. EXP-225 independently
refines the implied parent real-`-1` crossing to
`c=7.62537829761` (DOP853) and `7.62537829365` (Radau), a `3.96e-9`
difference. EXP-226 then passes the complete bilateral audit: a primitive
stable child before the root and, after it, a stable parent whose DOP853 and
Radau `2T` traversals satisfy closure, doubled section counts, state identity,
and monodromy squaring.

EXP-229 changes the interpretation, not these orbit calculations. Fresh
fixed-`c` correction from EXP-217 source-arm seeds reproduces all 21 EXP-227
events with maximum `a` difference `1.46e-14`, state difference `4.77e-11`,
and sign-invariant tangent difference `4.04e-12`. The supposed
`5.60e-7--5.85e-7` separation is exactly the error from linearly interpolating
the curved EXP-217 arm.

The fixed offset path therefore recrosses the already-qualified returning
flip arm; it does not discover a second boundary. The child and bilateral
stability calculations still demonstrate the expected primitive-child versus
parent-double-cover exchange across that known flip locus. They do not close a
child sheet, pair shrimp boundaries, identify the TBA, or locate a
double-critical center.

Evidence: [`../experiments/EXP-223-returning-period12-child-adaptive.md`](../experiments/EXP-223-returning-period12-child-adaptive.md)
and [`../experiments/EXP-226-returning-child-strip-endpoint.md`](../experiments/EXP-226-returning-child-strip-endpoint.md).
Corrective evidence:
[`../experiments/EXP-229-exp227-exact-source-identity.md`](../experiments/EXP-229-exp227-exact-source-identity.md).
