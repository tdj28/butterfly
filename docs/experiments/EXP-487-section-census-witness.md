# EXP-487: test the missed-crossing mechanism directly

Prospective exploratory witness study. EXP-486 remains unchanged: one of four
regions qualified, and the left-region refinements failed solver agreement.
This study tests event enumeration, not replacement fold roots or symbols.

## Fixed inputs and matrix

Use the first failed paired refinement in the depth-4, direction-0, left-region
family of each case: evaluations 28 and 33. This choice is explicitly informed
by the completed EXP-486 result. Both witnesses have four matching accepted
returns, then an earlier fifth crossing in Radau than in DOP853. The exact
source, parent inventory and input hashes are checked before use.

Start from each original full-trajectory initial state and tangent, not from a
newly selected replacement point. Integrate state plus one variational column
with both DOP853 and Radau at maximum steps .02, .005 and .001: twelve targets.
Keep rtol=1e-10, atol=1e-12, the 1e-8 initial guard and a fixed horizon of 50.
Do not stop on a target event count. Save every integration step/state as a
compressed binary array, all ordinary unoriented plane roots, normal-velocity
extrema, bracket endpoints and reconstructed roots.

## Reconstruction and acceptance

The plane residual h(t) can cross zero twice inside one solver step without
changing sign at its endpoints. Its derivative is the normal velocity. Locate
zeros of that velocity, partition time at those stationary points of h,
and bracket every strict sign change of h on the resulting intervals. Refine
with the solver's continuous interpolant and Brent's method (xtol=1e-12,
rtol=1e-14). Keep ordinary roots separately. An extremum within 1e-10 of the
plane is explicitly uncertain and prevents qualification; never call it a
transverse crossing. The extrema themselves remain numerically observed,
so this is not a proof that all possible roots have been found.

All six profiles in each case must reproduce the complete accepted census of
the finest Radau profile, including chronological states and times. Require
at least five accepted roots, state discrepancy <=1e-6 in scales (15,15,.01),
time discrepancy <=1e-7, section residual <=1e-8 and normalized crossing angle
>=1e-7. The previous Radau fifth event must match precisely the fifth accepted
reconstructed event within those same tolerances. Report every ordinary-event
omission and every failed comparison, not just the witness event.

## Controls and bounds

The analytic plane residual (t-.5)^2-.0001 has two known roots, .49 and .51,
inside one forced solver step. Both solvers must miss them in the ordinary
endpoint-sign event list and recover both through the actual census path.
The positive-offset version has no roots; the zero-offset version has an
uncertain tangency, not a licensed crossing. All six controls run before the
exclusive target marker. Unit tests retain missing/extra roots, changed
states, uncertainty and incomplete profile matrices as failures.

Freeze and verify the exact source on the remote before execution. Limits:
1,800 seconds, twelve integrations, 256 MiB output. One exclusive durable
attempt marker; no automatic retry. A read-only full-grid audit precedes
publication. No paid review, host rental or upload. A successful witness
would diagnose an event-detection weakness and qualify this numerical repair
for these two trajectories only. It does not retroactively pass EXP-486 or
establish a fold, generating partition, Jones word/arrow or homoclinic claim.
