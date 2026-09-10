# EXP-519: fresh fixed-c response of the recovered fold

Prospective, outcome-informed numerical development. This document defines a
test, not a result. The public source freeze must precede target integration.

## Question and benchmark

EXP-518 transported four constructions of one fold to its fixed endpoint, but
all sixteen comparisons with the saved primitive orbit failed full-state
proximity, despite passing the x-only projection. Does a newly measured local
a-response support one bounded correction that passes full-state proximity?

The anchor is the exact saved endpoint: a=.21559892539912653, b=.2,
c=7.152000000000001. Its known failed result is the baseline, not held-out data.
The old EXP-502/503/507 derivatives describe different four/eight-return
families and are not derivative evidence for the recovered four/seven families.
The old correction's approximate 4e-6 a displacement informed the workload
scale only. No Jones target word selects a point or a numerical outcome.

## Fixed calculation

Keep b and c fixed. In order, integrate a-h, a+h for h=1e-5, then a-h, a+h
for h=5e-6. Finish all four points, including ordinary numerical failures.
At each point independently seed from the same qualified EXP-518 endpoint:
never seed a stencil point from another stencil outcome. Preserve all four
cases (history,direction)=(4,0),(4,1),(7,0),(7,1), both DOP853 and Radau,
the original affine x/z/tangent and the consistently updated legacy-section y.
Warm u/time are both-solver means; boxes remain u +/- .02 and time +/- 1,
with horizon time+3. A paired complete midpoint census supplies the return-time
seed strictly inside that time box. No adaptive box or direction substitution.
New family IDs explicitly name EXP-519 and history four/seven; historical
receipts and eighth-return failures are unchanged.

Recompute a periodic orbit at every point, always seeded from the same saved
qualified endpoint cycle. Keep all inherited correction tolerances, paired
solver gates, primitive-period tests, six historical/eight Barrio event counts,
and both phase .25/1.25 observation windows. Retain every shooting/observation
mesh. Check original-anchor and EXP-518-anchor event-index correspondence
separately using the existing EXP-502 rule (identity error <=.1 and a >1e-4
margin against every cyclic relabeling). No favorable cyclic shift is selected.

Each point must pass unchanged local fold, original-region, angle, gain,
projection, curvature, three-offset, and complete accepted-prefix gates.
Across the eight fold profiles require scaled state spread <=1e-6 and each
matched displacement from the fixed anchor <=.01, both at input and output.
Scales are [15,15,.01]. These are numerical identity checks, not proofs of
unique continuation, invariant-curve existence, or exact-flow regularity.

## Fresh response and one conditional correction

All sixteen fixed keys (four constructions x two solvers x two windows) retain
six signed residual components: (cycle event 3 - fold input)/scales followed
by (cycle event 4 - fold output)/scales. Indices are zero based. The first
component is the signed x residual used in the historical controller.

For each scale compute the central derivative using the *realized binary64*
separation in a, normalized to 1e-5. Require every point qualified; all sixteen
fine x derivatives finite, absolute value >1e-8 and the same sign (either
orientation); coarse/fine relative error <=.05 both for x and for the full
six-vector Euclidean norm. Denominators use max(abs(fine x),1e-30) and
max(norm(fine vector),1e-30). Tiny individual components are not separately
claimed resolved; the complete response vector and x controller are tested.
Report every coarse/fine component and failure, not only their mean.

Only if these gates pass, take delta = clip(-mean(anchor x residual) /
mean(fine normalized x derivative), -1, 1), then propose a+1e-5*delta.
Use the realized rounded step for predictions and enforce its bound with
1e-10 normalized floating-point slack. This is one correction, no line
search or retry. Zero realized step is recorded as a scalar-floor/full-state
mismatch with no correction. Never substitute a favorable stencil point.
The correction's folds and cycle again start from the fixed EXP-518 anchor.

For every variant, require the maximum absolute component of the full
six-residual vector <=1e-4. Also test the fresh model's prediction:
norm(observed residual - predicted residual) /
max(norm(predicted residual - anchor residual),1e-12) <=.1.
Report full-state contact and prediction qualification separately; the
stronger qualified-correction verdict requires both in every variant and all
point-identity/primitive/regularity gates. An x zero alone never passes.

Unqualified stencil: correction not run, with explicit reason. Unqualified
correction: retained negative result. Resource interruption: incomplete,
not a scientific pass or a resettable attempt. The calculation is deterministic
development, with sixteen sensitivity variants of one object, not sixteen
independent samples or a statistical confidence interval.

## Evidence, resources and release

One exclusive local attempt; maximum 768 target IVPs, 7200 seconds including
isolated startup, 3 GiB including final summary, 12 GiB initial disk reserve,
8 GiB continuing floor, and 1 MiB failure-report reserve. Existing analytic
fold, dense-census, primitive-circle and response controls are hash-verified
and replayed locally with no new control IVPs. New synthetic controls exercise
realized slopes, both orientations, nonlinearity, projection-only false
contact, missing/false keys, one-correction limits, and scalar-vs-vector audit.
The runtime and raw auditor retain and account for every created mesh/guard,
event census, correction iteration, ordinary failure and executed point.

The public EXP-518 ancestry is replayed once per process while its complete
byte fingerprint stays unchanged; a cache hit still rehashes the closure and
returns a deep copy. No frozen predecessor source is edited. Validate the
actual sealed deployment under python -I -B without ambient repository, raw
artifacts or bytecode; retain failed rehearsal trees and dispose only of a
successful rehearsal's temporary hash-identical public-file copies after
recording their complete hashes. Seal the transitive source and input inventory, then
commit and push before any new target outcome. Run the frozen raw auditor
and separately coded scalar differentiation/correction/verdict arithmetic
before interpreting the result. Shared primitives and one decision-maker
remain correlated; this is not independent-team replication.

This is an ordinary successor, so paid Pro review is not requested under the
human-approval policy. No API call, GPU rental, SSH change or raw upload is
authorized by this protocol. The earlier raw-upload denials remain intact.
Do not alter scientific thresholds or restart a consumed attempt to fit a
result. New scope, external spend beyond authority or an unanticipated
scientific-contract defect requires a visible amendment and appropriate
direction, not silent recovery.

## What either outcome means

Success establishes numerical proximity of a qualified projected fold and
one qualified primitive orbit under these fixed full-state tests. Failure
rejects this bounded local correction, not the existence of other solutions.
Neither result supplies a second smooth critical point D, a generating
partition, a homoclinic proof, a joint fold/boundary contact, an explanation of
the whole parameter plane, or verification/refutation of Jones' flow-level
symbolic chains. No boundary is integrated and no old two-parameter controller
is automatically resumed. Preserve EXP-518's failed baseline prominently.
