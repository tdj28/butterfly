# EXP-505: retrospective turning-point sensitivity for EXP-186

Status: prospective post-run sensitivity protocol, before re-fitting the saved
EXP-186 pairs. This secondary audit does not interrupt EXP-504's frozen flow
continuation. No new trajectory, parameter, target word or collection is chosen.

## Fixed scope

Audit both original RK4 profiles, both coordinates and all five oracle variants,
including every nominal and requested bootstrap fit, using the exact archived
EXP-186 midpoint states/times/trajectory IDs. The original published result is
already known: x has two branches, z one; parity and word gates fail. This is
therefore explicitly retrospective, not a new held-out experiment or a fresh
verification of the collected trajectories.

Inputs are the original manifest, raw receipt and states archive, with the
hashes recorded in the EXP-186 record. The historical return-map helper and
landmark runner must retain their original byte hashes. Do not edit them.
Form consecutive same-trajectory pairs independently by sorted ID/time and
cross-check the production pair constructor. Replay the original oracle before
interpreting the sensitivity; require agreement with all saved robust outputs,
including ordered bootstrap counts, intervals, flags and reasons. Numerical
arithmetic uses rtol 1e-12 and atol 1e-13; discrete outputs must agree exactly.
A failed original replay is an unresolved audit, not permission to tune options.

## Sole sensitivity change

The legacy helper admits some stationary inflections as branch boundaries.
Keep its complete candidate-generation, deduplication, prominence, binning,
smoothing, support, bootstrap indices and aggregation rules unchanged. For each
root admitted by the old helper, additionally require:

- opposite nonzero derivative signs on either side;
- a height above both adjacent candidate landmarks or below both, not merely
  large absolute changes.

Reconstruct the complete pre-prominence candidate list with the original grid,
Brent solve and deduplication. Side probes are root +/- delta, where delta is
the minimum of one grid spacing and one quarter of the distance to either
adjacent candidate/domain endpoint. A zero or nonfinite side derivative fails
qualification. Retain every root's side probes, derivative values, signed
height differences and decision. Report what the filter removes as a
sensitivity rejection; do not claim certified root completeness or exact-flow
geometry. Unchanged legacy failures and support deficiencies remain failures.

Run the identical nominal/bootstrap oracle twice: original and additional-turn
filter. Each fit is identified by profile, coordinate, variant and call ordinal.
Use a temporary function substitution confined to the new audit process; the
shared source file and the running EXP-504 process are untouched. No favorable
subset or alternative probe scale is selected after seeing outcomes.

If original robust outputs reproduce, compare all corrected robust fields,
not just nominal branch counts. Replay the eight old profile/coordinate/solver
word rows using their saved orbit states and unchanged alphabet/zero-slope
requirements, first with original and then filtered partitions. This is only
downstream sensitivity of the same saved inputs, not renewed integration,
primitivity, generating-partition or Jones-arrow validation.

## Validation, provenance and interpretation

Before target re-fitting: analytic monotone-cubic, ordinary maximum/minimum,
two-turn cubic and low-prominence controls; synthetic deterministic bootstrap
replay; pair-order cross-check; input/hash and first-failure controls; isolated
source startup; a clean live-pushed source freeze. One exclusive EXP-505 marker.
Limit this saved-data analysis to 600 seconds and 100 MiB new output; retain
failures and consume the attempt rather than retry or mutate old evidence.
Require at least 8 GiB free throughout. No paid review, cloud rental, upload,
dependency change or evidence deletion is needed.

After the run, hash outputs and independently replay the pair construction,
root geometry, original oracle results and sensitivity outputs from the same
authenticated saved data. The audit shares historical fitting helpers and is
not an independent-team numerical replication. Retain exact source/runtime
bindings and all four profile-coordinate results, including unchanged ones.

The primary report is how many retained roots/nominal or bootstrap decisions
change, whether critical intervals/robust outcomes change, and whether any of
the eight saved-input word outcomes change. No change clears only this helper
sensitivity for EXP-186's saved partitions, not all EXP-186 assumptions or the
42 candidate manifests in the static exposure inventory. Any changed result
receives a labeled correction without replacing the historical receipt.
