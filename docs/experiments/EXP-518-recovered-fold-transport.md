# EXP-518: transport the recovered fold representations

Prospective protocol. No new target integrations or numerical result are
asserted here; the dated updates track preflight checks and source-freeze status.

## Question and known outcomes

EXP-517 recovers the same full-state local fold with histories four and seven,
each in both original initial directions. All eight solver profiles pass
unchanged local gates. Can these four constructions track that fold through
the two remaining fixed EXP-510 parameter substeps?

This is outcome-informed development. EXP-510 stopped at substep two;
EXP-508/509 already exposed the final endpoint using the old depth-four/eight
representations and a saved primitive cycle/boundary calculation. The newly
constructed seven-return curves have not been tested there, but the parameter
endpoint itself is not blind or wholly held out. No target word is used.
Every original failure and consumed marker remains immutable.

## Fixed path and complete matrix

Copy the exact binary64 parameter dictionaries from the EXP-510 frozen plan,
not rounded prose coordinates or a new interpolation:

| Stage | a | b | c |
| --- | --- | --- | --- |
| Start: EXP-517 / old substep 2 | .21559488260076548 | .2 | 7.162000000000001 |
| New substep 3 | .21559690399994602 | .2 | 7.157000000000001 |
| New substep 4 | .21559892539912653 | .2 | 7.152000000000001 |

At every executed stage retain all four cases `(4,0),(4,1),(7,0),(7,1)`,
both DOP853 and Radau, every midpoint/guard/Newton/census product, and every
failure. A stage cannot pass using a subset. If a stage fails, finish its
complete four-case matrix, mark later stages unrun because the predecessor
failed, and do not use failed roots to seed another calculation.

Four and seven are construction-history lengths, not primitive orbit periods
or symbolic-chain labels. The original eighth-return failure remains in the
parent ledger and is not renamed as a successful seven-return calculation.

## Warm start and unchanged scientific gates

For each case take the mean of both qualified predecessor root u/time values.
Preserve the original affine-curve x, z, and tangent; update a, b, c and the
legacy section's y coordinate consistently. Preserve the explicit history and
count `history+1`; never relabel history seven as the failed history eight.
Use inherited u +/- .02, time +/- 1 and horizon time + 3. At each proposed u,
retain a paired full midpoint event census and use its accepted return time
to seed the unchanged bounded two-equation Newton solve. A seed outside the
time box is a retained failure, not permission to expand a box.

Keep all inherited ODE tolerances, iteration limits, three fixed offsets,
gain/projection/angle/curvature, original-region and local finite-difference
thresholds. Check both solvers' complete accepted prefixes at every eligible offset, not only
the final event. Fold equations converging on a collapsed input remain failed.

Require all eight qualified full input/output states at a stage to have
scaled componentwise spread <= 1e-6, and each matched solver/case displacement
from its predecessor <= .01, with scales `[15,15,.01]`. The .01 displacement
gate is the existing EXP-510 finite branch-identity test, not a replacement
for its 1e-6 cross-representation accuracy gate. Both must pass. This is not
rigorous unique continuation or proof of invariant-curve existence.

## Endpoints and claim scope

Only after both stages qualify may the new endpoint folds be compared with
the exact, hash-bound EXP-508/509 endpoint primitive cycle. Retain all sixteen
originally defined comparison variants (four constructions, two matched
solver methods, two repeat windows) and both full-state endpoints. Reuse the
unchanged <=1e-4 proximity rule, independently replay the scalar arithmetic,
and report the old boundary result only as reused context. No intermediate
cycle or newly qualified joint point is inferred; no new cycle or boundary
integrations belong to this fold-only test.

A successful endpoint does not silently resume the old joint controller:
its family/variant bindings and response derivatives were built for different
curve constructions. A successor joint-contact calculation must explicitly
bind the new four/seven-return families and qualify its local response model,
while preserving the primitive-period, full-state and all-variant proximity
thresholds. Do not reuse a failed depth-eight root or relabel its derivative.

Failure diagnoses local transport or identity, not global fold absence.
Success supports renewed joint contact, not a C/D dictionary, generating
partition, primitive chain membership, Jones arrow or exact-flow proof.
Even a future fold/boundary contact would not by itself establish the second
smooth critical point needed for a doubly critical itinerary. A section
grazing must not be relabeled as that missing scalar turning point.

## Execution and audit still required

Implement and test the actual bounded numerical dispatcher and full raw
auditor, bind the complete source/input closure, replay existing analytic
controls, exercise real copied-source startup without raw data, run regression
tests, then freeze/push the exact reviewed source before one exclusive attempt.
No target run is allowed before these gates pass.

Fixed cap: 256 target IVPs, 3600 seconds, 2 GiB including final summary,
11 GiB initial free space and an 8 GiB continuing floor, with a 1 MiB failure
reserve. Recheck actual disk before freeze. All products use the tested
bounded JSON and compressed raw writers. No paid API review, GPU job, remote
worker change or raw upload is part of this local CPU experiment.

The independent arithmetic audit must reconstruct all seeds, candidate
identities, full event histories, local qualifications, cross-representation
and predecessor distances, explicit unrun statuses, endpoint eligibility,
IVP inventory and byte totals from retained evidence. Public compact replay
must clearly state that it does not contain/re-audit all raw flow meshes.
