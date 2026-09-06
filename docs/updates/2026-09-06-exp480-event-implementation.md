# EXP-480: event-transport implementation, targets still locked

The first part of the [historical-section successor](../experiments/EXP-480-historical-section-successor-design.md)
now has a draft runtime, machine manifest, tests and a decision-level
[review brief](../reviews/EXP-480-design-review-brief.md).

Implemented checks include both sections on a common trajectory, full raw
plane/extremum event retention, independent correction under four solver
profiles, fixed-window recurrence and ordered cross-profile comparisons,
crossing/ambiguity margins, and failure/source/data integrity gates.
The numerical choices are proposals for review, not a completed scientific
freeze. No partition, historical letter, source word, or chain arrow is tested.

Sixteen focused tests pass. They use an analytic circular oscillator and
synthetic failures only; both actual DOP853 and Radau event integrators are
exercised. Tests caught an array-serialization issue during implementation,
which was corrected before any target call. The full local suite passes
**1,327 tests with one Linux-only skip**. No nominated Rössler trajectory,
target fit, or word was generated in this work.

The real execute CLI rejects the draft before opening target inputs or
calling a solver. Activation requires an adjudicated review bound to the
design, actual raw review receipt and numerical/runtime dependency files,
followed by a clean pushed source freeze. A Boolean status change alone
cannot satisfy that gate. Review has not yet been obtained; the review brief
must not be presented as an independent review or execution authorization.

The complete EXP-479 archive remains independently verified on prax and all
local originals are preserved. The unresolved provider transaction still
has no assigned ID or exact matching inventory name. Its separate watchdog
remains live; no paid create or unrelated resource mutation occurred.
