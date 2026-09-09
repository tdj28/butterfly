# EXP-487: missed crossing confirmed; numerical repair partly qualified

The follow-up ran and was audited without a paid service. **All twelve target
profiles completed. One witness passes every frozen check; the other does
not.** The result confirms a concrete limitation of ordinary endpoint-sign
event detection, while preserving a remaining accuracy failure.

| Witness | Extrema-based accepted crossings in every profile | Ordinary DOP853 omissions | Full frozen verdict |
| --- | ---: | --- | --- |
| a=.21575 | 7 | Fifth crossing missed at max_step=.02 | Pass: all six profiles |
| a=.21577 | 9 | Fifth crossing missed at max_step=.02 and .005 | Fail: state and old-witness agreement tolerances |

Both have b=.2 and c=7.212; the horizon is 50. Counts refer to the entire
fixed observation, not the period of an orbit. These are two outcome-informed
trajectories, not twelve independent discoveries.

## What went wrong, in plain language

An adaptive ODE solver can follow the trajectory accurately but still miss a
section crossing. Its ordinary event detector looks for a sign change between
step endpoints. If the trajectory crosses the plane and crosses back within
one step, the endpoint signs can be the same. The event disappears from the
list even though the numerical path passed through it.

We implemented a shared state-plus-tangent census that also locates zeros of
the normal velocity, which are stationary points of the plane residual.
It brackets crossings between those points and retains the ordinary event
list separately. Analytic controls exercise a hidden crossing pair within
one forced solver step, a no-crossing case and an exact tangency. The tangency
remains uncertain rather than being relabeled as a transverse crossing.

This principle is **not new to the repository or a new scientific method**.
`scripts/qualify_jones_period6_flip_extremum_count.py` already used
extremum-partitioned counts for the earlier periodic-orbit grazing study.
The EXP-486 variational-return path did not carry that safeguard forward.
This is a caller/integration gap. The new reusable module adds full
state-plus-tangent retention and narrow-crossing regression controls; the
older frozen implementation and evidence are unchanged.

## What the failure still means

For the first witness, the largest scaled-state discrepancy against the
finest Radau census is 3.26e-7, below the 1e-6 threshold. Its largest timing
discrepancy is 3.63e-11, below 1e-7. Every profile reproduces the earlier
Radau fifth crossing within both frozen tolerances.

For the second witness, the accepted event count agrees in all six profiles,
but the maximum scaled-state discrepancy reaches 2.26e-6. The two finer Radau
profiles also fail the 1e-6 state-match requirement against the old coarse
Radau witness. Thus even the finest profile does not pass the full protocol.
Its role as the comparison reference is not a license to declare it true.
Timing agreement and an agreed count do not erase this failure. No tolerance
was changed and neither experiment was retried.

Extrema themselves remain numerically detected, so the method is not a
rigorous all-root proof. No new fold, critical symbol, Jones word/arrow or
homoclinic claim is established. The one consistent EXP-486 fold region stays
its bounded positive result; the other regions stay unresolved.

## Evidence and checks

- [Prospective protocol](../experiments/EXP-487-section-census-witness.md).
- Freeze: `3059d522e8b14ab913ac79ae823ec3a23fd6276b`, pushed and verified
  against the live remote before execution.
- Raw run: `artifacts/EXP-487/target-3059d52`; 30.40 seconds on local CPU.
- Raw summary SHA-256:
  `1178079c0a84eb3f1daa60d295acb1ceefcf4e9eea361793ee87227d30ca3a5a`.
- [Public audited result](../experiments/receipts/EXP-487-section-census-result.json),
  SHA-256 `eb7f1c9765fe42a1c9fd06d9096e9cdfbf68084dde77969c48a866cd94005938`.
- The read-only audit reconstructs the two-witness/six-profile matrix,
  input lineage, section-event algebra, extremum sign brackets and all
  decisions; it checks raw binary trajectories and the full file inventory.
  This is a same-agent local audit, not an independent human review.
- Before execution: 1,896 tests passed, one existing Linux-only skip;
  all thirteen focused census tests and six actual analytic controls passed.

## Next scientific work

1. Separate convergence to a refined event state from agreement with the old
   coarse witness in a new, prospective accuracy study. Keep the old mismatch
   as a reported quantity, not a threshold to relax after the fact.
2. Test whether the problematic left interval approaches a section tangency
   and a change of first-return itinerary rather than a smooth projected fold.
   Use the time-dependent plane residual and its normal derivative directly;
   do not fit a smooth curve across the observed event discontinuity.
3. Qualify the extrema-aware census in the variational fold path, retaining
   all depth/direction families. Only then revisit the failed folds and the
   held-out partition/critical-membership test.
4. Audit other ordinary-event callers proportionately. The two witnesses do
   not automatically invalidate old runs, but dual-solver agreement on
   previously sampled points is not an all-event guarantee between them.
