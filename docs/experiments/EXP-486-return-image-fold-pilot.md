# EXP-486 — folds of continuous finite-return image curves

Prospective exploratory pilot following EXP-485, not independent confirmation
of its outcome-informed candidate regions. No paid review, GPU or upload.

## Question and claim boundary

EXP-485 found two sampled directional-slope sign changes per case, but adjacent
points came from different trajectories. This pilot tests actual continuous
curves: Q_m(u) = P^m(q_-m + D d u), followed by P(Q_m(u)), where P is the
historical negative-oriented first-return map. It integrates each curve sample
as one uninterrupted flow trajectory with an initial tangent. It does not reset
the trajectory to stored intermediate states or interpolate a curve through
different seeds. The derivative includes the change in section-hit time.

A positive result can support consistent numerical projected folds of these
finite-image curves, on the stated local domains and tolerances. It cannot
establish an invariant graph, generating partition, exact critical center,
Jones word/arrow, chaotic-saddle membership, homoclinic existence, or a whole
parameter-plane explanation. All controls and all families are reported.
Unknown/grazing returns, degenerate curve parameterizations and multiple
unmatched roots remain unresolved. Historical symbols never enter selection.

## Fixed matrix and numerical construction

Use both EXP-485 cases and the two observed intervals defined by bins 0/1 and
16/17. The curve anchor is the right endpoint (bin 1 or 17), for both depths
m=4 and 8. Preserve that deterministic choice and its dependence on the
previous exploratory result. Use the anchor's actual q_-m from the authenticated
EXP-485 predecessor chain. Two initial directions in normalized section
coordinates are (1,0) and (1,1)/sqrt(2), with D=diag(15,.01). This gives
2 cases x 2 regions x 2 depths x 2 directions = 16 families, each checked by
DOP853 and Radau. Families share old trajectories and are not independent
statistical replicates. No confidence interval or population claim is made.

For each family, derive its fixed initial u radius from prior data only:
clip(2 * old observed x-gap / abs(row_x(G_m) D d), .0001, .05), where G_m
is the chronological product of the saved DOP853 predecessor derivatives.
Sample exactly 17 equally spaced u values, including zero. Preparation checks
every starting state and +/-1e-5, +/-1e-6 center perturbation before targets.
Invalid inputs fail preparation; no replacement point, radius or direction.
The same u grid is used by both solvers. DOP853 is the refinement driver;
Radau independently integrates every evaluated u and checks its derivative.

Use rtol=1e-10, atol=1e-12, max_step=.02, and a total horizon
20*(m+1). Integrate the state and one variational column through a 1e-8 initial
root guard, then terminate on the (m+1)-th oriented root. Every observed root
must satisfy the section gate, correct velocity orientation and normalized
crossing angle >=1e-7. A gate failure is unresolved, never skipped. This
specialization is valid here because on y=y_small, y'=x+a*y_small and
x_small=-a*y_small: the historical x<x_small gate is precisely negative
orientation. Verify this identity in preparation. Dense event detection is
not a rigorous all-root guarantee; analytic count/timing controls and the
two solvers test the actual implementation.

At roots m and m+1, preserve the full state, tangent, time gradient and raw
variational column. Compare solver scaled states <=1e-6, times <=1e-7 and
relative scaled tangent discrepancy <=1e-4, using a reference floor of one.
At u=0 both solvers must reproduce the saved anchor and next state/times
within 1e-4. At the two centered finite-difference steps, both solvers must
match their variational tangents at both return depths within relative scaled
error 1e-3. Missing comparisons are not passes.

## Numerical roots and projection safeguards

Let v_m = D^-1 Q_m'(u). A curve point may license an x-graph slope only if
norm(v_m)>=1e-4 and abs(v_m,x)/norm(v_m)>=.001. These are finite numerical
conditioning rules, not invariant-bundle error bounds. The projected slope is
Q_(m+1),x'/Q_m,x'. A sign change caused by Q_m,x' changing sign is not an
output fold: endpoints of a candidate interval must have the same nonzero
Q_m,x' sign and satisfy all curve/solver gates.

Search every adjacent valid grid pair for a strict slope sign change. An
exact grid zero is nominated only when its immediate valid neighbors have
opposite slopes and the same input-tangent sign; deduplicate touching
intervals representing that same exact grid zero. Retain all candidates.
More than two candidate intervals makes the family unresolved without
selecting preferred roots. Otherwise refine all candidates using bracketed
Brent root finding, fixed xtol=1e-10, rtol=1e-12, maximum 40 iterations and
50 new paired evaluations per bracket. Any invalid interior evaluation makes
that bracket unresolved; it does not permit bridging the gap or trying a
different method. A reported root requires normalized output-x derivative
<=1e-7 in both solvers, valid input-graph conditioning, matching tangent sign,
and all state/time/tangent gates. This is a numerical zero, not an interval
certificate. Preserve the original u bracket and every refinement evaluation.

Only roots whose Q_m,x lies inside the original observed x interval belong
to that candidate region; all other roots are still reported. If several u
roots map to the same section point, report each and the maximum pairwise
scaled-state separation. A family is consistent only if its in-region roots
are nonempty and their maximum separation is <=1e-4. A region is consistent
only if all four depth/direction families qualify and their pooled root states
also agree within 1e-4. Separation here is the maximum scaled-coordinate
range (the maximum pairwise infinity-norm distance), not Euclidean distance.
Never average away an unmatched family or root.

## Controls, release and bounded execution

The actual production path must reproduce an analytic nonlinear coordinate
transform of a rotating, contracting flow. With X=x-k*z^2, Y=y, Z=z,
X'=-Y, Y'=X, Z'=-lambda*Z, the kth return is known analytically. A slanted
initial line has a known projected output fold while its input image remains
a valid graph. Both depths and solvers must reproduce the root/state/tangent.
The k=0 version is a no-fold control. A vertical initial line produces a
projection-degenerate apparent zero, which must be rejected. Synthetic tests
also cover missing returns, wrong gates/orientation, invalid interior brackets,
zero-grid candidates, excessive candidates and retained out-of-region roots.

Preflight runs the exact input preparation and all analytic controls, with no
Rössler target integration. Freeze/push tested code and plan before targets;
record source/input hashes and runtime versions. Consume one exclusive attempt
marker immediately before the first target call. Preserve starts, raw events,
every evaluated point, roots, failed gates and errors in a fresh directory.
No retries or successor launches are implicit in this protocol. Limits:
3,600 seconds, 4,096 trajectory integrations and 128 MiB output, with 8 MiB
reserved for the terminal summary. A read-only, separately coded algebra/grid
audit precedes scientific publication. Same-agent audits are labeled as such.

Stay within local numerical-method work. Paid reviews, a new paid host or
publication of a full raw archive require their applicable separate authority.
No change to prior experiment outcomes or numerical thresholds is permitted.
