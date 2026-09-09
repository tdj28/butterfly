# EXP-505: check one historical result for the known turning-point defect

## Recorded implementation failure; continued prospectively as EXP-506

EXP-505 stopped after retaining the first profile/x/original population's
255 branch fits. The new replay adapter omitted four fields that the historical
runner adds after `_word_row`: target comparisons, cyclic matches, reversal-only
matches and membership status. Comparing the incomplete row with the complete
old receipt therefore failed. This was an implementation defect in the new
audit, not a changed historical scientific conclusion.

Frozen source: `04771d80f973b60a39a187f382db8d773a32c089`.
Failure SHA-256:
`f025767950859ec7846dbaea96a4374fac4137a0989e429332bfcabf2cc7b29c`.
The entire partial fit population and original source/input/marker inventories
remain local under artifacts/EXP-505/target-04771d8. The marker is consumed;
no filtered target fit ran and no restart or favorable-prefix selection is allowed.

[EXP-506](2026-09-09-exp506-legacy-word-adapter-continuation.md) separately
freezes the schema completion and exact-prefix reuse. Before any remaining
target fits, all 255 retained fit results reconstructed the original robust
partition within unchanged tolerances, without constructing another spline.
The adapter also reproduced all eight complete stored word schemas. That
confirms the diagnosed omission rather than treating a numerical mismatch as
a reason to loosen a threshold. EXP-186 is not yet cleared by this failed run.

## Pre-target validation history

The [prospective retrospective protocol](../experiments/EXP-505-legacy-turning-point-impact.md)
now specifies a complete saved-data sensitivity for EXP-186: both integration
profiles, x and z, five oracle variants, every nominal/bootstrap fit, and all
eight stored-input word rows. No new trajectory is needed. This work does not
change EXP-504's frozen numerical sources or its rejected continuation result.

The old manifest, raw receipt, state archive, return-map helper and landmark
runner were hash checked. Their recorded identities agree. No new target fit
has been interpreted. The analytic controls distinguish stationary inflections
from true extrema, and a separate pair constructor matches the production
constructor on shuffled synthetic records.

The first 12 controls passed, and an authentic isolated copied-source consumer
passed with zero target fits/integrations and an 80-path source/input closure.
The full repository suite passed 2,446 tests with one Linux-only skip in
175.79 seconds (artifacts/EXP-504/release-suite-01.xml). A pre-freeze local audit
then tightened bookkeeping: every fit invocation now records its sample hash
and result, including fits rejected before a spline or any roots exist. A new
control explicitly exercises that case. This changes retention, not fitting or
scientific thresholds. Focused tests and isolated startup must pass again
before the target re-fit is started from a clean live-pushed freeze.

That final pre-target check passed: **66 focused tests in 4.73 seconds** and
the isolated startup passed again with zero target fits/integrations. The
machine-plan SHA-256 is
`374eb53e0949c8310d70d2b6851985acbcf91234c33b3184b23ba9a5c88ddc84`.

No paid model review, rental, raw upload, package change or evidence deletion
is used. The original EXP-186 result is already known to fail its parity/word
gates; this is explicitly a retrospective helper sensitivity, not a new
held-out symbolic test. An unchanged result would clear only this defect's
effect on these saved partitions/words, not every old assumption or the other
41 candidate manifests in the exposure inventory.
