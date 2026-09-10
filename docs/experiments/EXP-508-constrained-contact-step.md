# EXP-508: one constrained lower-c step

## Timing, question and permitted conclusion

This outcome-informed pilot follows the complete EXP-507 raw audit. It tests
whether one lower-c predictor plus an explicit fixed-c fold correction can
preserve the qualified primitive cycle and fold proximity while reducing the
limiting-boundary gap. EXP-504's rejected point and EXP-507's nonjoint result
remain unchanged. A passing step is local continuation evidence, not an exact
critical contact, C/D identification, generating partition, source-matched
p-to-p+1 arrow or verification/refutation of Jones's symbolic chains.

## Frozen model and two-stage sequence

Start at the single EXP-507 point. Retain all 256 correlated residual variants.
The model's a column is the measured EXP-504-to-EXP-507 secant, normalized by
the realized a displacement divided by .0001. Its c column remains the original
EXP-502/503 fine-stencil column. Require a pure nonzero a displacement,
qualified endpoints, positive fold a slopes above 1e-8, the inherited common
orientation/condition rule, and at most .1 relative two-component a-column
change from the original fine stencil in every variant. Independently coded
scalar arithmetic checks the secant column. This hybrid model is not a newly
measured full Jacobian. No updated model is fitted during the two-stage run.
Use scalar sums for the plan-bound predictor; retain platform-sensitive matrix
diagnostics in execution evidence rather than demanding exact bits in the
machine-plan recipe. NumPy prediction arithmetic is cross-checked numerically.

1. Predictor: subtract exactly .02 from the starting binary64 c; hold b=.2.
   Compute the realized normalized c displacement. Choose the normalized a
   displacement -(mean F_fold + mean J_fold,c * dc)/mean J_fold,a. Reject rather
   than clip if its magnitude exceeds .1. The realized bound allows 1e-12
   floating-roundoff slack in normalized units. Preserve the original-a domain
   bound .002 and c in [original c-.2, original c].
2. Recompute the complete point. Numerical qualification and original,
   EXP-507-start and adjacent cycle-index correspondences must all pass before
   a corrector is eligible. A failed full-state fold-proximity gate alone does
   not prevent this prescribed correction: it is what the correction tests.
3. Corrector: hold the predictor's b,c fixed. Use -mean F_fold/mean J_fold,a,
   clipped to [-.1,.1], for one further a displacement. Recompute the entire
   point from warm predictor seeds, with unchanged boxes/horizons/thresholds.
   Run the correction even if the predictor already meets full-state tolerance.
   The sole exception is |mean F_fold| <= 1e-12: skip the zero-sized correction
   only when full-state fold proximity already passes; otherwise reject the
   step with the scalar-floor/full-state mismatch explicitly recorded.

Each stage retains all four fold representations with both ODE methods,
eight boundaries with both Decimal configurations, and both cycle methods and
both windows. All inherited numerical and primitive six-historical/eight-Barrio
return-count gates remain unchanged. Keep every mesh, guard, shooting iteration,
coefficient stream, full-prefix certificate and every parent candidate. These
representations share trajectories/cycles; they are not independent samples.
Warm seeds use the unchanged EXP-504 constructor. No alternative step size,
third correction, fallback or restart is allowed.

## Acceptance and baseline

The complete prescribed sequence must finish (or the exact correction-waiver
rule must apply). Its terminal point must qualify, pass all original/start/
adjacent identities, and satisfy worst full-state fold input/successor distance
<= 1e-4. In addition, require a strictly smaller worst full-state boundary
distance at fixed cycle index 1 than EXP-507, and a strictly smaller absolute
boundary residual in every one of the 256 correlated vectors. An improved mean
or combined norm cannot override any failed criterion. Report the full-state
boundary reduction descriptively and joint proximity separately under the
unchanged all-variant 1e-4 rule.

Retain the predictor-only endpoint under those same criteria as the cheapest
baseline, beside the corrected endpoint. This comparison determines whether the
corrector was actually needed under the declared tolerance; do not assume it
helped. A passing predictor cannot replace a failed prescribed correction.
Archive every predicted and observed component separately. A stage with failed
qualification cannot license numerical-change interpretation. A raw failure or
resource interruption preserves the attempt and cannot be labeled a completed
accepted step. Missing conditional stages have explicit status and reason.

## Resources, controls and source gate

Local CPU only. At most two full points, 1,024 target IVPs, 3,600 seconds and
3 GiB of complete run output including summary, with 12 GiB initial free space
and an 8 GiB continuing floor. Reserve 1 MiB for failure; the exclusive marker
has its own 1 MiB cap. Prior point sizes (about 1.08-1.36 GB) motivate this
two-point allowance; a larger actual Newton workload stops at the same cap.
Do not delete old raw files or increase the cap after outcomes. The existing
bounded JSON, NPZ and compressed-stream adapters apply to every new product.
The final summary uses point references rather than duplicate journals.

Before target access: test linear/secant arithmetic, every conditional stage,
predictor-only baseline, nonfinite/missing variants, component-local failure,
full-state versus scalar gates, original/start/adjacent identity, exact bounds,
raw writer equivalence and quota failure. Run the full local suite and an
authentic isolated copied-source startup, and hash-check/replay all 34 original
analytic-control files. Publish and live-verify the clean source freeze before
the new attempt marker. Default CLI execution performs validation only.

The local design audit specifically challenges the stale c derivative, rejects
combined-norm reasoning, exposes the cheaper predictor-only comparator and
prohibits selecting it after a failed correction. It verifies raw capacity for
both stages and the complete-summary check. This is a same-agent audit, not
independent-team replication; paid review is not requested under human policy.

## Raw audit, publication and escalation

Hash the entire retained inventory before scientific interpretation. Replay
the unchanged full-point raw auditor for each required stage, reconstruct the
warm seed/order, all controller decisions and both baseline/terminal endpoints,
and re-count the complete directory including its summary. Counts must match
all retained integrations, including guard IVPs. A same-code local replay is
not an independent scientific replication.

Only code, compact comparison evidence and documentation are authorized public
Git products here; raw trajectories remain local. No new paid model call,
GPU rental, remote computation, raw upload or deletion is authorized by this
plan. New spend/egress authority, relaxed thresholds, an exhausted storage
reserve or a scope beyond these two stages requires a separate decision, not
an improvised modification or reused marker. Record every outcome, positive or
negative, in the dated update and claim ledger before a further continuation.
