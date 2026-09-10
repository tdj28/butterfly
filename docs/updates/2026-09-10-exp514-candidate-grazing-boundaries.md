# EXP-514: distinguish section grazing from projected folds

## Current scientific status

The five failed EXP-513 fold searches are not evidence of root absence.
Read-only diagnostics of the saved EXP-512 endpoints and EXP-513 midpoints
identify a concrete alternative: **each surviving sign-change half contains
one aligned extremum changing sides of the section plane**. Both solvers agree
on the extremum ordinal and the preceding accepted-return count.

| Direction | Original nodes | Extremum index (zero based) | Accepted returns before candidate |
| --- | --- | ---: | ---: |
| 0 | [1,2] | 3 | 1 |
| 0 | [15,16] | 11 | 5 |
| 0 | [16,17] | 19 | 8 |
| 1 | [17,18] | 11 | 5 |
| 1 | [18,19] | 19 | 8 |

These are **nominations from old observations**, not new integrated roots or
grazing certificates. The derivation is checked in, preserves all five cases,
and rejects ambiguous alignment instead of selecting a favorable extremum.

## Next test, now in pre-target validation

The [EXP-514 protocol](../experiments/EXP-514-candidate-grazing-boundaries.md)
directly solves the section-tangency equations and then tests the two-sided
birth/death of crossings at four signed offsets. It reuses the validated
grazing equations and thresholds from EXP-492, but retains every new side's
full dense census, guard mesh and all accepted returns over the EXP-513 horizon.
The new controller and audit are implemented; validation precedes the freeze
and any target integration.

This refines the previously proposed event-aware search: there is already
enough endpoint evidence to nominate the grazing equation directly. It does
**not** claim to implement safeguarded bisection. Its Newton step is bounded;
an out-of-box proposal remains a retained failure, not a reason to enlarge the
box. No root, fold, Jones symbol or arrow is yet established by this test.

Local analytic positive/negative controls exercise the combined producer.
The prospective cap is 160 target IVPs, 3,600 seconds and 2 GiB including the
summary. No paid review, new worker or raw upload is requested. All earlier
failed attempts, frozen sources and raw products remain intact.

## Preserved pre-target checks

EXP-513 merged normally through PR #79 at
`e678aff6d477dc4d43f00eeb98047db41c792270` after all four final-head CI jobs
passed. EXP-514 continues on a new branch from that main commit.

All 12 initial target-free tests passed. The real combined analytic control
producer then passed **24 integrations**, retaining every mesh and side
census in `artifacts/EXP-514/preflight-controls-01`.

The first isolated consumer failed because the source allowlist omitted the
EXP-492 numerical manifest read by the new plan builder. The failed isolated
tree remains intact. The missing manifest is now explicitly included, with a
regression assertion. No target was accessed or attempt marker consumed. The
obsolete full-suite run was deliberately interrupted after 941 passing tests;
its partial XML is preserved and is **not** claimed as a complete pass.
The corrected **159-file isolated consumer passes**, with its complete receipt
in `artifacts/EXP-514/preflight-startup-02.json`. The final pre-target full suite
passes **2,700 tests, one Linux-only skip**, in 481.14 seconds
(`preflight-suite-02.xml`). The staged public scan passes on 2,915 files;
manuscript citation/figure checks and the symbolic control table also pass.

The local design audit distinguishes a tangency of the chosen section from
a smooth projected-map critical point. It requires all four signed side inputs
at a common paired-root center and the full-horizon event comparison, retains
all five intervals, and forbids promoting a qualified tangency to an absence
claim about other folds. The changed nomination equation is disclosed rather
than described as a rerun of EXP-513. This is a same-agent local audit, not an
external or paid review. The source is ready for the pre-target Git freeze.
