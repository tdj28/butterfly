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

## EXP-506: one saved-data sensitivity is now checked

The [complete EXP-186 sensitivity](../updates/2026-09-09-exp506-legacy-word-adapter-continuation.md)
replays both profiles, x/z, all five variants and all nominal/bootstrap fits.
The additional derivative-sign and extremum-height filter removes none of the
510 retained-root occurrences; all robust results and eight original word
outcomes are unchanged. Its full audit re-fits 2,040 branch cases and 40
word-slope splines. This clears only this defect's sensitivity for those saved
partitions/words, not EXP-186's other assumptions or the other exposure cases.
The initial EXP-505 adapter failure is preserved. EXP-506 also has an explicitly
reported final-summary output-cap deviation despite passing numerical replay;
it is not labeled wholly protocol-compliant. The shared legacy helper and
historical receipts remain byte-identical.

## 2026-09-09: exposure inventory, not numerical clearance

The checked-in `scripts/inventory_legacy_turning_point_callers.py` now traces
the local helper call chain and explicit imported callers without executing
the old experiments. The [source-bound inventory](receipts/EXP-481-legacy-caller-inventory.json)
retains **21 source scripts** (including the analytic reproducer) and three
test files. Literal manifest-schema matches identify **42 candidate experiment
manifests**, from EXP-106 through EXP-201. These are exposure candidates, not
42 demonstrated mistakes or a complete dynamic dependency graph. Exact-path
mentions in large release inventories likewise do not prove execution.

Both whole-map counting and local critical-point tracking reach the unsafe
helper. The coverage-censored consumer also uses its results even though it
does not call the fitter directly. This means an eventual impact audit must
include nominal fits, bootstrap decisions, robust-variant aggregation and
critical-location use, not only the headline branch counts.

A concrete raw-replay starting point is EXP-186. Its local `receipt.json`
and `states.npz` hashes match the original published anchors in the
[EXP-186 record](EXP-186-heldout-jones-landmark-word.md): respectively
`efae1b0cbee8edf74bf11b6bf3de38c56418c5f8acb454ea3297722d7a836903` and
`f58894f952a40857d29b77f12f959001cb05eaa5a9a5eb2e88d1585ddb295731`.
The current legacy helper and EXP-186 runner are byte-identical to their
versions at original source `877ee75e77bbbd874bbd4311ebd38f8f14e1ed95`.
That establishes available inputs and source identity, **not** numerical
replay or an unchanged verdict. No historical result has been cleared,
reclassified, rerun or erased by this inventory. The shared helper remains
unchanged. Freeze a separate retrospective sensitivity protocol before
comparing its admitted roots with true turning geometry on these saved pairs.
