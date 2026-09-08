# EXP-482 numerical refinement — engineering draft, not target authorization

**Current checkpoint (2026-09-08):** the human policy supersedes the mandatory
paid-review requirements below. The review packet was published, but its API
attempt failed before generation. It will not be retried automatically. The
local-audit gate migration is complete. All 192 target numerical comparisons
passed and collection/analysis completed with support-limited primary maps;
see the [complete result](../updates/2026-09-08-exp482-map-result.md) and
[current policy](../updates/2026-09-08-human-controlled-pro-reviews.md).

Both engineering measurements are complete, and the
distinct successor implementation has passed its actual source preflight
(426 tests, no skips; no target trajectories). See
[successor status](../updates/2026-09-07-exp482-successor-preflight.md) and
[protocol](EXP-482-successor-protocol.md). The remaining public review-packet
publication subsequently succeeded; no completed prospective Pro review or
target execution occurred. Earlier prospective sections
below are retained as historical expectations, not unfinished benchmark work.

EXP-481's complete qualification failed its unchanged scaled-state accuracy
criterion. All adaptive solver comparisons passed; smaller RK4 steps are the
next hypothesis, not an already verified repair. Preserve the stopped run,
original source and consumed attempt. This successor is explicitly informed
by those observed numerical diagnostics; it is not a clean confirmatory repeat.

## First bounded engineering measurement

Before selecting the successor's numerical/resource design, measure the
existing analytic-circle journal collector at RK4 .0025/.00125 through t=20.5,
with fixed batches of 128, 256 and 512 synthetic initial states, in that order.
Record every outcome. Use a 1,000-step journal interval, the existing crossing,
capture and analytic-error expectations, 20,000 maximum steps per profile and
32 raw events per seed. Each invocation has an external 60-second guard,
512 MiB sampled RSS/disk bounds and no automatic retry. These are synthetic
circles only: no target Rössler trajectories, new symbols or paid hosts.

The unchanged benchmark tests exact final-state error <1e-5, ordered profile
membership agreement and event-state/time differences <1e-5. The new explicit
`--step-profile refined` opts into the smaller steps; the original benchmark
default is unchanged. Raw event arrays, checkpoints and complete journals are
preserved by `scripts/benchmark_paired_sections.py`.

This first timing comparison can identify Python/batch overhead. It does not
by itself establish target completion: before a target release, account for
actual Rössler RHS work, both reference geometries, larger event/snapshot caps,
full-horizon journal counts, replay/analysis cost and conservative headroom.
Do not turn a fastest-case microbenchmark into a hard runtime promise.

## Decisions still open before any target execution

- Qualify finer steps against the unchanged 1e-4 state/timing criteria; their
  accuracy has not yet been observed. Identify the already seen qualification
  seeds explicitly and keep them distinct from fresh inferential sampling.
- Choose and freeze the fixed CPU batch/resource configuration based on the
  complete engineering measurements. RK4 .00125 through 300 requires 240,000
  steps per batch; the old 60,000-step declaration cannot be reused.
- Preserve both cases, reference conditioning, whole-seed holdout/bootstrap,
  all-profile agreement and the narrow scientific claim. No better-case,
  coordinate or threshold rescue of EXP-481.
- Obtain the compact prospective review for the materially revised successor,
  including the relevant prior review/adjudication and actual numerical
  failure. Map accepted repairs and freeze source, plan and gates before new
  target work. No placeholder approval or deletion of EXP-481's attempt marker.

## Full-workload engineering measurement (frozen before observation)

The next measurement is `scripts/benchmark_paired_refinement.py`. Its default
only prints the protocol; explicit `--execute` runs once in a fresh directory.
It does not change EXP-481 or authorize target integration.

Use batch 512 (selected from the disclosed first timing comparison), steps
.0025/.00125, the complete t=300 horizon, checkpoints every 50 time units,
1,000-step journals, 240,000 maximum steps, 262,144 maximum raw events per batch
and 8 MiB snapshots. The analytic circle has period 4.1 to avoid an endpoint
root; each seed must produce exactly 146 raw and 73 accepted events on each
section, no failure/ambiguity/capture, and final-state/event-time error <1e-5.
The same six/eight distant synthetic capture references are used, with a
discarded Rössler RHS evaluation at every circle RHS call. That extra arithmetic
does not create Rössler trajectories or qualify actual reference conditioning.

Measure complete journal writes/audits, independent raw replay using the real
80–140/180–240 windows and four strata, full file inventories, all four solver
qualification paths on two synthetic seeds, and actual both-case cubic analysis
with 8,192 seeds and all 200 bootstrap resamples. Require three branches and
the complete near/far reference matrix; the existing two-sheet adverse fixture
must remain unresolved. Preserve every outcome; no automatic retry.

Project collection/replay over all 32 batches **per profile** (two cases),
qualification over all 128 trials, and double time/disk/memory estimates.
Use the slowest of three supervisor-style filesystem scans to estimate a
full-tree scan. Conservatively charge twice that extrapolation at every .25 s
poll, including the small-tree startup period; report infeasible if its implied
occupancy reaches one. This is a pessimistic engineering estimate, not a
guarantee: unknown target event frequency, ambiguous roots, retained populations
and OS load remain limitations. Compare against existing 1,800/14,400/7,200 s
phase budgets, 8 GiB disk and 2 GiB RSS. The benchmark itself has a 900 s
parent/worker guard, sampled 2 GiB RSS/disk bounds and 16 GiB free-space reserve.

Verification status before measurement: protocol and analytic/projection unit
controls only. Full-workload live outcome remains unobserved.

**Subsequent result:** the once-only measurement is now complete; preserve the
preceding paragraph as the prospective status, not the current result. All
analytic/map controls passed, but the frozen .25-second polling feasibility
estimate failed. The separately labeled one-second polling calculation fits
projected limits. See the [complete update](../updates/2026-09-07-exp482-full-workload.md)
and [receipt](receipts/EXP-482-full-workload.json). Neither result authorizes
target work or changes EXP-481. Select the new seed/bootstrap draws 482001/482002
for the successor, with prior-outcome dependence explicitly disclosed.

The prax backup affects storage only. The upload guard rejected the renewed
request after the user's general go-ahead; no upload occurred and no bypass
will be attempted. The audited 37.7 MB EXP-481 archive remains safely local.
