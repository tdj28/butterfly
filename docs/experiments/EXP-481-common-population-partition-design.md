# EXP-481 — Common-population historical partition: implementation worklist

Status: outcome-free successor design; **not an execution authorization**.
EXP-480 qualified observation of both fixed cycles, but no transient cloud,
partition or word has been generated for this successor.

Implementation checkpoint: the separate dual-section in-memory kernel and
analytic-only benchmark now exist and pass their synthetic controls. See
[the collector update](../updates/2026-09-06-exp481-dual-section-collector.md).
Do not rebuild it from scratch. The write-once durable journal and draft-only
integrity preflight now also pass their outcome-free controls; see
[the recording update](../updates/2026-09-06-exp481-durable-recording.md).
An explicit [numeric sampling/analysis proposal](EXP-481-sampling-and-analysis-proposal.md)
and tested seed selection/held-out map primitives now exist. They are unreviewed,
not a frozen target plan. Journal replay, fixed-ID cohort intersection and joint
map/proximity decisions now pass [end-to-end synthetic controls](../updates/2026-09-06-exp481-replay-decisions.md).
The adaptive adapter and raw capture-reference audit also pass their
[controls](../updates/2026-09-06-exp481-adaptive-qualification.md). The bounded
target runner and adjudicated review remain pending. Durable adaptive recording
and the sampled-resource supervisor now pass
[synthetic process-loss controls](../updates/2026-09-06-exp481-durable-supervisor.md).
The draft preflight cannot
authorize target execution.

## Question

Do independently sampled finite-time noncaptured trajectories at both
EXP-479 nominations support a stable, adequately resolved historical-section
scalar return map, and is the nominated cycle near its neutral critical set?
Answer that before attaching Jones's letters. A monotone, multivalued,
undersupported or unstable projection is an informative outcome.

## Implementation sequence

1. Reuse the existing Float64 batched integration and capture code only after
   separating its single-section survivor filter from raw collection. Observe
   both sections on each same trajectory, retaining seed IDs, event times,
   states, capture flags and numerical failures. Do not stop a trajectory's
   integration merely because one section has marked it captured.
2. Define a common retention rule prospectively. One candidate is uncaptured
   under both section-specific tests at the same physical horizon. Report the
   full contingency table (neither, historical-only, Barrio-only, both),
   integration failures and insufficient-event exclusions. This estimates a
   finite-time conditional population; it does not prove a chaotic saddle.
3. Make trajectory/seed the independent sampling unit. Freeze whether the
   primary map estimate weights trajectories equally or events equally.
   Unequal numbers of returns make those different estimands. A bounded equal
   number of temporally stratified pairs per retained seed is a possible
   implementation; disclose every resulting coverage exclusion. Bootstrap and
   train/validation splits must be by seed, never by treating correlated
   successive returns as independent observations.
4. Before collecting new outcomes, compile a complete numeric manifest:
   deterministic seed distribution, both original candidate IDs and hashes,
   physical horizons/checkpoints, step/refinement profiles, two capture rules,
   root and boundary exclusions, storage caps, per-seed pair selection,
   trajectory weights, calibration/holdout split, and failed/censored cases.
   Qualify the collector on synthetic dual-section trajectories and the
   existing non-target controls. Do not tune these choices on source words.
5. Freeze scalar-map adequacy as the primary endpoint: held-out conditional
   spread, domain coverage and support, reproducibility of branch/critical
   structure under fixed reconstruction variants, and trajectory-block
   uncertainty. x is the historically motivated primary coordinate; z may be
   a declared diagnostic, not required to inherit the distant control's
   branch count. Reuse thresholds only with an explicit rationale under the
   new sampling/weighting convention.
6. Only an adequate neutral map may be used to assess the orbit's critical
   membership, with independently inferred intervals and slope residuals.
   Use both nominated cases; an overall claim cannot select only the better
   one after observing results. Freeze support/sample-size justification for
   map resolution, not the probability of obtaining a desired word.
7. Obtain/adjudicate the compact design review, pass controls, and push the
   exact executable freeze before target sampling. Alphabet transport and
   continuation-arrow tests remain later, separate gates.

## Economical first action

Complete the source/review-bound production CLI, canonical environment/import
closure, authenticated startup and both-case aggregation in the numeric proposal.
The kernel, durable journal, deterministic seed/pair selection and held-out
seed-bootstrap analyzer, replay and joint decisions are implemented; do not rebuild them. The ambiguous
previous provider transaction remains separately guarded and must not trigger
a duplicate worker create.

The proposed retention/weighting ideas above are design candidates, not
silently frozen choices. No new survivor outcomes should be generated until
the numerical choices, executable plan, controls and review are complete.
