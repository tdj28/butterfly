# Pre-outcome incident: a stationary inflection can become a legacy branch boundary

Discovered 2026-09-06 while implementing EXP-481's seed-level analyzer.
No new nominated Rössler trajectory was generated or fitted. This is a concrete
analytic-helper defect, not evidence that Jones's construction is false or
that a specific historical Rössler receipt is wrong.

## Reproducer

`scripts/check_legacy_stationary_inflection.py` calls the existing
`return_map._critical_points` on the exact function `(x-0.5)^3` and its exact
derivative `3*(x-0.5)^2`, on `[0,1]` with 4,097 grid points and prominence 0.03.
The function is monotone: its derivative never changes sign. The legacy helper
nevertheless reports `[0.5]` as a branch-dividing critical point. See the
[source-bound reproducer receipt](receipts/EXP-481-legacy-stationary-inflection.json).

A stationary inflection is a derivative-zero point in the calculus sense, but
is not an extremum separating increasing/decreasing return-map branches. The
legacy helper admits an exactly zero grid derivative, then accepts large
absolute height differences on either side without checking that the point is
above both adjacent landmarks or below both. Its downstream `count+1` branch
interpretation is therefore unsafe in this case.

## Change and scope

The new `seed_return_map.py` requires opposite derivative signs near a proposed
turn and same-sign height differences to both adjacent landmarks, as well as
the predeclared prominence/support tests. Synthetic cubic extrema remain
resolved, and the stationary-inflection control has one branch in every
nominal variant. The final full-size smoke has 1.0 count consensus for that
control in all five variants; the preceding preserved smoke ranged from 0.935
to 0.975 before the same-sign height check. No acceptance threshold was lowered.

The earlier `return_map.py`, its frozen execution sources and historical raw
results are intentionally unchanged in this EXP-481 implementation branch.
No prior numerical result is silently recomputed or reclassified. Existing
EXP-479 nominations remain the declared conditional inputs, not certificates
of exact criticality; EXP-480's event-reproducibility result does not rely on
this branch-count helper.

## Follow-up required

Before relying on earlier critical-count claims in a new manuscript release,
audit which reported results call this helper and whether their reported roots
actually have the required sign/turn geometry. This is a separate, explicitly
post-run sensitivity/correction using preserved raw data and frozen historical
source—not a reason to rerun old collection, alter its inputs or delete its
negative evidence. Report unchanged and changed outcomes alike. If a fix is
made to the shared helper, use a separate reviewed correction commit with the
analytic regression and an impact ledger. Do not claim the historical results
are cleared merely because the new EXP-481 analyzer passes its controls.
