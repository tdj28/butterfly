# EXP-510: keep the continuation on a qualified fold branch

The [fixed four-substep protocol](../experiments/EXP-510-four-substep-fold-transport.md)
targets the same endpoint as EXP-508, but transports the roots from qualified
EXP-507 using smaller parameter increments. The purpose is to test the branch
tracking failure diagnosed by EXP-509—not to relax the input-gain threshold or
reclassify the rejected collapsed-curve roots.

Every executed substep includes both directions, both history lengths and
both solvers. Continuation requires every representation's existing gates,
cross-history full-state agreement and bounded displacement from the previous
qualified point. No stage can borrow a successful subset. The endpoint cycle
is reused only for explicitly labeled comparisons; no new intermediate cycle
or complete joint point is claimed.

The implementation and raw auditor are complete. **28 focused controls pass
in 3.52 seconds**, including 11 new transport regressions and 17 inherited
bounded-product controls. Isolated copied-source startup passes with 107
source/input paths. All original analytic controls replay without new IVPs.
Receipts are retained in artifacts/EXP-510/preflight-01.xml,
preflight-startup-01.json and preflight-controls-01.json. The full local suite
passes **2,566 tests with one Linux-only skip in 201.11 seconds**, retained in
artifacts/EXP-510/pretarget-suite-01.xml. Citation/figure and symbolic-table
checks pass. The clean source freeze precedes numerical execution; no target
has run.

EXP-508/509's audited result merged through PR #75 as
`43bdb2194e0e084b150d7cc4f6ba9336449cc252`, after all final-head Python 3.12
and 3.13 push and PR checks passed. EXP-510 continues on the fresh-main branch
`codex/exp510-small-step-fold-transport`. The pre-target machine-plan hash is
`45ea6fe9fece7e9cb856665b19a652f7087746d761d8113bb8779dc56d696d28`.

Limits: four substeps, 512 IVPs, 1,800 seconds, 2 GiB complete output, 12 GiB
initial free-space reserve and an 8 GiB continuing floor. Every failed stage,
raw file and consumed marker remains preserved. No paid review, new GPU job,
remote compute or raw upload is needed. Jones's flow-level symbolic chains
remain unresolved.
