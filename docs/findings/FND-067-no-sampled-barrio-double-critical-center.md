# FND-067 — No sampled Barrio double-critical center

Status: qualified finite-sample rejection and prospective localization

EXP-197 applies the qualified positive-x Barrio-section CUDA path to all 58
corrected stable representatives of the isolated second period-6 component.
Both RK4 steps complete without numerical failures. They resolve 31 and 32
robust three-branch maps, with 31 candidates retaining the same distinct phase
assignment and passing all critical-location and survivor-count parity gates.

No cross-step candidate places both assigned orbit phases inside the two
critical intervals. No candidate passes the assigned zero-slope ceiling. The
nearest candidate, `component-sample-059` at
`(a,b,c)=(0.21555,0.2,7.372)`, has a maximum normalized midpoint distance of
`0.04963`, interval distance `0.03603`, and zero-slope residual `1.894` under
frozen ceilings `0.05`, `0.02`, and `0.2`. One of its phases matches the first
critical with a slope residual near `0.044`; the second assigned phase is
outside its critical interval and is not stationary.

This rejects direct double-critical membership at the sampled corrected
orbits. It neither rejects Barrio-Blesa-Serrano double superstability nor shows
that a center exists between samples. Because the target and all thresholds
were frozen before execution, the closest point is a legitimate prospective
localization for a dense, coupled signed-residual refinement.

Evidence: [`../experiments/EXP-197-barrio-z-two-critical-scan.md`](../experiments/EXP-197-barrio-z-two-critical-scan.md).
