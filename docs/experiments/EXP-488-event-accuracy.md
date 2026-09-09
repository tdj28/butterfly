# EXP-488: accuracy of the reconstructed section crossings

Prospectively frozen exploratory refinement, 2026-09-08. No paid review.
EXP-487 remains failed in case `local-a027-c083`; EXP-486 is unchanged.

## Question and design

Do both saved EXP-487 witness trajectories have a reproducible section-event
census when tolerances tighten? The second witness failed both refined state
agreement and agreement with the older EXP-486 Radau event. These are different
questions: an older numerical reference need not be more accurate. Here the
old reference is retained as a diagnostic, never required to be ground truth.
This is a new estimand, not permission to change EXP-487's verdict.

Use precisely both original states, tangents and parameter triples from the
hash-bound EXP-487 public receipt. Replay its existing audit before targets.
The complete matrix is two witnesses × DOP853/Radau × tolerance pairs
`(1e-10,1e-12)`, `(1e-12,1e-14)`, `(1e-13,1e-15)`: 12 integrations.
The first tolerance level reproduces an observed baseline, not a holdout.
Keep maximum step 0.001, horizon 50, guard 1e-8, the legacy negative-oriented
section, state scales `(15,15,0.01)` and extremum margin 1e-10 unchanged.
Reuse the frozen EXP-487 extremum-partitioned census, including its Brent
root tolerances. Keep all ordinary roots, reconstructed roots, extrema,
raw variational vectors, integration steps and augmented states.

## Decision fixed before outcomes

All six profiles must have equal accepted counts, at least five returns,
no uncertain extrema, angle at least 1e-7 and section residual at most 1e-8.
For all six unordered pairs among the four **fine** profiles (two solvers
at each of the two tighter tolerances), every ordinal event must agree to
scaled state infinity error 1e-7 and time error 1e-9. These are tenfold and
hundredfold tighter than the EXP-487 thresholds, respectively; they are
engineering convergence checks, not calibrated confidence intervals.
No favorable solver, event, or refinement pair may be selected.

Report every profile's ordinal errors against the finest Radau comparison
profile and against the old EXP-486 Radau fifth event. That comparison profile
is not presumed exact. Baseline disagreement does not itself reject fine
convergence; missing counts, uncertain extrema and invalid section geometry
do. Strict monotone error reduction is not required near floating-point limits.
Both cases pass = both witnesses numerically converged under these checks;
one pass = mixed; neither = unresolved. No result supplies a new fold or letter.

## Controls, audit, limits and release

Run EXP-487's six hidden-pair/no-root/tangency controls before targets. Also
run all six solver/tolerance profiles on the existing nonlinear transformed
rotation field `control_field` from EXP-486, at the same maximum step and
guard, horizon 13, initial `(-4,0,0.5)`, tangent `(1,0,1)`. Its accepted
events are exactly `t=2*pi*n`, n=1,2, with state
`(-4-0.25*(1-exp(-0.06*t)), 0, 0.5*exp(-0.03*t))`.
Require state infinity error ≤1e-8 and time error ≤1e-9, both events and no
uncertain extrema. Synthetic matrix tests challenge missing/duplicated arms,
nonfinite values, fine disagreement, count changes and coarse-reference drift.

The same-agent local audit is not independent peer review. It independently
reconstructs the matrix, checks section-event algebra, retained trajectory
shape/finiteness, bracket completeness, source/input hashes and exact decision
replay. It does not reintegrate targets or prove absence of undetected extrema.
The manifest contains no outcomes. Commit/push and verify the exact source
before creating the exclusive EXP-488 marker and starting targets. Retain UTC
start/end timestamps and all raw reports, including failures. One attempt,
12 target calls, 1,800 s alarm, 256 MiB output cap; no retries or fallback.
Escalate a needed new paid service, expanded data disclosure or changed
scientific target to the human; local numerical failures are reported as such.

The prior cheaper ordinary-event list remains visible. Extremum partitioning
already existed in the project's period-six grazing helper; this study does
not claim algorithmic novelty. Its contribution is testing accuracy on both
fixed failures before using the corrected collector for further geometry.
