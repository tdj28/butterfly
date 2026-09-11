# EXP-525 completed; local replay exposes a portability limit

The approved one-step collection and its automatic raw audit completed on
prax within the combined six-hour cap. No failure record exists in that run.
The original audit and collection receipts, consumed marker, and every frozen
source file were rechecked after completion. The complete new evidence has
also been retrieved into ignored local storage, and its inventory and hashes
match the retained server copy. Nothing was deleted or rerun as a new attempt.

The detailed research evidence remains private. This operational note does
not publish the numerical outcome or claim public data reproducibility. The
earlier EXP-524 publication request remains pending; no alternate package,
derived numerical receipt, or figure is being released to bypass that hold.

## A failed Mac replay is preserved

The new post-run checker, `scripts/verify_exp525_result.py`, authenticates the
completed receipt, source, full raw inventory, historical calibration, and
separately implemented scalar decisions. These local checks pass. Its optional
`--replay-raw` mode additionally invokes the original frozen raw auditor; it
does not implement an independent auditor or run any new trajectories.

That optional full replay **fails on the Mac** at the exact dictionary
comparison in `scripts/audit_exp497_contact_localization.py`, with
`ValueError: fold qualification replay differs`. A logging-only diagnostic
isolated last-bit differences in floating-point normalization quantities in
the first rejected comparison, with no changed Boolean decision there. It
returned the original recomputed values and allowed the same failure to occur;
it did not substitute stored values or relax the comparison. This explains
the first failure, not every later comparison that the failed replay never
reached. The evidence host and laptop also use different Python patch versions.

The correct status is: original authenticated prax raw audit completed;
local byte authentication and scalar replay passed; complete Mac raw replay
failed. Passing software tests do not erase that distinction. All original
frozen code, numerical thresholds, raw files and receipts remain unchanged.
The combined recovery regression suite passes 86 tests. A separate local
adversarial pass found no blocker in the checker or public wording; its own
verification was byte/scalar verification, not a completed Mac raw replay.
A portable replay correction, if pursued, belongs in new versioned analysis
code with explicit numerical-error and unchanged-decision checks, not an edit
to the executed source or a retrospective relabeling of this failure.

## What remains

The approved audit-plus-one-step recovery is complete. No additional target
step is launched under that consumed authority. Jones's flow-level symbolic
chains remain unverified. Further continuation needs a bounded prospective
campaign; successful contact correction alone cannot establish section
grazing, a C/D assignment, or the proposed word-insertion mechanism.

PR 91 was squash-merged into `main` at
`0e3bf2bcfd41ca835a5ff20374a1ad794520bd6f` after all four final-head checks
passed. That merge published implementation and operational documentation,
not the detailed private research results. The immutable execution refs remain
unchanged.
