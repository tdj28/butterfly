# EXP-209 — Three-point period-12 normal-form and attraction audit

Status: prospectively frozen before child continuation

## Question

Do the three EXP-208 children open with the square-root and multiplier scaling
of a locally supercritical period doubling, and do nearby trajectories return
to the full-offset children?

## Frozen design

At each `c=7.18,7.24,7.30`, the event-to-child `a` interval is sampled at seven
fixed fractions from `0.1` through `1.0`. Period-6 parents and period-12
children are separately corrected at fixed parameters. The phase-aligned RMS
between each child and the double-covered parent defines the branch-opening
amplitude. Its log--log exponent must lie in `[0.4,0.6]` with `R^2 >= 0.995`.

The flip normal form also predicts
`(1-lambda_child)/(-lambda_parent-1) -> 4`; every sampled ratio must lie in
`[3,5]` and each target's median in `[3.5,4.5]`. Every row must preserve
parent/child stability exchange, period ratio two, both section identities,
and all proper-subperiod nonclosures. Radau independently checks fractions
`0.1`, `0.32`, and `1.0`. At the full offset, two opposite perturbations are
integrated for 16 child periods and must return within `1e-5` of the orbit,
then recorrect to the same phase-invariant child within RMS `1e-7`.

Manifest:
[`../../experiments/manifests/EXP-209-period12-normal-form.json`](../../experiments/manifests/EXP-209-period12-normal-form.json).

## Claim boundary

A three-of-three pass establishes sampled local supercritical-period-doubling
signatures and perturbed attraction on these fixed-`c` slices. It does not
estimate formal normal-form coefficients, measure basin size, repair EXP-207's
branch-arm failure, construct a continuous two-parameter child surface,
establish global supercriticality, identify the TBA curve, or establish double
superstability.
