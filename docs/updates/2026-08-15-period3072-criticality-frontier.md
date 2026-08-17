# Period-3072 criticality frontier

Date: 2026-08-15

## Secure position before this sequence

Eight primitive returning-arm real-`-1` events are independently qualified.
Six births are independently supercritical, and the deepest stable child has
primitive period 768. EXP-309 nominates exact primitive period-3072 children;
EXP-310 independently finds the selected child strongly unstable but leaves
the parent inside the unchanged `1e-4` neutral margin.

## EXP-311: four-step continuation

All four full pseudo-arclength corrections and every orbit/identity gate pass.
The daughter grows distinctly primitive but bends across the finite event
coordinate, ending only `7.77e-13` away. The frozen `1e-11` separation gate
therefore fails. This preserves an exact prefix without classifying terminal
stability.

## EXP-312: receipt-bound resumption

Six additional exact rows pass before matching at the frozen minimum step
reaches `1.00429e-8 > 1e-8`. Terminal orbit and exact `3584/4096` identity
gates pass, but the nine-row and `1e-11` gates fail. The first row beyond
`4e-12` is selected deterministically without reading a multiplier.

## EXP-313: first separated two-solver audit

The independent DOP853/Radau audit passes every nonclassification gate. Parent
moduli are `1.0023029158/1.0023672000`; child moduli are
`22667.8828618/22667.8901561`. Both families are therefore unstable, and the
frozen stability-exchange gate fails. This is a robust local geometry result:
the exact daughter branch has curved to the parent-unstable side and becomes
extremely unstable.

## Implication for Jones

Nothing here rejects the returning-arm cascade or hub organization. Event
eight and primitive period-3072 existence are strengthened. What remains open
is the local eighth-birth direction. Parameter distance from the finite RK4
event representation is no longer an adequate proxy for the common
coexistence side at this resolution.

## Next executable gate

Localize the period-1536 real-`-1` parent event separately under the exact
DOP853 and Radau flow representations, using fixed-a correction and signed
dominant multiplier brackets. Bind both coordinates and their discrepancy.
Only then switch or sample the period-3072 daughter on a coordinate that both
solvers place on the same parent-stability side. Keep the `1e-4`
classification margin and all orbit/identity gates unchanged.

## EXP-314: solver-specific parent-event brackets

One new parent-only endpoint per solver passes after 1,810 seconds. DOP853
brackets real `-1` over width `5.9544e-13`; Radau brackets it over
`5.9827e-13`, on the opposite side of the shared EXP-310 coordinate. Both
outward residuals exceed `1e-4` and all numerical gates pass. The EXP-310
neutral classification is therefore explained by solver-specific event
coordinates straddling its sampled `a`, not physical multistability. EXP-315
is frozen for two deterministic bisections of each bracket before any new
period-3072 switch.

## EXP-315: event-scale refinement

Both two-step solver-specific bisections pass. DOP853 ends with width
`1.48853e-13`; Radau ends with width `1.49575e-13`. The intervals are disjoint
by `1.49575e-13`, while all midpoint corrections and independent orbit/Floquet
checks pass. This converts the earlier qualitative solver split into a bounded
event-coordinate uncertainty.

The scientific conclusion is deliberately narrow: there is no evidence here
for physical multistability or two bifurcations. Instead, at period 1536 the
two adaptive flow representations place the numerical real-`-1` event a few
`1e-13` apart. A common absolute `a` coordinate cannot securely put both
solvers on the same side with the unchanged `1e-4` margin.

The next executable gate is an event-relative child switch. For each solver,
correct the parent from its own bracket, generate the anti-periodic daughter,
and evaluate parent and child at an identical signed offset measured from that
solver's event. Only cross-solver agreement in those relative coordinates can
resolve the eighth birth direction.
