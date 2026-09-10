# EXP-510: keep the continuation on a qualified fold branch

## Audited result: one qualified substep, then another input-curve collapse

The complete **180-IVP raw audit passes**. The first substep qualifies all
four families and both solvers. Their scaled cross-history full-state spread
is 1.4988e-13, below 1e-6, and their maximum displacement from EXP-507 is
0.00093268, below .01. This is a qualified fold-only transport step; no new
cycle or joint-contact point at that parameter was measured.

The second substep again fails both depth-8 families in both solvers. Their
center input gains are 5.23e-12–2.46e-11, below the unchanged 1e-4 minimum;
both neighboring slopes are positive, about 0.032429. The shorter-history
folds still qualify. The controller correctly stops and leaves the final
two prescribed substeps unrun. There is no endpoint comparison, full transport
success, exact contact or symbolic-chain result.

| Substep | a | c (b=.2 throughout) | Raw IVPs | Audited result |
| --- | --- | --- | --- | --- |
| 1 | 0.21559286120158497 | 7.167000000000001 | 88 | All four folds and transport checks pass |
| 2 | 0.21559488260076548 | 7.162000000000001 | 92 | Depth 4 passes; both depth-8 inputs are unresolved |
| 3 | 0.21559690399994602 | 7.157000000000001 | 0 | Not run: predecessor unqualified |
| 4 | 0.21559892539912653 | 7.152000000000001 | 0 | Not run: predecessor unqualified |

This rules out this particular four-substep recipe as a sufficient repair.
It does not prove that every smaller-step strategy must fail, or that the
physical fold ceases to exist between the two parameters. A numerical
qualification boundary is not automatically a physical bifurcation locus.
In particular, finite transported curves can lose useful coverage or
conditioning even when another representation resolves the same return map.

## Reproduction and resources

Execution took 795.27 seconds and retained 538,510,243 bytes including the
summary, within the fixed 1,800-second and 2-GiB caps. Counts reconcile as
132 inherited archive products plus 48 explicitly retained guard integrations.
All raw inventories, source bindings, attempt markers, scalar comparisons and
the 26-parent ledger pass replay. Every failure is retained; no tolerance,
attempt or original result was changed. The raw audit itself ran zero IVPs.

The [public audit receipt](../experiments/receipts/EXP-510-four-substep-fold-transport-result.json)
is byte-identical to artifacts/EXP-510/primary-audit-01.json, SHA-256
`43399d794bf8c55a20e73706a4850453f43ac762a465a3a7d39b9cc7665a8fe7`.
Public compact replay passes with 13 receipt/tamper controls; the five
algebraic regularity controls also pass (18 tests in 20.41 seconds). Public
replay does not reacquire the full local raw archive or independently recount
its integrations and disk bytes. Shared-code local audit is not independent
scientific replication.

Final release validation: **2,584 local tests pass**, with one Linux-only skip,
in 219.40 seconds (artifacts/EXP-510/release-suite-01.xml). Citation/figure
availability and the receipt-generated symbolic table also pass. The original
228-file run inventory and all frozen source hashes were rechecked after
publication-copy preparation and remain unchanged.

```
PYTHONPATH=.:python .venv/bin/python scripts/verify_exp510_public_transport.py \
  --result docs/experiments/receipts/EXP-510-four-substep-fold-transport-result.json \
  --expected-sha256 43399d794bf8c55a20e73706a4850453f43ac762a465a3a7d39b9cc7665a8fe7
```

## Next: distinguish root selection from finite-curve coverage

At the failed second parameter, directly sample the declared depth-8 image
curves across a prospectively fixed u-domain. Retain both directions and
solvers, all event/regularity failures, input-coordinate turning points and
all connected slope-sign brackets. Compare curve coverage with the qualified
depth-4 fold states before starting another Newton correction. This can
separate an accessible fold missed by the solver from a finite representation
that does not adequately cover it. A finite grid alone cannot certify absence
of every root; any absence claim needs an appropriate enclosure or an explicit
unresolved remainder. Do not simply repeat the same continuation with a new
step size or lower the input-gain threshold.

## Execution record

Source `0e11f95e352364afcb0be43a2e39a1d12ffaf9b5` was frozen, pushed to the
working branch and preserved `codex/exp510-local-execution` reference, then
live-verified before starting artifacts/EXP-510/target-0e11f95. The one-shot
marker is consumed. PR #76 tracks this experiment. The producer summary reports
`transport_completed=false`, SHA-256
`539cedeb5b044f97761f510a5a91b1b8026732c5089b36df173b8993e1ab5577`.
The full raw audit and failure diagnosis above supersede the historical
pre-target status below.

## Pre-target checkpoint

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

The [critical-point regularity note](../methods/critical-point-regularity.md)
explains the motivating distinction with exact algebraic examples. Its five
no-IVP controls pass; they do not change any frozen numerical source or gate.
