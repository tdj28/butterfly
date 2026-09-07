# EXP-480: review complete, numerical gaps repaired before target execution

One GPT-6 Astra Pro design review completed, at a conservative reported cost
of **$0.58094**. The exact response and packet are retained in
[the review bundle](../reviews/EXP-480-review-01/review.md). The reviewer found
two material gaps: uncertainty at the historical half-plane gate, and missing
end-to-end calibration of the anisotropic correction/event accuracy budget.

Both are repaired before observing either target. Every raw plane root now
retains its signed gate distance; ambiguous membership and weak orientation
prevent qualification, including potentially excluded roots. The real shooting
corrector plus all four solver profiles passes an analytic attracting-cycle
test at the declared coordinate scales. The expanded focused suite passes
23 tests, including deliberately adverse geometry and failure cases.
The full local suite passes **1,334 tests**, with one unrelated Linux-only
process-identity test skipped on macOS.

[The adjudication](../reviews/EXP-480-adjudication.md) addresses every review
finding, narrows the endpoint to paired-section event reproducibility, records
casewise outcomes and fixes the operator stopping policy. The original review
packet is preserved unchanged; the reviewer did not inspect the later fixes.
The manifest binds the actual review and amended runtime. Execution still
requires the clean pushed source and exact input checks.

This qualifies a numerical prerequisite only. It does not verify a partition,
critical letter, Jones word, chain arrow, or cross-section correspondence.
Both nominations remain fixed. The next survivor study must control not just
capture selection but also the different weighting caused by unequal numbers
of section returns per trajectory.

Operationally, the API client first rejected broad `.env` permissions before
making a request; owner-only permissions now protect that file. The earlier
Runpod transaction remains separately watched, with no exact owned match and
no new worker created. No target trajectory has been generated at this
pre-execution checkpoint.
