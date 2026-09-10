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
