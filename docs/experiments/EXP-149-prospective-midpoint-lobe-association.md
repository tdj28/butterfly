# EXP-149 — Prospective midpoint branch/lobe association

Status: passed prospective two-branch/lobe-exclusion association

## Question

At the untouched midpoint, does the independently determined PIM branch class
agree with inclusion or exclusion of the already frozen UPO left lobe?

## Frozen decision rule

The relation—not the midpoint class—is predicted:

- a two-branch saddle must have zero post-burn-in PIM left-lobe states on every
  access line at both horizons;
- a three-branch saddle must have at least ten per line and horizon, with every
  such state within scaled `(y,z)` distance `5e-5` of the full EXP-147 lobe and
  `1e-4` of its nested coarse subset.

The lobe threshold remains `y < -31.135026064071056`; scales remain
`(30,0.0006)`; the PIM burn-in remains 100; and the midpoint atlas must retain
at least 500 fine and 250 coarse lobe points. All six access-line/horizon
decisions must pass. No unresolved, mixed, or threshold-relaxed result counts
as agreement.

## Execution boundary

The analysis implementation and unit tests are committed before EXP-148 is
started. Once EXP-148 completes, an immutable manifest may fill only the exact
paths and SHA-256 hashes of the already frozen EXP-147 lobe receipt and the new
EXP-148 receipt/state archive. No scientific value or decision rule may change.

## Interpretation boundary

A pass is the first prospective association between local saddle branch class
and UPO-lobe inclusion. It remains one midpoint, uses finite PIM point clouds,
and is not an exact manifold-intersection proof or a continued TBA curve.

## Result

EXP-149 passes. EXP-148 independently selects two branches. Every one of the
six access-line/horizon PIM clouds has zero post-burn-in states below the frozen
left-lobe boundary, while the EXP-147 atlas supplies 989 fine and 558 coarse
lobe points. The association class is `two_branch_and_lobe_excluded`.

Tracked receipt: `docs/experiments/receipts/EXP-149.json`.
