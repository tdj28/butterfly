# EXP-490: direct projected-fold shooting across all 26 candidate intervals

Prospective exploratory successor, 2026-09-08. All sixteen EXP-486 families
and all 26 original candidate intervals are retained, including the two
depth-eight families with four candidates each. This is a new geometric
estimand, not a relaxation of EXP-486's two-bracket limit or a rerun of its
failed root searches. EXP-487/488 remain mixed; EXP-489's two grazing witnesses
motivate the distinction between event boundaries and smooth projected folds.
No paid review or remote compute is requested.

## Question and equations

Does a candidate interval contain a numerically qualified projected fold of
the specified finite-return image curve, with the correct event ordinal?
We do not assume slope-sign changes bracket a continuous function.

For initial curve `q(u)=q0+u*v0`, integrate the state q, first sensitivity v
and second sensitivity w at fixed elapsed time:

    q' = f(q),  v' = J(q)v,  w' = J(q)w + H(q)[v,v],  w(0)=0.

For Rössler, the Hessian contraction is `(0,0,2*v_x*v_z)`. On the historical
plane, solve the two equations

    h = y-y_small = 0,
    g = f_y*v_x - f_x*v_y = 0.

For a transverse return, the x sensitivity is `X_u=g/f_y`. This determinant
form does not divide by the near-zero velocity during Newton iteration.
Its fixed-time Jacobian is

    h_u=v_y, h_t=f_y,
    g_u=(Jv)_y*v_x + f_y*w_x - (Jv)_x*v_y - f_x*w_y,
    g_t=(Jf)_y*v_x + f_y*(Jv)_x - (Jf)_x*v_y - f_x*(Jv)_y.

With `tau_u=-v_y/f_y`, the exact event second derivative is
`X_uu=(g_u+g_t*tau_u)/f_y - g*(J*(v+f*tau_u))_y/f_y^2`.
The root must subsequently pass the transversality, event-order, finite-
difference, input-projection and solver checks below. A Newton zero alone
is not a fold, and failure to find one is not proof that none exists.

## Complete input and target matrix

Build a public candidate table from the hash-bound EXP-486 audited receipt
and its saved endpoint reports. Copy each family's parameters, initial state,
tangent, history depth, prior x interval and original u bracket exactly.
Use the midpoint of that u bracket and the mean of its four old endpoint
return times (two endpoints, two solvers) as the sole initial guess.
Time bounds are minimum old endpoint time minus .5 and maximum plus .5;
census horizon is the upper time bound plus 2. Every input and historical
endpoint hash is published before new trajectories, allowing this successor
to run from the public table without the old local raw archive.

Run two solvers, DOP853 and Radau, for each of 26 candidates: 52 bounded
shootings, maximum eight nine-dimensional trajectory integrations each.
Use rtol=1e-13, atol=1e-15, max_step=.001. No alternative initial guess,
line search, bracket expansion or target-driven retry. An update outside
the fixed u/time box, singular Newton matrix or exhausted iteration budget
leaves that candidate unresolved for that solver. Preserve every iterate.

Stop Newton only when |h|≤1e-10 and
`|g|/max(1,||f||*||v||)≤1e-10`. Convergence does not waive any later check.
For each converged shooting, run three separate six-dimensional extremum-
partitioned censuses, centered at its root u and at u±epsilon, where
`epsilon=min(1e-6, bracket_width/100)`. If either perturbation leaves the
original bracket, retain an explicit unresolved-boundary result and skipped
census records; do not shrink epsilon. Retain all ordinary roots, reconstructed
roots, extrema and augmented trajectories through the frozen horizon.

## Qualification, fixed before target outcomes

- Select the first m+1 accepted negative-oriented events, where m is the
  original history depth (4 or 8). All selected events must have normalized
  crossing angle ≥1e-7 and plane residual ≤1e-8, with no uncertain extremum
  before the selected event. Extra later events remain in the raw census.
- The center census's (m+1)th event must match the fixed-time shooting endpoint
  to time 1e-7 and scaled-state infinity error 1e-6, using (15,15,.01).
  A different event ordinal makes the root unresolved.
- At all three displacements, the mth event defines the input curve. Its
  scaled tangent norm must be ≥1e-4 and x fraction ≥.001. Its x tangent must
  keep the same sign; no vertical-projection or event-order gap is bridged.
- Center normalized output derivative, relative to input tangent norm, must
  be ≤1e-7. The two perturbed x-graph slopes must have strictly opposite signs.
- The central difference of the two output x sensitivities must agree with
  the shooting-derived X_uu to relative error ≤1e-3, using max(1,|X_uu|) as
  denominator. Require the magnitude of `15*X_uu/Xinput_u^2` to be ≥1e-6.
- Both solvers must independently pass; their roots must agree within u 1e-9,
  time 1e-7 and scaled state 1e-6 at both input and output returns. Report
  all comparisons, not a favorable profile. A candidate qualifies only if
  every check passes. Separately flag whether the input x lies inside the
  original observed region; out-of-region roots are not silently discarded.

Report each candidate and every family, including nonconvergence, skipped
perturbations, invalid event order and failed curvature/solver checks. Count
qualified in-region folds and unresolved candidates per family; do not claim
a complete region or partition merely because each family has one success.
Existing qualified EXP-486 right-hand roots are the prior positive baseline,
not new independent discoveries. No C/D assignment or word/arrow comparison.

## Controls, feasibility, audit and release

Use the existing transformed-rotation field with counts 2 and 3 and both
solvers, with exact state, first/second sensitivity and projected-fold formulas.
Exercise a genuine fold (k=1e4, initial tangent (1,0,.01)), no fold (k=0,
tangent (1,0,.01)), and degenerate x projection (k=0, tangent (0,0,.01)).
This is the previous analytic system with its z coordinate scaled by .01;
it preserves the known x dynamics while making the positive input curve
well-conditioned in the unchanged target metric (15,.01). The unscaled
first development control correctly failed that metric's x-projection gate;
no target threshold or target initial condition is changed.
Positive control initial (-4,0,.005) has exact root
`u=1/(2*(1-exp(-.06*T)))-.5`, T=2*pi*count. Use the fixed u box from that
known root minus .04 to plus .02, seed time T+.01, time box T±.5, horizon
T+2.5 and epsilon1e-6. For the degenerate control seed time is exactly T
to challenge a pointwise zero that is not a fold. Controls use the same
shooting, census and qualification pipeline; negatives must not qualify.
Synthetic tests verify the fold Jacobian and event second derivative against
known formulas and finite differences, malformed/missing arms and all gates.

The same-agent read-only audit reconstructs all 26 candidates and 16 families,
checks source/input hashes, raw nine-dimensional endpoint identities, Newton
steps, separately evaluated Rössler fold algebra, complete side-census geometry,
and exact qualification replay. It is not independent peer review, a rigorous
error bound, or an all-root guarantee. The public table is executable input;
its historical endpoint provenance is separately hash-anchored.

One fresh attempt, at most 572 retained target trajectories (416 Newton and
156 census calls, each census also has a tiny guard subintegration), maximum
7,200 wall seconds and 8 GiB output. Before launch require at least 16 GiB free
space; keep an 8 GiB free-space floor during execution. Current local available
space is approximately 28 GiB. No paid service, cloud upload, deleted evidence
or automatic retry. Escalate any needed paid service, enlarged disclosure or
materially different scientific objective; numerical failures remain results.
Freeze the complete code, table, controls and protocol on the remote first;
execute in the same turn once green, without a discretionary review gate.
