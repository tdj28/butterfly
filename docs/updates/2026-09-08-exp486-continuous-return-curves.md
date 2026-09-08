# EXP-486: continuous return curves, not joined scatter points

The successor to EXP-485 is implemented. This update initially records the
pre-target checkpoint; execution and audit outcomes will be appended below.
No paid review, API call or GPU rental is involved.

The question is whether the two candidate fold regions in each local case
survive on actual curves transported through the flow. The fixed matrix uses
two cases, two regions, two history lengths and two initial curve directions:
16 families, with both DOP853 and Radau at every evaluated point. We integrate
each curve sample continuously, including the changing section-hit time.

The known-fold, no-fold and vertical-projection controls all pass at both
history lengths through the actual grid/refinement path. The 20 focused tests
also pass. Preparation reconstructs all 16 starting curves from authenticated
EXP-485 evidence without running a Rössler target.
The full pre-target suite passes 1,869 tests with one existing Linux-only skip
in 113.29 seconds. The additional read-only auditor uses separately coded
event-time algebra and candidate-bracket reconstruction; its failure-injection
tests check corruption of tangents, eligibility, chronology and residuals.

The prospective [protocol](../experiments/EXP-486-return-image-fold-pilot.md)
fixes the grid, selection, thresholds, resource limits and missingness rules.
All candidate roots are retained, including out-of-region or unresolved roots;
the test cannot select whichever curve happens to match Jones. Candidate
regions were informed by EXP-485, so this is exploratory, not independent
confirmation. Even a positive result would establish only local numerical
fold geometry, not an invariant quotient or a verified historical chain.

## Execution and audit

Pending the exact-source freeze, target run and read-only evidence audit.
The next scientific decision is whether all four depth/direction families
agree in each region. A failed region stays failed; no silent replacement
of the radius, anchor, direction or numerical gate is allowed.
