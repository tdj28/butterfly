# FND-088 — The sampled returning-child strip ends at a double-cover candidate

Status: broad sampled strip qualified; terminal real-`-1` root independently
localized, final representation-safe double-cover control pending

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
middle slice at this fixed event-relative offset. EXP-224 must independently
refine the implied real-`-1` crossing and verify primitive child versus
double-cover behavior bilaterally before the endpoint is called a qualified
second flip boundary. Nothing here yet proves global child-sheet termination,
paired shrimp boundaries, TBA membership, or double-criticality.

EXP-225 independently refines the implied parent real-`-1` crossing to
`c=7.62537829761` (DOP853) and `7.62537829365` (Radau), a `3.96e-9`
difference. Its primitive left child and DOP853 right double cover pass. The
only remaining gate is a representation-safe Radau double-cover audit;
redundant `2T` Newton correction is singular at the object being tested.

Evidence:
[`../experiments/EXP-223-returning-period12-child-adaptive.md`](../experiments/EXP-223-returning-period12-child-adaptive.md).
