# Independent symbolic verification: work log

## Starting point

The prominent chain diagram was transcribed and checked against Jones's
source. It was **not independently computed from new Rössler orbits**. The
user has now requested that verification explicitly. The historical diagram
and every connecting arrow remain attributed reproduction targets until new
dynamical evidence passes the necessary gates.

## Corrections made before target computation

- Clarified that the approximate-landmark test failed partition parity and
  word recovery, not a qualified symbolic-ordering test.
- Separated the local alphabet calibration at `c=20` from the landmark at
  `c=6.124`; no transport between them has been demonstrated.
- Removed the claim that the prior negative search excluded inadequate
  sampling at its tested points.
- Closed an encoder bug: a nonfinite permitted zero-slope residual could
  previously bypass the slope gate. Added regression controls; no historical
  result is silently changed or relabeled by the fix.

## New, separate verification tracks

[EXP-478](../experiments/EXP-478-quadratic-symbolic-control.md) independently
enumerates the quadratic map's finite critical-cycle words using exact
arithmetic, then compares them under a declared conditional dictionary.
This checks a limited combinatorial claim, not the flow realization.

[EXP-477](../experiments/EXP-477-symbolic-center-pilot.md) prepares a new
raw-retaining replay of the unfinished EXP-204 center scout. It uses no Jones
words and explicitly defers historical-section reconstruction, local
partition/alphabet qualification, critical membership and connecting paths.
GPU collection and local fitting are separate so the rented GPU can be
released before CPU spline/bootstrap analysis.

The read-only Runpod inspection found unrelated running workers. They are
outside this task's scope. No target execution or new paid worker has occurred
at this protocol-preparation checkpoint. Freeze commits, actual outcomes and
cost/teardown evidence will be appended rather than invented in advance.

## EXP-478 completed after public freeze

The enumerator and separate comparison were pushed at
[`f4b2ea1`](https://github.com/tdj28/butterfly/commit/f4b2ea13c60395713911240b0fbf0ce469850cc4)
before running from a clean detached checkout. Exact enumeration completed
for all prescribed periods. The conditional word-list and within-period order
comparisons both passed; the two third-branch nodes remain outside the scalar
model. The [complete experiment result](../experiments/EXP-478-quadratic-symbolic-control.md)
links the full certificates and comparison, and the manuscript now includes
a receipt-generated table. An independent reviewer checked the source
identity, completeness and mapping after execution.

This is positive evidence for the finite combinatorial structure, not a
claim that the Rössler chains have been independently reproduced. No paid
compute was used for this calculation.
