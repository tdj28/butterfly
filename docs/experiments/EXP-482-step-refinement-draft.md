# EXP-482 numerical refinement — engineering draft, not target authorization

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

The prax backup approval affects storage only; local numerical engineering
can continue while the audited 37.7 MB EXP-481 archive remains safely local.
