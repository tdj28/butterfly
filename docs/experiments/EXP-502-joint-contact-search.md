# EXP-502: a bounded joint a,c contact step

Prospective outcome-informed pilot, not preregistered. EXP-497 supplies a
primitive-cycle/right-fold proximity anchor; EXP-501 supplies the qualified
limiting boundary and a negative contact result at that anchor. No EXP-502
target outcome has been generated when this design is written. Paid review
is not requested under the human-directed policy.

## Question and exact target

Can both distinct operational contact residuals be reduced together by
varying a and c at fixed b=0.2? The reference is
(a,c)=(0.21558015990653545,7.212). The first residual is
(cycle event 3 x - right-fold input x)/15; the second is
(cycle event 1 x - limiting grazing predecessor x)/15. Indices are zero-based
within the inherited historical-section phase windows. Event 1 is selected
prospectively because it was the closest all-variant index in EXP-501; this
is an outcome-informed search, not an independent confirmatory sample.
All six event distances remain reported. No alternate index may replace a
failed primary search.

Eight fixed new stencil points: a or c separately, both signs, at scale 1 and
1/2. Base increments are ha=0.0001 and hc=0.002. Every point starts from the
same authenticated EXP-497 cycle correction and the same EXP-497/501 fitted
fold/boundary root seeds. No favorable-neighbor seeding. Record the exact
binary64 parameter values actually passed, and divide finite differences by
their realized spacing, expressed in the normalized ha,hc coordinates.
The base residuals are the old audited results, not a repeated EXP-501 run.

At every point recompute both cycle profiles, all four right-fold
representations, and all eight boundary representations in both decimal
precisions. The cycle and fold implementations, thresholds, full-state
input/output proximity, finite-difference curvature checks and primitive
six/eight event tests remain those used by EXP-497. The boundary uses the
EXP-501 decimal affine-input, shooting, coefficient retention and complete
accepted-prefix census contract. Only the parameter-dependent section offset
and initial y coordinate change; initial x,z and directions remain fixed.
Use mean fitted parent roots as seeds, u boxes seed +/-0.02, time boxes seed
+/-1, and fold horizon seed time +3 with epsilon 1e-6. Boundary prefix counts
remain 4,1,4,1,5,8,5,8. This is finite-return-curve transport, not an invariant
quotient theorem. Preserve all 26 parent ledger entries and old failures.

For cycle-index transport, compare the six new events to the corresponding
EXP-497 method/window under all six cyclic shifts. Identity must be the
unique best shift by more than 1e-4 in the maximum scaled-state distance
(maximum absolute component under scales [15,15,0.01]),
and its maximum distance must be <=0.1. Do not rotate a failed row into
agreement. This is a numerical local correspondence check, not proof of
global continuation.

## Complete response matrix and one proposal

Cross four fold representations with eight boundary representations and two
boundary precisions, sharing each of the two cycle methods and two windows:
256 ordered residual-vector variants. All eight stencil points must qualify
before a joint proposal is allowed. For each variant compute both 2x2 central
difference Jacobians. Require both finite and nonsingular, 2-norm condition
number <=1e4, and identical determinant sign across every scale and variant.
Each fine/coarse Frobenius difference must be <=5% of the fine norm (floor
1e-12). Missing, unqualified or inconsistent variants block the proposal;
they are not discarded. No inferential independence is assigned to this
cross-product of correlated representations.

Use the mean fine Jacobian and the mean old reference vector to solve one
Newton step in normalized ha,hc coordinates. The mean system must itself
be finite with condition number <=1e4. If the maximum absolute step
component exceeds 10, shorten the entire vector by 10/maxabs. This is a
fixed radial trust bound, not a line search. Reject nonfinite or exactly zero
steps. At most one new proposal point is measured; no retry, backtracking,
Jacobian refit or second proposal. All old source seeds are still used there.
The eight stencil points run regardless of previous stencil failures; a
failed point cannot seed another point. Stop only on resource or evidence
integrity failure, retaining all unfinished slots explicitly.

Primary success requires the proposed point's complete qualified matrix,
right-fold **input and output** proximity to cycle event 3 and its successor,
and boundary predecessor full-state proximity to event 1, all <=1e-4 under
scales [15,15,0.01]. Zero x residual alone is insufficient. Report the same
full-state tests at all stencil points as diagnostics; a favorable stencil
point does not impersonate the proposal. Secondary diagnostic: whether the
maximum absolute mean two-residual vector falls by at least 20% relative to
the old anchor. A decrease is not contact and does not replace the primary.

Outcomes: qualified joint proximity; qualified proposal without joint
proximity (with/without residual reduction); unresolved response matrix;
or failed proposal qualification. Every result keeps Jones words, C/D,
homoclinicity, exact criticality and primitive p-to-p+1 arrows unverified.
Failure of this local model does not refute a global chain or exclude other
cycle-index assignments/parameter regions. No paid API or GPU is needed.

## Validation, raw evidence and bounds

Freeze source, inputs, machine plan, controls, runner, independent audit and
failure rules before targets; verify a clean live-pushed commit and isolated
copied-source startup before the exclusive EXP-502 attempt marker. Preserve
the exact frozen source ref. All controls execute before the marker: the
inherited full fold control matrix, one-/two-traversal periodic controls,
both decimal analytic grazing/variation/census controls, and synthetic
two-residual response matrices (known linear solution, singularity, nonlinear
scale disagreement, missing/failed variants and radial clipping). Retain
control raw files where the inherited producer provides them; the old fold
control producer retains reports but not complete meshes, disclosed here.

Every periodic shooting/observation mesh, fold Newton/census mesh and decimal
state/tangent coefficient step is retained. Count actual solve_ivp calls,
including each fold census's separate guard integration, before they begin;
also retain a separate count of archived trajectory products for comparison
with inherited audit functions. Source inspection found that the inherited
census producer omits the guard mesh from its returned archive. The successor
wrapper therefore retains each guard separately and checks its endpoint
against the main census's initial state. Older archive-product counts are
not silently relabeled as counts of every solve_ivp invocation. The separate audit checks inherited fold algebra and
cycle closure/event/minimal-period evidence, every decimal coefficient,
Newton trace and polynomial certificate, and reconstructs the complete
response matrix. A second scalar 2x2 implementation checks the proposed step;
shared classification is disclosed, not independent-team replication.

Local CPU caps: 9 new parameter slots, 2048 actual target IVPs, 7200 seconds,
8 GiB new output, 17 GiB free before starting and 8 GiB reserve. These are
caps, not forecasts. Numerical point failures are retained and all other
stencil points still run. Exceptions or storage/time/source failures stop
execution and preserve partial files and the consumed marker, never reset it.
All raw evidence remains local; only authorized code and compact audited
results are published. No denied raw upload is retried. A passing local
result still needs geometric branch coding and a genuine neighboring-period
connection before it can validate the Jones mechanism.
