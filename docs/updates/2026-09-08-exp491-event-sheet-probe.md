# EXP-491: screening the full candidate intervals

## Live calculation

The full 156-trajectory local run started at **2026-09-09 04:28:29 UTC**
(September 8 local time). It is not another proposal-only checkpoint.
The frozen source was pushed and its exact live remote hash verified before
execution: `4c8ec515a80f2ac591cf819fb314a643345b756e`.

The calculation retains all 26 original intervals, both endpoint samples and
their midpoint, both solvers and all 16 finite-return curve families. It is
checking event-time continuity and input-coordinate conditioning; it does
not repeat EXP-490's Newton searches. Three samples are a screen, not proof
of a continuous branch. No symbolic letters or words are being inferred
from an incomplete run.

All 48 analytic control profiles passed the preflight and separate numerical
audit. The complete test suite passed **1,960 tests**, with one Linux-specific
skip. The new uncertain-extremum adjacency regression changes none of the
72 preserved EXP-490 census results. Full details are in the
[prospective protocol](../experiments/EXP-491-event-sheet-probe.md) and
[preflight record](../experiments/EXP-491-preflight.md).

Raw output is retained locally under `artifacts/EXP-491/target-4c8ec51`.
The exclusive marker must not be reset or reused. Monitoring during the run
is limited to completion and operational validity; final counts will be
reported only after the complete matrix and raw inventory are audited.
No paid review, GPU rental, API request or new upload is being used.

Next in this same execution: complete the run, audit all trajectories and
decisions, publish the all-family scatter figure with source hashes, and
update the claim ledger and next steps. Jones's flow-level symbolic chains
remain unverified; the purpose is to resolve the geometry needed to test
them, not lower the standard for calling them verified.
