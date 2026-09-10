# EXP-520 release — integrate the tested interpreter guard

The original EXP-520 release head
`9fdfd2125fc754af9fc56a372b8f688880bafe36` had three successful checks and
one failed Python 3.12 PR job. The failure was the EXP-518 isolated-consumer
startup at its unchanged 240-second limit; 2982 other tests passed. The job
used Ubuntu's system Python 3.12.3. This failure is preserved, not rerun
blindly and not described as a failed EXP-520 numerical census.

Main commit `b9c10e1f8652ccc5ed9cd5619946dbe863883c2d` now carries the
managed-Python environment requirement and explicit interpreter-origin check
that passed all four final-head checks on PR85. Integrate that main commit
normally, retaining both EXP-519 and EXP-520 results, figures and narrow SVG
whitespace exceptions. No frozen numerical source, threshold, old failure or
execution ref changes. The new final head still requires every push/PR check
before normal merge; success at another head is not a substitute.

## Reconciliation with the EXP-521/522 releases

On 2026-09-10, integrate main through `02a64bc` in a separate release
worktree, leaving the live EXP-523 checkout on prax untouched. Retain all
EXP-520 census findings, all four experiment-specific SVG exceptions, and
the newer EXP-521 failure and EXP-522 refinement result. The update index
now identifies EXP-522, rather than EXP-519, as the latest audited result.
No later result retroactively changes the EXP-520 claim boundary.

The focused census, figure, interpreter and conditional-grazing tests pass
(64 passed; the unchanged empirical figure redraw was deselected). Paper
reference checks pass. A separate read-only adversarial review found no
content blocker in the four conflict resolutions. These are release checks,
not new integrations or independent verification of Jones's chain.
