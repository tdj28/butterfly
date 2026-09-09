# EXP-492: directly locating the sixteen event boundaries

## Live execution checkpoint

The complete sixteen-candidate run was launched from frozen source
`919f16f1846d145ff14ad1da35e3fb516cd1e849`, verified against the live remote
before execution. The same source is preserved on
`codex/exp492-local-execution`. Raw output is local at
`artifacts/EXP-492/target-919f16f`; it is not a public raw-data release.

This follows through on EXP-491's unresolved intervals, not a new search for
favorable examples. All sixteen nominations and the ten unselected prior
intervals remain in the ledger. The question is whether the nominated extrema
actually become tangencies that create/remove a crossing pair. A positive
answer identifies boundaries of a section-event description; it does not
yet identify Jones's C/D symbols or prove an insertion arrow.

Before launch, all 48 analytic control IVPs and their separate exact-event
audit passed; 34 focused tests and the full 2,007-test suite passed, with one
Linux-only skip. The input reconstruction was byte-identical. See the
[frozen protocol](../experiments/EXP-492-event-boundaries.md) and
[preflight](../experiments/EXP-492-preflight.md).

The runner repeats the analytic controls, then consumes its exclusive target
marker and executes every candidate with both solvers and the prescribed
two-sided matrix when the root gate permits it. It retains failures without
retrying or replacing a candidate. Only operational completion is monitored
until the complete outcome matrix is audited.

No new paid service, Pro review or upload is involved. The next actions in
this execution are the full raw-data audit, an all-candidate geometry figure,
and a documented scientific interpretation before merging the result.
