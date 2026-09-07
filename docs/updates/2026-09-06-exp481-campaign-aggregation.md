# EXP-481: both-case campaign analysis is wired

The campaign-level analysis now composes the existing cohort, map and
critical-proximity components. It cannot report only the better of the two
declared cases. This is software validation, not new evidence about Jones's
symbolic chains.

The preceding durability checkpoint is merged into `main` at
`851d15ceb114c6236501b1098f98989148b74606` (PR #40); all four Python 3.12/3.13
CI checks passed.

## What changed

`python/butterfly/paired_campaign.py` reconstructs the committed seed table and
enumerates **512 collection batches** and **128 qualification trials** before
outcomes exist. Every original ID appears once in each collection case/profile.
Each declared qualification seed has both RK4 and both adaptive profiles.
Enumeration does not launch a solver or authorize execution.

The analysis wrapper checks both cases' complete ordered batch grids, source
and plan binding fields, original IDs, initial coordinates, fixed split,
physical windows, pair shapes and population counts before fitting either
case. It then runs the existing primary and diagnostic analyses separately
for both cases. Missing or substituted inputs raise an error. An unresolved
scientific result is retained, with overall primary support false; good
diagnostics cannot rescue it.

All six historical reference states are retained in source order, including
misses and unsupported points. When the primary gate passes, all six x values
reach every primary model's critical-region comparison. No reference phase is
selected to improve agreement. A successful scalar-map assessment still does
not verify an alphabet, a symbolic arrow or a topological theorem.

## Validation and limits

The full local suite passes **1,519 tests**, with one older Linux-only skip on
macOS. All **25 new campaign tests** pass. The suite was run with the host
access needed for the existing live process-loss and supervision controls.

The new tests use analytic cubic-map arrays, not Rössler trajectories. They
exercise both complete cases, all six rows against all 20 primary models per
case, missing/substituted second-case data, incorrect batch membership and an
unresolved second case with successful diagnostics. The two scientific
outcomes remain visible separately. Test controls use eight bootstrap
replicates for speed; the unchanged research proposal requires 200.

This is an **in-memory composition**, not an authenticated data loader. The
production caller must supply complete externally bound journal replay and
independently verified reference rows. Matching hashes written into a Python
dictionary do not establish source authority. Canonical environment/import
closure, real startup attestation, the complete production CLI and compact
adjudicated review are still required before new target computation.

No target trajectory, paid review, GPU rental or remote upload was performed
for this checkpoint. The proposal remains unreviewed and execution-disabled.
The research-integrity playbook influences this implementation through fixed
case/batch accounting and retention of unresolved outcomes, rather than
best-case selection. The next implementation step is the authenticated
production entry point, using these components without rebuilding them.
