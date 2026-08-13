# EXP-210 — Dense fixed-offset period-12 surface patch

Status: prospectively frozen before surface continuation

## Question

Can the isolated and fixed-`c` EXP-208/209 child results be extended into a
regular two-parameter period-12 surface patch over the dense EXP-206 flip
curve?

## Frozen design

All 31 exact EXP-206 event slices from `c=7.18` through `7.30` are crossed at
physical post-flip offsets `5e-6`, `15e-6`, `30e-6`, and `45e-6` in `a`. Each
of the resulting 124 fixed-parameter parent/child pairs is corrected directly,
avoiding EXP-207's ill-conditioned free-`a` nullspace predictor.

Every point must close, retain an unstable period-6 parent and primitive stable
period-12 child, preserve period ratio two and exact 6/8 versus 12/16 section
identity, and keep the flip multiplier ratio in `[3,5]`. At each of the 31
`c` slices, the four physical offsets must fit a square-root opening exponent
in `[0.4,0.6]` with `R^2 >= 0.995`. Neighboring children along each fixed-offset
line must agree phase-invariantly within RMS `0.05`. DOP853/Radau parity is
required at the six near/far-offset corner, center, and endpoint controls.

Manifest:
[`../../experiments/manifests/EXP-210-period12-surface.json`](../../experiments/manifests/EXP-210-period12-surface.json).

## Claim boundary

A pass establishes a dense regular sampled period-12 surface patch with local
normal-form scaling. It is not a formal continuous-surface theorem, global
continuation or endpoint result, basin-size measurement, TBA curve, or
double-superstability result.
