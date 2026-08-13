# EXP-209 — Three-point period-12 normal-form and attraction audit

Status: passed all normal-form, stability, identity, and attraction gates

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

## Result

All three fixed-`c` slices pass all seven branch points. The phase-aligned
opening exponents are `0.502576`, `0.503031`, and `0.503504`, with respective
`R^2` values `0.9999975`, `0.9999967`, and `0.9999957`. All 21 flip multiplier
ratios lie in `4.01066--4.15024`; the three medians are
`4.03423--4.04734`.

The smallest sampled parent modulus is `1.02075`, the largest child modulus is
`0.91679`, and all 21 rows preserve exact 6/8 versus 12/16 section identity.
The minimum proper-subperiod return distance is `0.02935`. Nine Radau
checkpoints agree with DOP853 to maximum whole-orbit RMS `1.34e-8`, multiplier
modulus difference `1.94e-9`, and relative period difference `1.50e-13`.

Both perturbation signs return at every full-offset child. Maximum terminal
distance to the orbit is `6.57e-11`, and the largest phase-invariant RMS after
recorrection is `1.41e-8`. The result establishes replicated sampled local
supercritical signatures and attraction at three slices, within the stated
claim boundary.

Raw receipt: `artifacts/EXP-209/receipt.json`, 48,049 bytes, SHA-256
`f57becaf08aa0ddb7a05bd7e258448cc95f3aca7611ebcd4cf00265303ebbfd0`.
Compact receipt:
[`receipts/EXP-209.json`](receipts/EXP-209.json).
