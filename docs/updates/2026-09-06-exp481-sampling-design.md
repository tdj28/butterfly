# EXP-481: independent partition tests now have a concrete sampling design

We have moved from recording infrastructure to the statistical question:
can the historical return map be inferred independently of Jones's words?
There is now an explicit [numeric proposal](../experiments/EXP-481-sampling-and-analysis-proposal.md),
a [machine-readable design](../../experiments/manifests/EXP-481-paired-sampling-proposal.json),
and tested seed/pair selection and held-out map-analysis code.
**No new nominated Rössler trajectory or symbolic verification result exists
from this checkpoint.** The proposal is unreviewed and execution-disabled.

## What is implemented

- An exact, reproducible table of 8,192 new initial-condition coordinates,
  shared by both nominated cases/profiles, with global IDs and a fixed
  4,096/4,096 calibration/holdout split. A result-free batch table names all
  512 planned 64-seed case/profile batches. Neither table contains outcomes.
- Selection of four consecutive-return pairs per seed per physical-time window,
  on both sections. All required strata must be present; no filling gaps,
  duplicating rows, survivor renumbering or bridging unresolved events.
  Faster-returning trajectories receive no more selected weight.
- A held-out scalar-map audit that fits only calibration data, preserves
  calibration normalization on holdout, checks distinct-seed bin support and
  prediction error, and bootstraps whole seed blocks. It does not request a
  target branch count. An affine baseline is reported on the same held-out rows.

The proposal uses historical `x` as primary; historical `z` and Barrio `z`
cannot rescue a failing primary projection. Both nominated cases remain
mandatory. The same-cohort, two-window and two-step comparison is explicit,
as are the resource caps and still-unimplemented execution links.

## What the controls actually show

**25 new tests pass** across selection, analysis and result-free plan checks.
They include global-ID conservation, unequal event counts, missing strata,
ambiguous crossings, calibration/holdout leakage rejection, seed rather than
row resampling, unsupported gaps and degenerate coordinates. The complete local
suite passes **1,406 tests**, with one unrelated Linux-only process test skipped
on macOS.

The separate smoke uses the proposal's full five variants and 200 seed-block
bootstrap replicates, on 512 calibration and 512 held-out synthetic seeds with
four pairs each. All four declared controls behave as expected:

| Synthetic control | Result | Meaning |
|---|---|---|
| Affine monotone map | One branch, no critical points | The analyzer does not force Jones's three branches. |
| Cubic with extrema at 0.25 and 0.75 | Three branches; extrema recovered near both known locations | It can recover two genuine turning regions without being given their locations/count. |
| Monotone cubic with stationary inflection | One branch, no turning regions | Zero slope alone is not misidentified as a turning branch boundary. |
| Same calibration graph, two separated held-out sheets | Unresolved in all five variants | A clean fitted curve cannot conceal a badly multivalued held-out projection. |

For the cubic, the largest held-out normalized q90 spline error is below
`3.102e-5`, while the same-row affine baseline errors exceed `0.0912`.
For the multivalued holdout the spline and affine errors both exceed `0.25`.
Those are analytic-map software controls, not Rössler evidence or a calibrated
false-positive rate. The recovered extrema envelopes are descriptive, not
simultaneous confidence intervals.

- [Exact control configuration and source hashes](../experiments/receipts/EXP-481-synthetic-sampling-configuration.json)
- [Control results and raw/audit hashes](../experiments/receipts/EXP-481-synthetic-sampling.json)
- Full local seed/batch tables, synthetic raw arrays and audits:
  `artifacts/EXP-481/synthetic-sampling-05/`.

The earlier `synthetic-sampling-01/` through `-04/` also passed their nominal
control gates and are retained. In `-04/`, the stationary-inflection control's
bootstrap count consensus ranged from 0.935 to 0.975: not every resample agreed.
Inspection identified a geometry weakness: absolute prominence alone can admit
a false extremum when a sub-grid root pair is incompletely represented. The
final implementation also requires a maximum above both adjacent landmarks or
a minimum below both. This is a pre-outcome source correction, not a changed
acceptance threshold; the old target analyzers and prior evidence are untouched.
The final run binds source after adding declaration validation, degenerate-map
handling, the affine comparator and an explicit stationary-inflection guard/control; no numerical acceptance threshold was
changed to obtain a passing control. Regeneration uses the checked-in
`scripts/qualify_paired_sampling.py` with a fresh `--output-dir`.

## Next, without rebuilding completed pieces

An exact analytic reproducer also confirms that the legacy `_critical_points`
helper can label a stationary inflection as a branch boundary. The
[incident record](../experiments/EXP-481-legacy-turning-point-incident.md)
preserves the defect and separates the corrected new analyzer from the pending
historical-result impact audit. No prior Rössler claim is cleared or overturned
by this control alone; that audit is required before the next manuscript release.

Implement the audited journal-to-pairs join and cross-profile intersection,
joint window/profile stability and the complete cycle-point/critical-region
matrix. Then finish the early-transient adaptive adapter, bounded execution
supervisor and authentic source/input/review gates. Check reference capture
points against the already-retained EXP-480 raw events. Obtain and adjudicate
one compact design review only when that end-to-end path is ready, push its
exact executable freeze, then run it.

The research-integrity playbook influenced the design directly: equal trajectory
weights, disjoint held-out seeds, preservation of negative controls, explicit
support rather than invented power claims, and no source-word-driven branch
count. This work is a public engineering/design checkpoint, not a manuscript
result. No paid model or compute call was made. A read-only provider check again
found no exact task-name match for the unresolved earlier create transaction and
confirmed its watchdog alive; that remains insufficient to claim teardown.
