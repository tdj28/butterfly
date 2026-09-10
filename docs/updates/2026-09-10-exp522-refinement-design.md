# EXP-522 — A fresh nonlinear correction, not a rewritten EXP-521 verdict

Prospective design checkpoint. No EXP-522 target data exists at this checkpoint.
The [protocol](../experiments/EXP-522-nonlinear-contact-refinement.md) uses the
audited EXP-521 endpoint and an explicitly old a derivative to refine contact
at fixed c. Its predicted a is 0.21559338680106457. The old linear c-step
failure remains failed.

The predicted worst full-state residual is about 3.22e-9 versus the actual
parent's 1.82e-6; this forecast must be tested, not taken as a result. New
acceptance requires tenfold improvement for every variant in addition to the
unchanged full-state and prediction gates. First-gap net progress is compared
with the original EXP-519/520 anchor, not the imperfect EXP-521 trial; both
references and the old local progress verdict remain visible.

The source-only adversarial review found no blocking defect. It requested a
synthetic producer-to-auditor round trip, which was added and passed with the
real bounded writer, exact polynomial census, complete accounting and consumed
marker. Synthetic geometry is explicitly substituted only in that test.
All 29 EXP-522 tests pass; a broader parent/new/figure/CI-guard suite passes
106 tests. These are software controls and source review, not independent
scientific confirmation. No paid review was requested.

Manifest SHA-256: `5caf77cfce8c6e3caac3ccd35ad1cbb4279d7d9386407d6958af9ac466bba783`.
The real isolated startup will be repeated at execution. This one-point run
has prospective 256-IVP/3600-second/1.5-GiB limits, with 10-GiB initial free
space and 8-GiB floor. Raw output stays local. Preserve all failures and the
immutable EXP-521 execution ref. No Jones arrow, D or exact critical locus is
claimed by this design checkpoint.
