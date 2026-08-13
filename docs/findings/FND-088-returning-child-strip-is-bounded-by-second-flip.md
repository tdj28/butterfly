# FND-088 — A second flip bounds the sampled returning-child strip

Status: numerically qualified on one frozen parameter path

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

This establishes a second flip boundary of the sampled child strip along one
precisely defined path. It materially strengthens the interpretation of the
returning-arm geometry as organized shrimp anatomy. It does not yet prove that
the child sheet ends globally, that the new crossing continues as a curve and
connects to either broad arm, that those arms bound one shrimp, or that any of
these sets coincide with the TBA or a double-critical center.

Evidence: [`../experiments/EXP-223-returning-period12-child-adaptive.md`](../experiments/EXP-223-returning-period12-child-adaptive.md)
and [`../experiments/EXP-226-returning-child-strip-endpoint.md`](../experiments/EXP-226-returning-child-strip-endpoint.md).
