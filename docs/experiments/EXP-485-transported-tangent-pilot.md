# EXP-485 — finite-history transported-tangent pilot

Prospective local CPU experiment; no paid review or external upload. This is a
method-development pilot, not confirmatory verification of Jones' chains.

## Question and construction

EXP-484 qualified direct first-return derivatives at 80 observed calibration
states. A fixed-z coordinate partial is not the derivative along a thin return
curve. Can a finite-history dominant direction at those same states stabilize
under history-length and solver changes? This tests a necessary practical
ingredient of a scalar reconstruction, not existence of an invariant curve.

Keep both parameter cases and every EXP-484 point. Authenticate the EXP-482 raw
journals and recover the eight immediately preceding accepted historical-negative
returns of the same seed. Reject ambiguity anywhere in that seed's journal;
missing history fails preparation without selecting a replacement. Preserve raw
event indices, times and states, and verify exact agreement with the EXP-484
anchor. There are 80 observation points from 27 and 26 distinct old calibration
seeds respectively; repeated points/segments are not independent replicates.

Evaluate the event-time-corrected 2D first-return derivative at each predecessor
with DOP853 and Radau: exactly 1,280 integrations, no deduplication and no target
word inspection. Reuse the authenticated EXP-484 derivatives at the endpoints.
Keep its solver tolerances, event rules, horizon and state/time/Jacobian gates.
Both solvers must also reproduce every saved predecessor-to-successor state and
elapsed time at those thresholds. A segment restarts at its recorded RK4 state:
the product is a finite-history derivative cocycle along observed points, not
an exact derivative of a single uninterrupted eight-return trajectory.

Use the declared section metric D = diag(15, .01), with scaled Jacobian
D^-1 J D. Compose chronologically over the last 1, 2, 4 and 8 predecessors,
renormalizing each product. Its leading left singular vector is a direction at
the endpoint. Require singular-value ratio <= 1e-4 at depths 4 and 8 in both
solvers, angle between those two unoriented lines <= .001 rad, and cross-solver
line agreement <= .001 rad at every depth. These operational thresholds mean
strong finite-time direction selection and ~0.057-degree agreement; they are
not rigorous invariant-bundle error bounds. Ratios below machine precision
must not be called exact rank loss. Scaling is fixed, not tuned for a result.

For the depth-8 direction v, report (Jv)_x/v_x only when |v_x| >= .001.
Otherwise report an undefined x-graph derivative. Compare it descriptively with
the coordinate partial. Do not assign C/D, interpolate a critical point, or
infer branch existence from adjacent signs alone. Direction qualification
requires all segment geometry gates as well as the direction gates. Report
all points, missing returns, failed gates and complete continuous metrics.

## Controls, release, and bounds

Synthetic tests cover a contracting diagonal map, changing output tangent and
noncommuting chronological products, sign/scaling invariance, huge/small
products, near-vertical lines, and isotropic and history-inconsistent negative
controls. The actual CLI runs EXP-484's analytic rotation/contraction flow
controls through both solvers, plus tangent positive/negative controls, before
any target integration. Existing EXP-484 coordinate finite-difference results
remain useful but do not validate an invariant curve; no new such claim is made.

Freeze tested source and machine plan on a pushed commit before targets. A fresh
preflight consumes no targets. Execution consumes one exclusive EXP-485 marker;
no reset/retry on failure. Record starts and raw solver results before analysis,
hash all inputs/source/output, and retain failures. Bounds: 1,800 seconds and
64 MiB output, with 4 MiB reserved for the summary and 128 KiB for a failure
record. No automatic successor
run. A read-only post-run audit must independently reconstruct the full expected
trial grid, event-time correction, product orientation and decisions before
public scientific reporting. Same-agent audit is not an independent reviewer.

## Next decision

If directions stabilize, use the qualified finite-history directions to design
a separate curve/critical-point continuation and held-out symbolic test. If
they do not, identify whether missing returns, integration agreement, competing
directions, or x-projection degeneracy caused failure. Neither outcome alone
verifies or refutes Jones' symbolic chains. Do not require an exact mathematical
invariant-curve proof before attempting an honestly conditional numerical test.
