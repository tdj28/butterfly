# EXP-481: common-trajectory collector implemented, target sampling still locked

The new `python/butterfly/paired_sections.py` records both sections along the
same batch of trajectories. Capture is a recorded label, never a reason to
stop integration. Existing `saddle.py`, EXP-479 and EXP-480 runners remain
unchanged. No new nominated Rössler trajectory, transient cloud, partition,
critical letter or word was generated.

This addresses a concrete design problem: the old single-section sprinkler
removes a captured trajectory and filters its middle-time records using that
section's final survivors. Calling it separately for each section would not
produce a common-population comparison.

## What the new collector retains

- Original seed IDs, initial and last valid states, failures and their first
  step/state; capture times and streaks separately for each section.
- Every detected endpoint-bracketed plane root, before orientation/gate
  filtering: event time/state, direction, nominal membership, signed gate
  distance, crossing angle, ambiguity flags and distance to the reference cycle.
- Both-section capture/failure/ambiguity checkpoint arrays. A contingency
  summary partitions seeds into neither/first-only/second-only/both captured,
  numerical failure and ambiguous-but-not-failed categories. The underlying
  arrays retain overlaps; this is not yet a selected survivor population.
- Unfiltered records from trajectories that later capture or fail. No
  trajectory weighting or statistical independence assumption is imposed.

Ambiguous roots cannot increment capture streaks. Capture times are first-hit
times under the chosen repeated-near-return rule; trajectories continue even
after both sections have marked them captured. A record cap aborts before
committing its overflowing step. Step state and both sections' diagnostics
are committed together so interruptions cannot splice different horizons.

## Controls completed

**24 analytic/synthetic tests pass.** They cover all capture categories,
continued integration after capture, unequal per-section event counts,
step refinement, seed-order invariance, rejected gate-edge roots, weak
orientation, sliding planes, exact step-endpoint ownership, record limits,
failure after capture, ordinary/late interruption and invalid input rejection.
The new field-parameterized RK4 arithmetic agrees exactly with the existing
kernel when both are given the same synthetic field. Hermite root interpolation
and cycle-distance evaluation reuse the existing helpers.
The full local regression suite passes **1,362 tests**, with one unrelated
Linux-only process-identity test skipped on macOS.

The important unequal-count control uses
`(x,y,z)=(cos(wt),sin(wt),sin(2wt))`, `w=pi/2`. One section has one return
per period, the other has two. The observed capture labels occur at different
times, but both sections retain the trajectory to the same final horizon.
This is a wiring test, not a model of the Jones six/eight-return cycles.

`scripts/benchmark_paired_sections.py` has an **analytic-only** entry point.
The 128-seed circle control completed both `dt=0.02` and `dt=0.01` profiles,
retaining 1,280 raw roots per section per profile. Ordered seed IDs,
orientations and nominal membership match. Maximum cross-profile event-state
and event-time differences were `2.911e-8` and `1.522e-7`; final-state errors
against the analytic solution were `1.177e-6` and `7.352e-8` respectively.
Both predeclared engineering gates passed. The local raw NPZs and source hashes
are retained at `artifacts/EXP-481/synthetic-collector-01/`; compact
[configuration](../experiments/receipts/EXP-481-synthetic-configuration.json)
and [result](../experiments/receipts/EXP-481-synthetic-collector.json) are public.
Synthetic execution speed is not extrapolated to a Rössler workload.

## What is still required before research execution

This is an in-memory numerical kernel plus engineering controls, **not the
durable, frozen target runner**. It detects endpoint-bracketed Hermite roots;
it can miss tangencies or multiple roots inside an unbracketed step. Initial
plane roots at `t=0` are flagged and excluded; later endpoints belong to the
step ending there. A step-refinement/adaptive-control protocol must qualify
the intended target observations; no all-root certificate is claimed.
The `failed` mask includes nonfinite integration and escape from the declared
bounded region; a finite escape is not a proof of mathematical divergence.

Next build the durable raw writer and outcome-free execution preflight, and
finish the explicit numeric manifest: seed distribution and IDs, capture
reference provenance, common retention, trajectory/event weighting, seed-level
holdout/bootstrap, horizons and support, coordinate choice and map adequacy,
failure/record-limit policy, and review binding. No target CLI or completed
scientific plan is supplied yet. The
[EXP-481 worklist](../experiments/EXP-481-common-population-partition-design.md)
still requires review/adjudication and a pushed pre-outcome freeze before
target sampling. Existing negative symbolic evidence remains unchanged.
