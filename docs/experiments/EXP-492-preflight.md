# EXP-492 preflight

2026-09-08 local date; before the target marker exists.

The complete outcome-informed input ledger retains 26 prior intervals, with
16 boundary nominations in 10 families. Its 64 full endpoint reports are
anchored through the independently reconstructed EXP-491 completed summary,
not just mutually consistent new hashes. Rebuilding from the retained old run
produced the exact input SHA-256
`9377b422f1321d1b811f59a2b477bf72bee5e58bb4272decb60e040746cf86da`.
No new target trajectory was used to select or tune these inputs.

All five real analytic conditions passed in both solvers: prefixes 0, 1 and 8,
no root in the frozen box, and a transverse crossing. The 48 control IVPs
produced `artifacts/EXP-492/preflight-controls-01/controls.json`, SHA-256
`a38d08c3fbad0ab121eca4fbf6d4e9cb20bc56de54be27adcbb370a33f957c04`.
The read-only control audit independently checked the exact grazing locations
and every accepted analytic event time, including expected negative-failure
reasons. After that control run, a before-IVP resource callback was added;
its default is a no-op and its refusal path has a regression test. Production
repeats all controls with the frozen source before consuming the target marker.

All 34 focused tests pass. They cover immutable historical reconstruction,
self-consistent tampering, numerical settings, independent polynomial
Jacobians for all realized prefix counts, real Newton shooting in both
solvers, hard search boxes, retained failed IVPs, before-IVP resource refusal,
common side inputs, complete matrices, empty legitimate event lists, paired
time/state/count failures, earlier and bracket-adjacent uncertain extrema,
wrong prefix counts, and failed square-root scaling.

Full suite: **2,007 passed, one platform-specific skip in 132.25 seconds**
(`.venv/bin/python -m pytest -q`). The skip needs Linux `/proc`; this host is
macOS. The complete target-independent controls also passed their separate
arithmetic audit. No target marker existed at this checkpoint.

Approximately 26 GiB free space was observed. The runner enforces the frozen
16 GiB initial reserve, 8 GiB floor/output cap, 384-target cap and 7,200-second
whole-run deadline. The existing-CPU workload heuristic is 5,714.682309 s at
the maximum target count, leaving room for controls; it is not a guarantee.

These are same-agent local audits, not independent peer review. New paid
service spend is $0. No paid review is requested or required. Raw trajectories
remain local and ignored by Git; scripts, compact results and figures will
be public. A census exception may leave its partial mesh unavailable; the
start marker, previous data and failure record must survive, without retry.
