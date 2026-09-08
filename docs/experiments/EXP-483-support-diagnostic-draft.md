# EXP-483 draft: diagnose the support bottleneck using preserved EXP-482 data

Status: completed; see the [illustrated result](../updates/2026-09-08-exp483-support-diagnosis.md).
Descriptive, outcome-informed analysis; **no new target integration
or changed EXP-482 result**. No paid review is requested or required for this
routine local diagnostic. This is not a new confirmatory sample.

## Question and fixed source

Why did the completed EXP-482 map test lack domain support despite adequate
retained seed counts and passed early numerical qualification? Is the observed
loss primarily associated with the time window, final-horizon conditioning,
the equal-weight pair selector, or persistently sparse section geometry?

Use only `artifacts/EXP-482/target-8ce3716` at execution freeze
`8ce37169ef9c24c570f5e2b9d5a60e48f310c377`. The campaign receipt SHA-256 is
`c4ab5fb1fdd07273e5e5f4b2c7548b1d073e3645e1cc63f24738a2bf2418c27e`;
full analysis SHA-256 is
`d43f996f0a9e24d959689fba975cb3f851505a5192a26e4dca006dcf2af2a27d`.
First verify those anchors and the complete relevant journal inventories.

## Execution list

- [x] Implement/test a bounded read-only diagnostic and commit it before the
  new diagnostic execution. No calls to a field, integrator or paid API.
  `scripts/diagnose_exp483_support.py` has a 600-second wall limit, requires a
  clean committed source and fresh output below `artifacts/EXP-483`, streams
  authenticated raw batches, and retains a failure receipt if it fails. The
  original analysis is replayed unchanged for integrity, not refitted under
  alternative settings. Twelve new synthetic tests and four existing summary
  tests passed before execution. The inherited raw bound is 262,144 events per
  batch. Outputs contain aggregate counts, not a new raw-data copy.
- [x] Reproduce the original common cohort and four-pairs-per-window selection
  exactly before comparing alternative descriptive populations.
- [x] For both cases, both step profiles and both original windows, tabulate
  distinct-seed occupancy on all declared 30/40/50-bin partitions using the
  original calibration normalization. Include calibration and held-out counts
  separately; do not use holdout data to refit, normalize or select a model.
- [x] Partition missing support into zero observed seeds versus one to seven
  observed calibration seeds; separately count held-out observations outside
  the fitted interval and inside under-supported bins. Overlapping reasons must
  be disjointly tabulated or explicitly marked nonadditive.
- [x] Compare the original selector with **all available true consecutive
  accepted event pairs** in those same windows as a descriptive sensitivity
  check. Count distinct seeds, not pair abundance, and never bridge an ambiguous
  event or interpolate an unobserved crossing. Keep unequal pair counts visible.
- [x] Describe reference-conditioning effects with mutually explicit groups
  from existing capture/failure/ambiguity records. Never call an uncaptured
  finite-time path a proven chaotic invariant orbit or treat post-capture pairs
  as independent transient evidence.
- [x] Report every case/window/profile and the fixed-bin sensitivity, including
  negative or mixed evidence. Do not infer physical absence of a return map from
  an empty observed bin or a missing bootstrap/turning result.
- [x] Propose the smallest new geometry-directed flow experiment justified by
  these diagnostics. New initial states or integration require a separate
  prospective source/design freeze and unchanged evidence-preservation rules.
  The separate EXP-484 pilot targets actual early calibration states and their
  two-dimensional first-return derivatives. It does not refit or rescue EXP-482.

## Boundaries and stopping

No replacement primary pass/fail decision, new fit selection, alphabet,
critical-membership matrix, chain-arrow verdict or homoclinic conclusion is
allowed from these post hoc comparisons. EXP-482 remains support-limited.
No original artifact, attempt marker, phase terminal or held-out label is edited.
Use a fresh diagnostic output directory with explicit resource bounds and retain
any failed audit; the old experiment is not restarted or resumed.

The purpose is to choose a defensible sampling/geometry method, not to find a
favorable interpretation of already inspected observations. The independent
flow-level symbolic-chain question remains the scientific finish line.
