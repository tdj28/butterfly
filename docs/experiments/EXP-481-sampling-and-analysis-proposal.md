# EXP-481: a common-population test of the historical return map

Status: **numeric proposal, not reviewed or authorized for target execution**.
The result-free seed table and local selection/map-analysis primitives are
implemented. The remaining execution/review work is listed at the end.
The machine-readable choices are in
[`EXP-481-paired-sampling-proposal.json`](../../experiments/manifests/EXP-481-paired-sampling-proposal.json).
The earlier locked draft remains intact as historical design evidence.

## The question in plain language

Jones's symbols require a meaningful division of a return map into branches.
Before testing the letters, we must find those branches without asking the data
to reproduce the letters. At each of the two previously nominated cycles,
sample new trajectories, observe the historical and Barrio sections on the
same trajectories, and ask whether a scalar coordinate predicts its next return
reliably on held-out trajectories. Only then compare the already-qualified
cycle with independently inferred turning regions.

This design can fail informatively: too few trajectories may remain, the
projection may be multivalued, the map may be monotone, critical locations may
move with the numerical/analysis choices, or the cycle may miss the turning
regions. None of these alone debunks Jones's entire construction. No outcome
licenses a homoclinic existence claim, alphabet transport or a symbolic arrow.

## Sampling, not a repeat of the old scout

Both `local-a025-c083` and `local-a027-c083` stay in scope. EXP-479 selected them;
they are not an independent random sample of the parameter plane. The new
initial conditions are independent of the old grid, conditional on using its
rectangle as the sampling frame: 8,192 IID uniform `(x,z)` draws from
`[-14,-0.2] × [0.008,0.55]`, with PCG64 seed `481001`. Each candidate supplies
its own historical-section `y` offset. The same ordered `(x,z)` table is used
for both cases and both step profiles. That pairing does not make the two
candidate results independent replications across parameter space.

Global IDs `0..4095` are calibration and `4096..8191` are holdout. This split is
fixed before states are integrated. IDs are never reassigned after failure,
capture or exclusion. The canonical table commitment is
`84400ee6a80d4e83fcea0355f37a1f1e86b1ea1468c33821292bce784cb49ebc`.
The initial section-plane root is excluded and flagged, not a reason to remove
the seed; every seed starts on that plane by design.

Observe each seed to physical time 300, at Float64 RK4 steps 0.01 and 0.005,
with checkpoints every 50 time units. The earlier 200-unit scout informs the
sampling frame and step choices; the longer horizon and later observation
window explicitly test finite-time sensitivity. They do not establish an
infinite-lived chaotic saddle or eliminate every long transient.

Capture is five consecutive accepted section returns within scaled distance
0.0002 of the relevant reference cycle. References are exactly the first
window of each EXP-480 DOP853-refined result: six historical and eight Barrio
points, not a relabeled correspondence between them. Historical distances use
`(x,z)/(15,0.01)`; Barrio distances use `(y,z)/(15,0.01)`. The shared physical
units make the thresholds comparable as operational distances, not invariant
geometric objects. A label does not stop integration. The narrow threshold and
repeated returns reduce accidental near-hits, but do not prove asymptotic basin
membership or phase-ordered convergence. Their dependence remains a limitation;
this proposal does not add an undeclared radius sweep after results.

## One common cohort, eight selected pairs per trajectory

Each profile first reports every seed in mutually exclusive categories:
numerical failure; ambiguous but not failed; historical-only capture;
Barrio-only capture; both captured; neither captured but insufficient pairs;
or retained. Underlying masks and raw events preserve overlaps and all excluded
records. The final analysis cohort is the intersection of retained IDs across
both profiles, so the two numerical analyses use the same IDs. A disagreement
of more than 0.03 of all 8,192 input IDs blocks the joint numerical claim.
Report each profile's counts and the intersection loss; do not quietly replace
one sample by its easier survivors.

Retained seeds must remain numerically valid and unambiguous to time 300,
uncaptured by either section, and have sufficient pairs on **both** sections
in **both** observation windows `[80,140]` and `[180,240]`.
This is a deliberately conditional finite-time population. Conditioning can
select unusual trajectories; the result is not a claim about the whole basin.

Divide each window into four 15-unit, half-open source-time strata. Select the
first true consecutive accepted-return pair with its source in that stratum
and its target no later than the window end. A target may fall in the next
stratum: strata constrain source times, not both endpoints. An opposite-direction
or gate-rejected root is not a return to the chosen section. An unresolved root
excludes the seed; it is never silently skipped to join nonconsecutive returns.
No interpolation, duplicated pair, nearest substitute or refill is allowed.

Each retained seed therefore contributes exactly four pairs per window per
section, regardless of how many other returns it has. Windows are analyzed
separately. This gives equal trajectory weight in each map, not equal weight
to every available event. Selection of the earliest pair in each stratum is
an explicit temporal sampling rule, not a uniform draw from all return events.
All eligible counts and raw pair indices remain available to audit that choice.

## A held-out scalar map, with a simple baseline

The primary coordinate is historical-section `x`. Historical `z` and Barrio
`z` are diagnostic projections and cannot rescue failure of the primary map.
Do not demand the distant EXP-176 control's branch count at these parameters.

`seed_return_map.py` uses the established binned-median smoothing-spline
approach, with changed sampling and uncertainty bookkeeping—not a claim of a
new reconstruction method. For each window/profile separately:

1. Normalize both coordinates using the minimum and maximum of calibration
   pair endpoints only. Keep these constants for validation and bootstrap.
2. Fit cubic smoothing splines to bin medians. The five fixed variants are
   `(bins,smoothing)=(40,1e-5),(30,1e-5),(50,1e-5),(40,1e-6),(40,1e-4)`.
   Each occupied bin needs eight distinct original calibration seeds, with
   at least 70% of bins occupied. More than two consecutive empty interior
   bins is unresolved. No spline extrapolation is used.
3. Find derivative sign changes only between the first and last supported
   bin medians; retain extrema with at least 0.03 normalized prominence on
   both sides and opposite derivative signs one grid spacing to either side.
   A maximum must be above both adjacent landmarks and a minimum below both;
   absolute differences alone do not suffice.
   A stationary inflection is not a turning boundary; a sub-grid pair of
   numerical roots is not merged into one extra branch. A retained extremum needs its bin and both neighboring bins
   occupied. Flat/degenerate calibration coordinates and spline warnings
   cannot be promoted to qualified partitions.
4. Evaluate on held-out seed blocks without refitting. At most 5% of held-out
   rows may be outside the fitted/supported domain. The 90th percentile
   absolute prediction error on supported rows must be at most 0.08 of the
   calibration coordinate range. Report a calibration-only least-squares
   affine baseline on exactly those same held-out rows beside the spline.
   The baseline is descriptive and does not add an outcome-selectable gate.
5. Resample entire calibration seeds 200 times with PCG64 seed `481002`,
   keeping their four pairs together. Repeated draws give their block repeated
   weight, but do not create new distinct observed seeds for bin support.
   Failed bootstrap fits count against stability. At least 80% must resolve
   with the nominal critical count. Retain all replicate counts, including
   failures, not only successful positions.
6. All five variants must agree in critical count. The descriptive envelope
   over nominal/count-matched bootstrap positions and variants must be no
   wider than 0.04 of the calibration range. This is **not** a 95% or
   simultaneous confidence interval, nor an inferentially calibrated test of
   exact topological branch count.

The sample-size floor is 256 retained calibration seeds and 256 retained
holdout seeds, per case after the common-cohort intersection. Four pairs make
1,024 rows per split/window, but still only 256 independent trajectory blocks.
For 50 bins, the 70% coverage rule requires at least 35 occupied bins, each
with eight distinct seeds. These are explicit resolution/support floors, not
a claim of 80% statistical power or a guarantee that 8,192 starts will suffice.
If they fail, report insufficient support and do not increase the sample within
this run. The range, prominence and error thresholds specify the resolution
being tested; they do not come with a proven false-positive rate.

The q90 criterion can miss rare secondary sheets affecting fewer than roughly
10% of supported observations. The allowed unsupported tail and gaps also
bound the conclusion: even a pass means an adequate **finite-resolution
projection on the retained sample**, not a globally single-valued return map.
The original row-bootstrap code remains unchanged; it is not used to claim
independence for correlated returns in this experiment.

## Joint stability and cycle comparison

The implemented primary gate requires agreement across both windows and steps
within each case: all resolve, critical counts agree, and matched ordered
critical regions together span no more than 0.04 of the combined calibration
domain. Ordered regions must be disjoint both within each map and in the
combined envelope; otherwise matching is unresolved. This is an explicit
pre-review clarification, not a gate chosen after target results.
Cases are reported individually; the future production wrapper must require
both for overall support. The per-case joint decision and following comparison
are implemented and [synthetically tested](../updates/2026-09-06-exp481-replay-decisions.md).

Only after that gate, compare **all six** historical reference-orbit points
with every ordered critical region. Require proximity within the inferred
interval padded by 0.01 of the calibration range and absolute normalized
spline slope no greater than 0.02 in every primary variant/window/profile.
Report the complete point-by-region distances and slopes, including misses.
No phase is selected to match a source letter, no derivative is rounded to
zero, and no expected number of near-critical events is forced.
The strongest permitted wording is finite-resolution proximity to independently
estimated turning regions, not exact criticality or Jones-symbol verification.

## Numerical qualification, bounds and next implementation

Before full collection, an adaptive adapter must compare both RK4 profiles
with DOP853 and Radau on the same preselected 16 global seed IDs per case,
through time 20. The manifest fixes tolerances, maximum steps and accepted
event-state/time agreement at `1e-4`. These early-transient diagnostics are
new target computations and must wait for the reviewed freeze. They cannot
certify long-time shadowing or exclude every missed tangency. Later ensemble
agreement is a separate check, not a substitute for that limitation.

The result-free batch table has 512 rows: two cases × two profiles × 128
64-seed batches. CPU only; no new paid worker. The proposal caps collection
at 14,400 seconds, analysis at 7,200 seconds, process RSS at 2 GiB, raw collection
storage at 8 GiB, and requires 16 GiB free before starting. These are stopping
bounds, not completion-time estimates. The wrapper must enforce them, preserve
partial evidence and stop on technical invalidity; no automatic retry/resume.

Remaining before any target data generation:

- Adaptive early-transient qualification adapter, shared event/capture semantics,
  and bounded CPU process supervisor, including complete two-case aggregation.
- Authentic source/input/review-bound production preflight; verify capture
  reference rows against EXP-480 raw events, not only copied result summaries.
- One compact design review, adjudication of all findings and exact pushed
  executable freeze. The journal/analysis primitives do not supply that authority.

This proposal is deliberately explicit so the reviewer can challenge the
scientific choices before outcomes exist. The research-integrity playbook
requires completing these steps, not another permission request to the user.
